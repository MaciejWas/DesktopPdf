import os
from PIL import Image
from PIL import ImageEnhance
from datetime import datetime
import random

from DesktopPdf.configuration import get_local_ip

def get_random_digits(n=6):
    if n <= 0:
        return ""

    password_number = random.randint(0, int("9" * n))
    password = str(password_number)
    password = "0" * (n-len(password)) + password
    return password


class PassManager:
    def __init__(self):
        self._current_password = get_random_digits(n=6)
        self.local_ip = get_local_ip()
        self._ips_with_access = [self.local_ip]

    def get_password(self) -> str:
        return self._current_password

    def set_password(self, new_password: str) -> None:
        self._ips_with_access = [self.local_ip]
        self._current_password = new_password

    def validate_password(self, password: str) -> bool:
        return password == self._current_password

    def register_ip(self, ip: str) -> None:
        self._ips_with_access.append(ip)

    def validate_ip(self, ip: str) -> bool:
        if ip in self._ips_with_access:
            return True
        else:
            return False

class FileManager:
    def __init__(self):
        self.save_folder = "pdfs"
        self._default_name = "PDF_%H:%M:%S_%d-%m-%Y.pdf"

        if self.save_folder not in os.listdir():
            os.mkdir(self.save_folder)

    @staticmethod
    def rotate_image(self, img: Image.Image) -> Image.Image:
        return pil_image.rotate(90)

    @staticmethod
    def sharpen_image(self, img: Image.Image) -> Image.Image:
        enhanced = ImageEnhance.Sharpness(img).factor(1.)
        return enhanced

    @staticmethod
    def to_black_and_white(self, img: Image.Image) -> Image.Image:
        return img.convert("1")

    def new_pdf(self,
        file: "werkzeug.datastructures.FileStorage",
        to_black_and_white = True,
        sharpen = True
        ) -> bool:

        pil_image = Image.open(file)

        if pil_image.size[0] > pil_image.size[1]:
            pil_image = self.rotate_image(pil_image)

        if to_black_and_white:
            pil_image = self.to_black_and_white(pil_image)

        if sharpen:
            pil_image = self.sharpen(pil_image)

        filename = datetime.now().strftime(self._default_name)
        pil_image.save(
            os.path.join(self.save_folder, filename)
        )

        return True

    def load_rotate_save(self, location: str):
        pil_image = Image.open(location)
        rotated = self.rotate_image(location)
        return rotated
