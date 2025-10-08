#!/usr/bin/env python3
import os
import urllib.request
import logging
from pathlib import Path

from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SD_BASE = os.getenv("SD_BASE_MODEL", "runwayml/stable-diffusion-v1-5")
SD_IMG2IMG = os.getenv("SD_IMG2IMG_MODEL", SD_BASE)
SD_INPAINT = os.getenv("SD_INPAINT_MODEL", "runwayml/stable-diffusion-inpainting")


def download_sam_model() -> bool:
    """Download Segment Anything checkpoint into ../models/sam."""
    model_url = (
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    )
    models_dir = Path("../models").resolve()
    sam_dir = models_dir / "sam"
    sam_path = sam_dir / "sam_vit_b_01ec64.pth"
    sam_dir.mkdir(parents=True, exist_ok=True)
    if not sam_path.exists():
        logger.info("📥 Downloading SAM model to %s", sam_path)
        try:
            urllib.request.urlretrieve(model_url, sam_path)
            logger.info("✅ SAM model downloaded successfully")
        except Exception as e:
            logger.error("❌ Failed to download SAM model: %s", e)
            return False
    else:
        logger.info("✅ SAM model already exists at %s", sam_path)
    return True


def download_stable_diffusion_models() -> bool:
    """Optionally warm up Stable Diffusion pipelines (will lazy-download otherwise)."""
    try:
        logger.info("📥 (Optional) Warming Stable Diffusion pipelines...")
        StableDiffusionPipeline.from_pretrained(SD_BASE)
        StableDiffusionImg2ImgPipeline.from_pretrained(SD_IMG2IMG)
        StableDiffusionInpaintPipeline.from_pretrained(SD_INPAINT)
        logger.info("✅ SD pipelines ready")
        return True
    except Exception as e:
        logger.warning("⚠️ SD warmup skipped or failed: %s", e)
        return False


def main():
    print("🚀 Downloading AI models for Retouch Studio...")
    download_sam_model()
    download_stable_diffusion_models()
    print("🎉 Model download complete!")


if __name__ == "__main__":
    main()
