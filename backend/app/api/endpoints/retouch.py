import base64
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from ...services.ai_service import get_ai_service

router = APIRouter(prefix="/retouch", tags=["retouch"])


@router.get("/capabilities")
async def capabilities():
    ai = get_ai_service()
    health = await ai.health()
    return JSONResponse({
        "models_loaded": health.get("loaded", False),
        "device": health.get("device", "cpu"),
        "capabilities": health.get("capabilities", [
            "txt2img", "img2img", "inpaint", "enhance_faces", "upscale"
        ])
    })


@router.post("/process")
async def process_image(
    prompt: str = Form(...),
    operation: str = Form("img2img"),
    image: Optional[UploadFile] = File(None),
    mask: Optional[UploadFile] = File(None),
    strength: float = Form(0.7),
    guidance_scale: float = Form(7.5),
    steps: int = Form(30),
    seed: Optional[int] = Form(None),
    enhance_faces: bool = Form(False),
    upscale: bool = Form(False),
    upscale_scale: int = Form(2),
):
    ai = get_ai_service()
    init_bytes = await image.read() if image is not None else None
    mask_bytes = await mask.read() if mask is not None else None

    try:
        result = await ai.process_image(
            init_bytes,
            prompt,
            operation=operation,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=steps,
            seed=seed,
            mask_bytes=mask_bytes,
            enhance_faces=enhance_faces,
            upscale=upscale,
            upscale_scale=upscale_scale,
        )
        img_b64 = base64.b64encode(result["image_png"]).decode("utf-8")
        return JSONResponse({
            "image_base64": img_b64,
            "meta": result.get("meta", {}),
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
