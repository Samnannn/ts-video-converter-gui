# TS Video Converter GUI

A tiny Windows app for turning annoying `.ts` video downloads into clean `.mp4` files.

When you download videos using some video downloaders, the final file often comes out with a `.ts` extension instead of a normal `.mp4`. These files can lag in VLC, behave badly in popular media players, and feel even worse when you move them to a phone. Converting them with VLC or large paid converter tools can be slow, confusing, and honestly too much work for such a simple job.

So this app does one thing:

**Select `.ts` videos, choose an output folder, click Convert, and get `.mp4` files quickly.**

It uses fast stream copy conversion, so it usually finishes much faster than traditional re-encoding tools because it does not rebuild the whole video from scratch.

## Why I Made This

I kept downloading videos and getting `.ts` files. They played badly, lagged on phones, and converting them one by one from the command line meant copying file paths, changing output names, and repeating the same boring steps again and again.

This app removes that headache.

No terminal.
No manual file paths.
No paid converter.
No Python setup for normal users.
No separate ffmpeg install.

## Features

- Convert `.ts` videos to `.mp4`
- Select multiple files at once
- Choose any output folder
- Random unique output names, so files do not overwrite each other
- Fast conversion using ffmpeg stream copy
- Lightweight Windows GUI
- Packaged release includes ffmpeg
- Normal users do not need Python

## Download

Go to the **Releases** page and download the latest Windows zip:

```text
TSVideoConverterGUI-Windows.zip
```

Extract it, then run:

```text
TSVideoConverterGUI.exe
```

That is it. The app is ready to use.

## How To Use

1. Open `TSVideoConverterGUI.exe`
2. Click `Add Files`
3. Select one or more `.ts` videos
4. Choose the output folder
5. Click `Convert`

Your converted videos will be saved as `.mp4` files with names like:

```text
video_a8f31c92bd.mp4
```

## What Makes It Fast

Many converters re-encode the entire video, which can take a long time and may reduce quality.

This app uses:

```text
ffmpeg -c copy
```

That means it copies the existing video and audio streams into an `.mp4` container without re-encoding whenever possible. For many `.ts` files, that makes conversion very fast and keeps the original quality.

## For Developers

Run from source:

```powershell
python app.py
```

When running from source, you need Python and ffmpeg installed on your machine.

## Build The Windows App

1. Put `ffmpeg.exe` here:

```text
vendor/ffmpeg.exe
```

2. Install build tools:

```powershell
python -m pip install -r requirements-dev.txt
```

3. Build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1
```

The final app will be created here:

```text
dist/TSVideoConverterGUI.exe
```

## License Note

This project can bundle ffmpeg for convenience. ffmpeg has its own license terms, so include ffmpeg license information when publishing release builds.
