from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import io

from ...services.lut_service import LUTService

router = APIRouter(prefix="/luts", tags=["luts"])
service = LUTService()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "luts"}


@router.post("/apply")
async def apply_lut(
    image: UploadFile = File(...),
    lut_name: str = Form(...),
    intensity: float = Form(1.0)
):
    data = await image.read()
    out_image = await service.apply_lut_bytes(data, lut_name, intensity)
    buf = io.BytesIO()
    out_image.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/list")
async def list_luts():
    return JSONResponse({"luts": service.list_luts()})
