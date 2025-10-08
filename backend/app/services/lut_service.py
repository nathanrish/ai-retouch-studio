from typing import List
from PIL import Image, ImageEnhance
import io

class LUTService:
    """Example LUT service with simple operations as placeholders.
    Replace with real .cube LUT loading and 3D interpolation as needed.
    """

    def __init__(self) -> None:
        self._luts = {
            "cinematic": 1.1,
            "vibrant": 1.2,
            "matte": 0.9,
        }

    def list_luts(self) -> List[str]:
        return list(self._luts.keys())

    async def apply_lut_bytes(self, image_bytes: bytes, lut_name: str, intensity: float = 1.0) -> Image.Image:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        factor = self._luts.get(lut_name, 1.0) * max(0.0, float(intensity))
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(factor)
        return img
