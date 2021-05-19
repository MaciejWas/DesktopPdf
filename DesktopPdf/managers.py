import os
from PIL import Image
from datetime import datetime

from DesktopPdf.configuration import get_local_ip


class PassManager:
    def __init__(self):
        self._pass = "1234"
        self.local_ip = get_local_ip()
        self._ips = [self.local_ip]

    def get_password(self):
        return self._pass

    def set_password(self, new_password: str):
        self._ips = [self.local_ip]
        self._pass = new_password

    def validate_password(self, password):
        return password == self.get_password()

    def register_ip(self, ip):
        self._ips.append(ip)

    def validate_ip(self, ip):
        if ip in self._ips:
            return True
        else:
            return False


class FileManager:
    def __init__(self):
        self.save_folder = "pdfs"
        self._default_name = "PDF_%H:%M:%S_%d-%m-%Y.pdf"
        if self.save_folder not in os.listdir():
            os.mkdir(self.save_folder)

    def new_pdf(self, file: "werkzeug.datastructures.FileStorage") -> bool:
        pil_image = Image.open(file)

        if pil_image.size[0] > pil_image.size[1]:
            pil_image = pil_image.rotate(90)
        filename = datetime.now().strftime(self._default_name)
        pil_image.save(
            os.path.join(self.save_folder, filename)
        )
        print("save ok???")
        return True