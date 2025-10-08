import os
from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass
class DiffusionConfig:
    base_model: str
    img2img_model: str
    inpaint_model: str
    device_override: Optional[str] = None


class DiffusionProcessor:
    def __init__(self, cfg: DiffusionConfig) -> None:
        self.cfg = cfg
        self.device = self._get_device()
        self._txt2img = None
        self._img2img = None
        self._inpaint = None

    # -----------------------------
    # Pipelines
    # -----------------------------
    def _ensure_txt2img(self):
        if self._txt2img is not None:
            return
        from diffusers import StableDiffusionPipeline
        import torch
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._txt2img = StableDiffusionPipeline.from_pretrained(
            self.cfg.base_model,
            torch_dtype=dtype,
            safety_checker=None,
        )
        self._move(self._txt2img)

    def _ensure_img2img(self):
        if self._img2img is not None:
            return
        from diffusers import StableDiffusionImg2ImgPipeline
        import torch
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._img2img = StableDiffusionImg2ImgPipeline.from_pretrained(
            self.cfg.img2img_model,
            torch_dtype=dtype,
            safety_checker=None,
        )
        self._move(self._img2img)

    def _ensure_inpaint(self):
        if self._inpaint is not None:
            return
        from diffusers import StableDiffusionInpaintPipeline
        import torch
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._inpaint = StableDiffusionInpaintPipeline.from_pretrained(
            self.cfg.inpaint_model,
            torch_dtype=dtype,
            safety_checker=None,
        )
        self._move(self._inpaint)

    def _move(self, pipe):
        if self.device == "cuda":
            pipe = pipe.to("cuda")
        elif self.device == "mps":
            pipe = pipe.to("mps")
        else:
            pipe = pipe.to("cpu")
        # disable NSFW checker as we don't use it in professional retouch context
        if hasattr(pipe, "safety_checker"):
            pipe.safety_checker = None

    # -----------------------------
    # Operations
    # -----------------------------
    def generate_txt2img(self, prompt: str, guidance_scale: float, steps: int, seed: Optional[int]) -> Image.Image:
        self._ensure_txt2img()
        import torch
        g = torch.Generator(device=self.device)
        if seed is not None:
            g = g.manual_seed(int(seed))
        result = self._txt2img(
            prompt=prompt,
            guidance_scale=float(guidance_scale),
            num_inference_steps=int(steps),
            generator=g,
        )
        return result.images[0]

    def img2img(self, prompt: str, init_image: Image.Image, strength: float, guidance_scale: float, steps: int, seed: Optional[int]) -> Image.Image:
        self._ensure_img2img()
        import torch
        g = torch.Generator(device=self.device)
        if seed is not None:
            g = g.manual_seed(int(seed))
        result = self._img2img(
            prompt=prompt,
            image=init_image,
            strength=float(strength),
            guidance_scale=float(guidance_scale),
            num_inference_steps=int(steps),
            generator=g,
        )
        return result.images[0]

    def inpaint(self, prompt: str, init_image: Image.Image, mask_image: Image.Image, guidance_scale: float, steps: int, seed: Optional[int]) -> Image.Image:
        self._ensure_inpaint()
        import torch
        g = torch.Generator(device=self.device)
        if seed is not None:
            g = g.manual_seed(int(seed))
        result = self._inpaint(
            prompt=prompt,
            image=init_image,
            mask_image=mask_image,
            guidance_scale=float(guidance_scale),
            num_inference_steps=int(steps),
            generator=g,
        )
        return result.images[0]

    # -----------------------------
    # Device selection
    # -----------------------------
    def _get_device(self) -> str:
        if self.cfg.device_override:
            return self.cfg.device_override
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
        return "cpu"
