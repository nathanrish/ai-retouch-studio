# AI Retouch Studio (v1.0)

Professional Photoshop panel with AI-powered retouching.

- **Backend:** FastAPI + Stable Diffusion (txt2img, img2img, inpaint) + SAM (precision masking) + LUTs
- **Frontend:** Photoshop UXP Panel (document export / smart object placement / SAM UI)
- **Infra:** Docker Compose (backend, Postgres, Redis), model downloader

<p align="left">
  <a href="https://github.com/nathanrish/ai-retouch-studio/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
  <img alt="Photoshop UXP" src="https://img.shields.io/badge/Photoshop-UXP-31A8FF?logo=adobephotoshop&logoColor=white">
</p>

## Features
- **AI Retouching (Stable Diffusion):** text-guided professional edits (img2img, inpaint)
- **Precision Masking (SAM):** point-based mask generation
- **LUT Color Grading:** quick grading via LUT service
- **Photoshop-native UX:** non-destructive Smart Object layers; automatic placement
- **Production-ready:** Dockerized, health checks, API docs, model management

## Quick Start

Prereqs: Docker Desktop, Python 3.10+, Photoshop (UXP Developer Mode)

```bash
# 1) Download models (SAM + warm SD)
cd backend
python scripts/download_models.py

# 2) Start stack
cd ../infrastructure
# If using Docker Compose v2 (recommended):
docker compose up --build
# If Docker Compose v1:
docker-compose up --build

# 3) Open docs and health
# http://localhost:8000/docs
# http://localhost:8000/api/v1/health
# http://localhost:8000/api/v1/retouch/capabilities
```

Photoshop panel:
1) Enable UXP Developer Mode
2) Load `frontend/` as a plugin
3) Open a document → enter prompt → Run Retouch; or use SAM controls to create a mask

## Getting the Code

- **Clone**
  ```bash
  git clone https://github.com/nathanrish/ai-retouch-studio.git
  cd ai-retouch-studio
  ```
- **Download ZIP**
  - Click "Code" → "Download ZIP" on the repository page → extract, then `cd` into the extracted folder.

## Run Locally (Docker)

- **Models**: Place `models/sam/sam_vit_b_01ec64.pth` or run downloader first:
  ```bash
  cd backend
  python scripts/download_models.py
  cd ..
  ```
- **Compose up**
  ```bash
  cd infrastructure
  docker compose up --build
  ```
- **Verify**
  - http://localhost:8000/api/v1/health
  - http://localhost:8000/docs

## Run Locally (without Docker)

Backend API:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (Photoshop UXP):
- Open Photoshop → Enable UXP Developer Mode → Load `frontend/` as a plugin.
- Open an image → use the panel to Run Retouch or Create Mask (SAM).

## Using on a VM (POC)

1) **Install Docker & Compose** on the VM (Ubuntu 22.04 recommended).
2) **Copy repo and models** to the VM, for example under `/opt/ai-retouch-studio`:
   ```bash
   mkdir -p /opt/ai-retouch-studio && cd /opt/ai-retouch-studio
   git clone https://github.com/nathanrish/ai-retouch-studio.git .
   mkdir -p models/sam
   # Copy sam_vit_b_01ec64.pth into models/sam/
   ```
3) **Start services**
   ```bash
   cd infrastructure
   docker compose up -d --build
   ```
4) **Open** `http://<VM-IP>:8000/docs`

GPU (optional): set `AI_DEVICE=cuda` and ensure NVIDIA runtime is installed.

## Photoshop Integration (UXP)

- **Load panel**: `frontend/manifest.json` → load folder in UXP Developer Mode.
- **Export & Place**: `frontend/src/photoshop-bridge.js` handles:
  - `readActiveDocumentAsPNG()` to export active document
  - `placeImageFromBytes(bytes, layerName)` to place AI results as a Smart Object layer
- **SAM UI**: `frontend/src/main.js` adds controls under `.ai-tools`:
  - Add points (foreground/background) → Create Mask → mask placed as new layer

## Testing the API

- **Swagger**: `http://localhost:8000/docs`
- **cURL (img2img)**
  ```bash
  curl -X POST http://localhost:8000/api/v1/retouch/process \
    -F "prompt=professional skin retouching, natural texture" \
    -F "operation=img2img" \
    -F "image=@test.png" 
  ```
- **cURL (SAM points)**
  ```bash
  curl -X POST http://localhost:8000/api/v1/segmentation/segment-from-points \
    -F "image=@test.png" \
    -F 'points=[[100,100],[150,150]]' \
    -F 'labels=[1,0]'
  ```

## Troubleshooting

- **Models missing**: Ensure `models/sam/sam_vit_b_01ec64.pth` exists or run `backend/scripts/download_models.py`.
- **Docker not found (Windows)**: Install Docker Desktop and verify `docker --version`.
- **Slow generation**: Reduce `steps`, use CPU-friendly settings, or run on a GPU with `AI_DEVICE=cuda`.
- **Photoshop bridge not working outside UXP**: The bridge is guarded to no-op when not running in Photoshop.
- **CORS**: For POC, CORS is open. In production, restrict origins in `backend/app/main.py`.

<!-- Demo GIF intentionally omitted until available. See docs/DEMO_GUIDE.md to add one. -->

## Repository Structure
```
ai-retouch-studio/
├─ backend/
│  ├─ app/
│  │  ├─ api/endpoints/
│  │  │  ├─ retouch.py          # Stable Diffusion routes (process, capabilities)
│  │  │  ├─ luts.py             # LUT endpoints
│  │  │  └─ segmentation.py     # SAM: segment-from-points
│  │  ├─ services/
│  │  │  ├─ ai_service.py       # SD orchestration (txt2img, img2img, inpaint)
│  │  │  ├─ diffusion_processor.py  # Diffusers pipelines
│  │  │  ├─ lut_service.py      # LUT demo service
│  │  │  └─ enhancement_service.py  # Stubs (GFPGAN/ESRGAN)
│  │  └─ core/config.py         # API prefix, SAM model path
│  ├─ app/main.py               # FastAPI app + routers + health
│  ├─ requirements.txt          # Backend deps (diffusers, accelerate, SAM, etc.)
│  ├─ Dockerfile                # Python slim, git-lfs, libs
│  └─ scripts/download_models.py# Model downloader (SAM + SD warmup)
│
├─ frontend/
│  ├─ manifest.json             # UXP plugin manifest
│  ├─ index.html                # Panel UI shell (+ .ai-tools)
│  ├─ css/main.css              # Base + SAM styles
│  └─ src/
│     ├─ main.js                # Retouch + SAM UI logic
│     └─ photoshop-bridge.js    # Export/Place with layer naming
│
├─ infrastructure/
│  ├─ docker-compose.yml        # mounts ../models → /app/models, sets SAM_MODEL_PATH
│  ├─ start-dev.sh
│  └─ init-db.sql
│
├─ models/                      # SAM checkpoint folder (mounted)
├─ docs/                        # Project docs
└─ quality/                     # Tests scaffold
```

## API Overview
- `GET /api/v1/health` → service health
- `GET /api/v1/retouch/capabilities` → model/device & features
- `POST /api/v1/retouch/process` (multipart)
  - form fields: `prompt`, `operation` (txt2img|img2img|inpaint), `image`, `mask` (optional), `strength`, `guidance_scale`, `steps`, `seed`, `enhance_faces`, `upscale`, `upscale_scale`
  - returns: `{ image_base64, meta }`
- `POST /api/v1/segmentation/segment-from-points` (multipart)
  - fields: `image`, `points` ([[x,y],...]), `labels` ([1/0,...])
  - returns: `{ mask (base64 PNG), score }`
- `POST /api/v1/luts/apply` (multipart) → returns image stream (PNG)
- `GET /api/v1/luts/list`

## Models
- **SAM checkpoint:** `models/sam/sam_vit_b_01ec64.pth`
  - Auto-downloaded by `backend/scripts/download_models.py`
- **Stable Diffusion pipelines:** downloaded on first use via Hugging Face (or warmed by downloader)

## GPU & Performance
- Set `AI_DEVICE=cuda` to enable GPU (if available)
- Compose includes GPU reservation stanza; adjust for your runtime
- For large images, consider reducing steps or using optimized models

## Development
```bash
# Install backend deps (optional local dev)
cd backend && pip install -r requirements.txt

# Run API locally (without Docker)
uvicorn app.main:app --reload

# Frontend: load ./frontend as UXP plugin in Photoshop
```

## Contributing
- Issues and PRs welcome. Please include repro steps and environment info.
- For major features (e.g., GFPGAN/ESRGAN), open an RFC issue first.

### Development tips
- Prefer small PRs with clear scope and screenshots where applicable.
- Include performance notes for model changes (VRAM, steps, latency).
- For UXP panel tweaks, attach a GIF of the interaction.

## License
Apache-2.0. See the [`LICENSE`](LICENSE) file for details.

## Roadmap (v1.1)
- Enhancement pipeline: GFPGAN, Real-ESRGAN
- SAM box-based segmentation
- Photoshop click capture for SAM
- Batch processing, presets
