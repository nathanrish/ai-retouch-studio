# Demo Capture Guide

This guide shows how to record a short screen capture and produce a lightweight GIF for the README.

## 1) Record a short MP4/WebM

- Windows: Xbox Game Bar (Win+G) or OBS Studio.
- macOS: QuickTime Player (File → New Screen Recording) or OBS.
- Linux: OBS or GNOME Screen Recorder.

Recommended:
- Duration: 10–20 seconds
- Resolution: 1280×720 (or panel area cropped)
- FPS: 30

Show the workflow:
1. Open Photoshop, load the AI Retouch Studio panel (frontend/).
2. Run an AI retouch (img2img) and show the new Smart Object layer.
3. Create a SAM mask (add points → Create Mask) and show the mask layer.

Save the recording as `docs/demo.mp4`.

## 2) Convert MP4 → GIF with ffmpeg

High‑quality palette method (best trade‑off):

```bash
# macOS/Linux
ffmpeg -y -i docs/demo.mp4 -vf "fps=12,scale=960:-1:flags=lanczos,palettegen" docs/palette.png
ffmpeg -y -i docs/demo.mp4 -i docs/palette.png -filter_complex "fps=12,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse" docs/demo.gif
```

```powershell
# Windows PowerShell
ffmpeg -y -i docs/demo.mp4 -vf "fps=12,scale=960:-1:flags=lanczos,palettegen" docs/palette.png
ffmpeg -y -i docs/demo.mp4 -i docs/palette.png -filter_complex "fps=12,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse" docs/demo.gif
```

Notes:
- fps=12 keeps size small; adjust (8–15) as needed.
- scale=960 width; adjust to your capture.
- `docs/demo.gif` will auto‑render in the README.

## 3) Optimize (optional)

You can further optimize the GIF with gifsicle:

```bash
gifsicle -O3 --lossy=40 docs/demo.gif -o docs/demo.gif
```

## 4) Commit & push

```bash
git add docs/demo.gif
git commit -m "docs: add demo.gif"
git push origin main
```

If you prefer, attach a short MP4 in the repo (or as a GitHub release asset) and link it in the README.
