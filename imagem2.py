from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO


IMAGE_PATH = "templates/preco_p.png"
OUTPUT_PATH = "teste_saida.png"


class ImageTextEditor:
    def __init__(self, image_path: str):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        self.image = Image.open(image_path).convert("RGBA")
        self.draw = ImageDraw.Draw(self.image)

    def load_font(self, font_size: int = 80):
        font_candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception:
                    pass

        return ImageFont.load_default()

    def add_centered_text(self, text, x_min, x_max, y, font_size=60, fill="white"):
        text = str(text)
        font = self.load_font(font_size)

        bbox = self.draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        x_position = x_min + (x_max - x_min - text_width) // 2
        self.draw.text((x_position, y), text, fill=fill, font=font)

    def process_image(self, preco_1, preco_2):
        # esquerda
        self.add_centered_text(preco_1, x_min=330, x_max=640, y=370, font_size=42)

        # direita
        self.add_centered_text(preco_2, x_min=710, x_max=1020, y=370, font_size=42)

        self.image.save(OUTPUT_PATH)
        print(f"Imagem salva em: {OUTPUT_PATH}")


if __name__ == "__main__":
    editor = ImageTextEditor(IMAGE_PATH)
    editor.process_image("R$ 39,90", "R$ 59,90")