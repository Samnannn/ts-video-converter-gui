import os
import queue
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from tkinter import END, BOTH, DISABLED, NORMAL, filedialog, messagebox, ttk
import tkinter as tk


APP_NAME = "TS Video Converter GUI"


def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


def ffmpeg_path() -> str:
    bundled = resource_path("ffmpeg.exe")
    if bundled.exists():
        return str(bundled)
    return "ffmpeg"


def random_output_path(output_folder: Path) -> Path:
    while True:
        output = output_folder / f"video_{uuid.uuid4().hex[:10]}.mp4"
        if not output.exists():
            return output


class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("780x520")
        self.minsize(720, 460)

        self.files: list[str] = []
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker: threading.Thread | None = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()
        self.after(120, self._poll_events)

    def _build_ui(self):
        pad = {"padx": 16, "pady": 8}

        title = ttk.Label(self, text="Selected .ts files", font=("Segoe UI", 11, "bold"))
        title.grid(row=0, column=0, sticky="w", **pad)

        self.file_list = tk.Listbox(self, selectmode=tk.EXTENDED, activestyle="dotbox")
        self.file_list.grid(row=1, column=0, sticky="nsew", padx=16)

        file_buttons = ttk.Frame(self)
        file_buttons.grid(row=2, column=0, sticky="w", **pad)

        ttk.Button(file_buttons, text="Add Files", command=self.add_files).pack(side="left", padx=(0, 8))
        ttk.Button(file_buttons, text="Remove", command=self.remove_selected).pack(side="left", padx=(0, 8))
        ttk.Button(file_buttons, text="Clear", command=self.clear_files).pack(side="left")

        output_frame = ttk.LabelFrame(self, text="Output folder")
        output_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=8)
        output_frame.columnconfigure(0, weight=1)

        self.output_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Video"))
        ttk.Entry(output_frame, textvariable=self.output_var).grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ttk.Button(output_frame, text="Browse", command=self.choose_output_folder).grid(row=0, column=1, padx=(0, 10), pady=10)

        action_frame = ttk.Frame(self)
        action_frame.grid(row=4, column=0, sticky="ew", **pad)
        action_frame.columnconfigure(1, weight=1)

        self.convert_button = ttk.Button(action_frame, text="Convert", command=self.convert)
        self.convert_button.grid(row=0, column=0, padx=(0, 12))

        self.progress = ttk.Progressbar(action_frame, mode="determinate")
        self.progress.grid(row=0, column=1, sticky="ew")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var).grid(row=5, column=0, sticky="ew", padx=16, pady=(4, 12))

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select TS videos",
            filetypes=[("TS video files", "*.ts"), ("All files", "*.*")],
        )
        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.file_list.insert(END, path)
        self.status_var.set(f"{len(self.files)} file(s) selected")

    def remove_selected(self):
        for index in reversed(self.file_list.curselection()):
            del self.files[index]
            self.file_list.delete(index)
        self.status_var.set(f"{len(self.files)} file(s) selected")

    def clear_files(self):
        self.files.clear()
        self.file_list.delete(0, END)
        self.progress["value"] = 0
        self.status_var.set("Ready")

    def choose_output_folder(self):
        folder = filedialog.askdirectory(title="Choose output folder", initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def convert(self):
        if self.worker and self.worker.is_alive():
            return

        if not self.files:
            messagebox.showinfo(APP_NAME, "Please select at least one .ts file.")
            return

        output_folder = Path(self.output_var.get()).expanduser()
        if not output_folder.is_dir():
            messagebox.showerror(APP_NAME, "Please choose a valid output folder.")
            return

        self.convert_button.configure(state=DISABLED)
        self.progress["maximum"] = len(self.files)
        self.progress["value"] = 0
        self.status_var.set("Starting conversion...")

        selected_files = list(self.files)
        self.worker = threading.Thread(
            target=self._convert_worker,
            args=(selected_files, output_folder),
            daemon=True,
        )
        self.worker.start()

    def _convert_worker(self, files: list[str], output_folder: Path):
        ffmpeg = ffmpeg_path()
        failures: list[str] = []

        for index, input_file in enumerate(files, start=1):
            output_file = random_output_path(output_folder)
            self.events.put(("status", f"Converting {index} of {len(files)}: {Path(input_file).name}"))

            command = [
                ffmpeg,
                "-hide_banner",
                "-y",
                "-i",
                input_file,
                "-c",
                "copy",
                "-map",
                "0",
                str(output_file),
            ]

            try:
                result = subprocess.run(command, capture_output=True, text=True, creationflags=_creation_flags())
                if result.returncode != 0:
                    failures.append(f"{Path(input_file).name}\n{result.stderr.strip()}")
            except FileNotFoundError:
                self.events.put(("missing_ffmpeg", None))
                return
            except Exception as exc:
                failures.append(f"{Path(input_file).name}\n{exc}")

            self.events.put(("progress", index))

        self.events.put(("done", failures))

    def _poll_events(self):
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "status":
                    self.status_var.set(str(payload))
                elif event == "progress":
                    self.progress["value"] = int(payload)
                elif event == "missing_ffmpeg":
                    self.convert_button.configure(state=NORMAL)
                    messagebox.showerror(APP_NAME, "ffmpeg.exe was not found. Use the bundled release build or install ffmpeg.")
                    self.status_var.set("ffmpeg missing")
                elif event == "done":
                    self.convert_button.configure(state=NORMAL)
                    failures = payload or []
                    if failures:
                        messagebox.showwarning(APP_NAME, "Finished with some failed files. Check the status text for details.")
                        self.status_var.set(f"Finished with {len(failures)} failed file(s).")
                    else:
                        messagebox.showinfo(APP_NAME, "Conversion finished.")
                        self.status_var.set(f"Finished. Saved MP4 files to: {self.output_var.get()}")
        except queue.Empty:
            pass

        self.after(120, self._poll_events)


def _creation_flags() -> int:
    if os.name == "nt":
        return subprocess.CREATE_NO_WINDOW
    return 0


if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
