import os
from PIL import Image, ImageEnhance, UnidentifiedImageError
from datetime import datetime
import random
import yaml
from sqlitedict import SqliteDict
import zlib
import base64
from PyPDF2 import PdfFileMerger

from DesktopPdf.configuration import get_local_ip

def get_random_digits(n=6):
    if n <= 0:
        return ""

    password_number = random.randint(0, int("9" * n))
    password = str(password_number)
    password = "0" * (n-len(password)) + password
    return password

def is_turned_on(checkbox_form_value: str):
    if checkbox_form_value in ["on", True]:
        return True
    else:
        return False


class Counter():
    def __init__(self):
        self.value = 0

    def next(self):
        self.value += 1
        return self.value

    def zero(self):
        self.value = 0


class PassManager:
    """Manages the current password, along with the IP whitelist"""

    def __init__(self):
        self._current_password = get_random_digits(n=6)
        self.local_ip = get_local_ip()
        self._ips_with_access = [self.local_ip]

    # Settings

    def update(self, settings: "multidict.MultiDict") -> None:
        """Updates the current settings"""

        self.set_password(
            settings.get("password")
        )

    def export_settings(self) -> dict:
        settings = {
            "password": self.get_password()
        }
        return settings

    # Password

    def get_password(self) -> str:
        return self._current_password

    def new_random_password(self):
        new_password = get_random_digits(n=6)
        print("New random password:", new_password)
        self.set_password(new_password)

    def set_password(self, new_password: str) -> None:
        print("Setting new password.")

        if new_password == "<random>":
            print("New pass is supposed to be random.")
            self.new_random_password()

        elif new_password == self._current_password:
            print("New password is the same as old.")
            pass

        else:
            print("Ultimately setting password to:", new_password)

            self._ips_with_access = [self.local_ip]
            self._current_password = new_password

    def validate_password(self, password: str) -> bool:
        return password == self._current_password

    # IP Whitelist

    def register_ip(self, ip: str) -> None:
        self._ips_with_access.append(ip)

    def purge_whitelist(self) -> None:
        self._ips_with_access = []

    def has_access(self, ip: str) -> bool:
        if ip in self._ips_with_access:
            return True
        else:
            return False


class FileManager:
    """Processes new images into pdf files and keeps track of all uploaded files"""

    def __init__(self):
        self.save_folder = "pdfs"
        self._date_format = r"%H:%M:%S_%d-%m-%Y"
        self._default_filename = f"PDF_{self._date_format}.pdf"

        self.sharpen = False
        self.grayscale = True
        self.rotate = True

        self.temporary_counter = Counter()

        self.database = SqliteDict("database.sqlite", autocommit=True)

        if self.save_folder not in os.listdir():
            os.mkdir(self.save_folder)

    # Date

    def get_date_format(self) -> str:
        return self._date_format

    def set_date_format(self, new_date_format: str) -> None:
        old_date_format = self._date_format
        self._date_format = new_date_format

        self._default_filename = self._default_filename.replace(old_date_format, new_date_format)

    def set_default_filename(self, new_filename: str) -> None:
        print(f"Received new default filename: {new_filename}")

        self._default_filename = new_filename.replace("<date>", self._date_format)

        print(f"Now filename is {self._default_filename}")

    def get_default_filename(self) -> str:
        print("getting default filename:", self._default_filename)
        return self._default_filename.replace(self._date_format, "<date>")

    def get_filename(self) -> str:
        current_date = datetime.now()
        base_filename = current_date.strftime(self._default_filename)
        pdfs = os.listdir(self.save_folder)

        if base_filename in pdfs:
            base_filename_no_ext = base_filename.replace(".pdf", "")
            count = len(
                [f for f in pdfs if f.startswith(base_filename_no_ext)]
            )

            filename = base_filename.replace(".pdf", f" ({count - 1}).pdf")

        else:
            filename = base_filename

        return filename

    # Settings

    def update(self, settings: "multidict.MultiDict") -> None:
        self.set_default_filename(
            settings.get("filename")
        )
        self.set_date_format(
            settings.get("dateformat")
        )

        self.rotate = is_turned_on(settings.get("rotate"))
        self.sharpen = is_turned_on(settings.get("sharpen"))
        self.grayscale = is_turned_on(settings.get("grayscale"))

    def export_settings(self) -> dict:
        settings = {
                "filename": self.get_default_filename(),
                "dateformat": self.get_date_format(),
                "rotate": self.rotate,
                "sharpen": self.sharpen,
                "grayscale": self.grayscale,
        }
        return settings

    # Image processing

    @staticmethod
    def rotate_image(img: Image.Image) -> Image.Image:
        return img.rotate(90, expand=True)

    @staticmethod
    def sharpen_image(img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Sharpness(img)
        enhanced = enhancer.enhance(1.2)
        return enhanced

    @staticmethod
    def to_grayscale(img: Image.Image) -> Image.Image:
        return img.convert("L")

    def process(self, img: Image.Image) -> Image.Image:
        """Applies rotation, grayscale and sharpening, according to settings"""

        if self.rotate and (img.size[0] > img.size[1]):
            img = self.rotate_image(img)

        if self.grayscale:
            img = self.to_grayscale(img)

        if self.sharpen:
            img = self.sharpen_image(img)

        return img

    @staticmethod
    def get_file_hash(path_to_file: str) -> int:
        """Returns the hash of the file at `path_to_file`"""

        with open(path_to_file, "rb") as f:
            content = f.read()
            encoded_content = base64.b64encode(content)
            pdf_hash = zlib.adler32(encoded_content)

        return pdf_hash

    def get_save_path(self, filename: str) -> str:
        save_path = os.path.join(self.save_folder, filename)
        return save_path

    def _merge_and_save(
        self,
        pdfs: list[str],
        save_path: str
    ) -> None:

        merger = PdfFileMerger()

        for file in pdfs:
            merger.append(file)

        merger.write(save_path)
        merger.close()

    def find_temporary_pdfs(self) -> list[str]:
        temporary_pdfs = [
            os.path.join(self.save_folder, f)\
            for f in os.listdir(self.save_folder)\
            if ("temporary" in f) and (f.endswith(".pdf"))
        ]
        return temporary_pdfs

    def save_to_database(self,
        pdf_hash: int,
        filename: str,
        description: str
    ) -> None:

        if str(pdf_hash) in self.database.keys():
            # If hash is in database then add the old data to description

            old_data = self.database[pdf_hash]

            old_title = old_data["title"]
            old_date = old_data["date_created"]

            old_info = f" (duplicate of '{old_title}' submitted at {old_date})"

            self.database[pdf_hash] = {
                "title": filename,
                "description": description + old_info,
                "date_created": datetime.now()
            }

            old_file_loc = os.path.join(self.save_folder, old_title)

            # Remove the old file if it is still in self.save_folder

            try:
                os.remove(old_file_loc)

            except FileNotFoundError:
                pass

        else:
            self.database[pdf_hash] = {
                "title": filename,
                "description": description,
                "date_created": datetime.now()
            }

    def new_temporary_pdf(
        self,
        file: "werkzeug.datastructures.FileStorage",
    ) -> bool:

        try:
            pil_image = Image.open(file)
        except UnidentifiedImageError:
            return False

        if pil_image.mode == "RGBA":
            # raise RuntimeError(
            #     "Image mode is RGBA, it should be RGB. "
            #     "Are you trying to upload a .png file?"
            #     )
            return False

        pil_image = self.process(pil_image)

        temp_id = self.temporary_counter.next()
        save_path = os.path.join(self.save_folder, f"temporary_pdf_{temp_id}.pdf")
        pil_image.save(save_path)

        return True

    def merge_temporary_pdfs(self,
        description: str="No description",
    ) -> None:
        """
        Merges all temporary pdfs at `self.save_folder`, deletes them, and
        saves the merged pdf
        """

        temporary_pdfs = self.find_temporary_pdfs()

        filename = self.get_filename()
        save_path = self.get_save_path(filename)

        self._merge_and_save(temporary_pdfs, save_path)

        self.temporary_counter.zero()
        for temp_pdf in temporary_pdfs:
            os.remove(temp_pdf)

        pdf_hash = self.get_file_hash(save_path)

        self.save_to_database(
            pdf_hash=pdf_hash,
            filename=filename,
            description=description
        )

    def search_for_pdf(self, filepath: str):
        with open(filepath, "rb") as f:
            content = f.read()
            encoded_content = base64.b64encode(content)
            pdf_hash = zlib.adler32(encoded_content)

        try:
            data = self.database[pdf_hash]
            if not filepath.endswith(data["title"]):
                _, filename = os.path.split(filepath)
                data["description"] += f" (Currently named {filename})"

            data["b64_file"] = encoded_content.decode("ascii")

        except KeyError:
            data = {
                "title": filepath,
                "description": "Not available",
                "date_created": datetime.min,
                "b64_file": encoded_content.decode("ascii")
            }

        return data

    def purge_database(self):
        for pdf_hash in self.database.keys():
            pdf_hash = int(pdf_hash)
            del self.database[pdf_hash]

class SettingsManager:

    def __init__(self, file_manager, pass_manager):
        self.remember = False
        self.file_manager = file_manager
        self.pass_manager = pass_manager

        self.default_settings = {
            "dateformat": '%H:%M:%S_%d-%m-%Y',
            "filename": "PDF_<date>.pdf",
            "grayscale": True,
            "password": "382941",
            "remember": False,
            "rotate": True,
            "sharpen": False,
        }

    def purge_settings(self):
        if "settings.yaml" in os.listdir():
            os.remove("settings.yaml")

    def update(self, settings: "multidict.MultiDict") -> None:
        self.remember = is_turned_on(settings.get("remember"))
        if not self.remember:
            self.purge_settings()

    def update_all(self, settings: "multidict.MultiDict") -> None:
        self.file_manager.update(settings)
        self.pass_manager.update(settings)
        self.update(settings)

    def restore_default(self) -> None:
        self.update_all(self.default_settings)

    def get_settings(self) -> dict:
        settings = {
            "remember": self.remember,
            **self.file_manager.export_settings(),
            **self.pass_manager.export_settings()
        }
        return settings

    def save_settings(self) -> None:
        settings = self.get_settings()
        print("Saving settings:")
        print(settings)
        with open("settings.yaml", "w") as f:
            yaml.dump(settings, f)

    def load_settings(self) -> None:
        try:
            with open("settings.yaml", "r") as f:
                settings = yaml.load(f)
                print("Loaded settings:")
                print(settings)
                self.update(settings)

        except FileNotFoundError:
            print("Settings file not found.")

        if self.remember:
            self.update_all(settings)
