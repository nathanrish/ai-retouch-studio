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

## Demo

Add a short screen capture/GIF to showcase the workflow. Place it at `docs/demo.gif` and it will render below:

![AI Retouch Studio Demo](docs/demo.gif)

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
Apache-2.0 (proposed). If you prefer a different license, update this section and add `LICENSE`.

## Roadmap (v1.1)
- Enhancement pipeline: GFPGAN, Real-ESRGAN
- SAM box-based segmentation
- Photoshop click capture for SAM
- Batch processing, presets
