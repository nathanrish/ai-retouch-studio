import os
import io
import asyncio
from typing import Optional, Dict, Any, List

from PIL import Image

from .diffusion_processor import DiffusionProcessor, DiffusionConfig
from .enhancement_service import EnhancementService


class AIService:
    """
    Stable Diffusion based AI service.

    - Lazy loads diffusers pipelines (txt2img, img2img, inpaint).
    - Async-safe with an internal lock for first-load.
    - Device-aware (CUDA/MPS/CPU) via DiffusionProcessor.
    - Provides orchestration and capabilities reporting.
    """

    def __init__(
        self,
        device_override: Optional[str] = None,
    ) -> None:
        self._device_override = device_override or os.getenv("AI_DEVICE")
        self._diffusion: Optional[DiffusionProcessor] = None
        self._enhance: Optional[EnhancementService] = None
        self._lock = asyncio.Lock()
        self._loaded = False

    # -----------------------------
    # Public API
    # -----------------------------
    def capabilities(self) -> List[str]:
        return [
            "txt2img",
            "img2img",
            "inpaint",
            "enhance_faces",
            "upscale",
        ]

    async def health(self) -> Dict[str, Any]:
        await self._ensure_loaded()
        return {
            "loaded": self._loaded,
            "device": self._diffusion.device if self._diffusion else "cpu",
            "capabilities": self.capabilities(),
        }

    async def warmup(self) -> None:
        """Ensure model is loaded (e.g., call at app startup or readiness probe)."""
        await self._ensure_loaded()

    async def process_image(
        self,
        image_bytes: Optional[bytes],
        prompt: str,
        *,
        operation: str = "img2img",  # txt2img | img2img | inpaint
        strength: float = 0.7,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 30,
        seed: Optional[int] = None,
        mask_bytes: Optional[bytes] = None,
        enhance_faces: bool = False,
        upscale: bool = False,
        upscale_scale: int = 2,
    ) -> Dict[str, Any]:
        """
        Run a Stable Diffusion operation. Optionally apply enhancement/upscaling.
        Returns PNG bytes and metadata.
        """
        await self._ensure_loaded()
        init_img: Optional[Image.Image] = None
        mask_img: Optional[Image.Image] = None

        if image_bytes is not None:
            init_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if mask_bytes is not None:
            mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L")

        # Run generation in worker thread
        result_img = await asyncio.to_thread(
            self._run_generation,
            operation,
            prompt,
            init_img,
            mask_img,
            strength,
            guidance_scale,
            num_inference_steps,
            seed,
        )

        # Optional enhancement
        if enhance_faces or upscale:
            result_img = await asyncio.to_thread(
                self._enhance_image,
                result_img,
                enhance_faces,
                upscale,
                upscale_scale,
            )

        # Encode PNG
        out_buf = io.BytesIO()
        result_img.save(out_buf, format="PNG")
        out_buf.seek(0)

        return {
            "image_png": out_buf.getvalue(),
            "meta": {
                "operation": operation,
                "strength": strength,
                "guidance_scale": guidance_scale,
                "steps": num_inference_steps,
                "seed": seed,
            },
        }

    # -----------------------------
    # Internal
    # -----------------------------
    async def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        async with self._lock:
            if self._loaded:
                return
            await asyncio.to_thread(self._load_services)
            self._loaded = True

    def _load_services(self) -> None:
        cfg = DiffusionConfig(
            base_model=os.getenv("SD_BASE_MODEL", "runwayml/stable-diffusion-v1-5"),
            img2img_model=os.getenv("SD_IMG2IMG_MODEL", "runwayml/stable-diffusion-v1-5"),
            inpaint_model=os.getenv("SD_INPAINT_MODEL", "runwayml/stable-diffusion-inpainting"),
            device_override=self._device_override,
        )
        self._diffusion = DiffusionProcessor(cfg)
        self._enhance = EnhancementService()

    def _run_generation(
        self,
        operation: str,
        prompt: str,
        init_img: Optional[Image.Image],
        mask_img: Optional[Image.Image],
        strength: float,
        guidance_scale: float,
        steps: int,
        seed: Optional[int],
    ) -> Image.Image:
        assert self._diffusion is not None
        if operation == "txt2img":
            return self._diffusion.generate_txt2img(prompt, guidance_scale, steps, seed)
        if operation == "inpaint":
            if init_img is None or mask_img is None:
                raise ValueError("inpaint requires init image and mask")
            return self._diffusion.inpaint(prompt, init_img, mask_img, guidance_scale, steps, seed)
        # default img2img
        if init_img is None:
            raise ValueError("img2img requires init image")
        return self._diffusion.img2img(prompt, init_img, strength, guidance_scale, steps, seed)

    def _enhance_image(
        self,
        image: Image.Image,
        enhance_faces: bool,
        upscale: bool,
        scale: int,
    ) -> Image.Image:
        assert self._enhance is not None
        out = image
        if enhance_faces:
            out = self._enhance.enhance_faces(out)
        if upscale:
            out = self._enhance.upscale(out, scale=scale)
        return out


# Singleton-style accessor if needed by FastAPI dependency injection
_ai_service_singleton: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service_singleton
    if _ai_service_singleton is None:
        _ai_service_singleton = AIService()
    return _ai_service_singleton
