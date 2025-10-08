# AI Retouch Studio

Professional Photoshop Panel with AI Retouching.

## Components
- Backend: FastAPI, Qwen-Image integration, LUTs, SAM (pending)
- Frontend: UXP panel (Photoshop), bridge to backend
- Infra: docker-compose for backend+db+redis

## Dev Quickstart
1. docker compose -f infrastructure/docker-compose.yml up --build
2. Open Photoshop and load `frontend/` as a UXP plugin (Developer Mode)
3. Use the panel to send retouch requests

## Environment
- QWEN_IMAGE_MODEL: override default model
- AI_DEVICE: set to 'cuda' or 'cpu' to force device
