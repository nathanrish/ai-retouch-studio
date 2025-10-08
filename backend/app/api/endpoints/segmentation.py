import io
import os
import json
import base64
from typing import Optional

import numpy as np
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from ...core.config import settings

router = APIRouter(prefix="/segmentation", tags=["segmentation"])

_sam_predictor = None


def _get_sam_checkpoint() -> str:
    # Default to container path
    return os.getenv("SAM_MODEL_PATH", getattr(settings, "SAM_MODEL_PATH", "/app/models/sam/sam_vit_b_01ec64.pth"))


def _ensure_sam_loaded():
    global _sam_predictor
    if _sam_predictor is not None:
        return
    try:
        from segment_anything import sam_model_registry, SamPredictor  # type: ignore
        import torch  # noqa: F401

        model_type = os.getenv("SAM_MODEL_TYPE", "vit_b")
        ckpt = _get_sam_checkpoint()
        if not os.path.exists(ckpt):
            raise RuntimeError(f"SAM checkpoint not found at {ckpt}")

        sam = sam_model_registry[model_type](checkpoint=ckpt)
        # Move to device if CUDA available
        try:
            import torch
            if torch.cuda.is_available():
                sam.to("cuda")
        except Exception:
            pass

        _sam_predictor = SamPredictor(sam)
    except Exception as e:
        raise RuntimeError(f"Failed to load SAM: {e}")


@router.post("/segment-from-points")
async def segment_from_points(
    image: UploadFile = File(...),
    points: str = Form("[]"),  # JSON: [[x,y], ...]
    labels: str = Form("[]"),  # JSON: [1,0,...]
    multimask_output: bool = Form(True),
):
    """Segment using point prompts via SAM. Returns base64 PNG mask and score."""
    try:
        _ensure_sam_loaded()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        data = await image.read()
        pil = Image.open(io.BytesIO(data)).convert("RGB")
        np_img = np.array(pil)

        pts = json.loads(points or "[]")
        lbs = json.loads(labels or "[]")
        if len(pts) == 0:
            raise HTTPException(status_code=400, detail="No points provided")

        import numpy as np  # local import to ensure availability
        input_points = np.array(pts)
        input_labels = np.array(lbs if len(lbs) == len(pts) else [1] * len(pts))

        _sam_predictor.set_image(np_img)
        masks, scores, logits = _sam_predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=bool(multimask_output),
        )

        best_idx = int(np.argmax(scores))
        best_mask = masks[best_idx]
        score = float(scores[best_idx])

        mask_pil = Image.fromarray((best_mask * 255).astype(np.uint8))
        buf = io.BytesIO()
        mask_pil.save(buf, format="PNG")
        buf.seek(0)
        mask_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return {"mask": mask_b64, "score": score}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAM segmentation failed: {e}")


@router.post("/segment-from-box")
async def segment_from_box(
    image: UploadFile = File(...),
    box: str = Form("[]"),  # JSON: [x1, y1, x2, y2]
):
    # TODO: Implement box-based SAM segmentation
    _ = await image.read()
    return {"note": "box-based segmentation not implemented yet", "box": box}
