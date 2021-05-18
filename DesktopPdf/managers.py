import os
import io
from PIL import Image
from datetime import datetime
import yaml

from DesktopPdf.configuration import get_local_ip


class PassManager:
    def __init__(self):
        self._pass = "1234"
        self.local_ip = get_local_ip()
        self._ips = [self.local_ip]

    def get_password(self):
        print(f"Getting password={self._pass}")
        return self._pass

    def set_password(self, new_password: str):
        print(f"Setting password to {new_password}")
        self._ips = [self.local_ip]
        self._pass = new_password

    def validate_password(self, password):
        print(
            f"Jakiś ziomek próbuje hasło {password} ale prawdziwe jest {self.get_password()}"
        )
        print(f"Czyli zwracam {password == self.get_password()}")
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
        self._download_dir = os.path.join("app", "PTDdownloads")
        self._default_name = "PDF_%H:%M:%S_%d-%m-%Y.pdf"
        self.history_path = os.path.join("..", ".history", "history.yml")

        print(f"History path: {self.history_path}")

        if ".history" not in os.listdir():
            os.mkdir("../.history")
            with open(self.history_path, "w") as f:
                yaml.dump(
                    {
                        "memory_since": datetime.now().strftime("%H:%M:%S_%d-%m-%Y"),
                        "received_files": [],
                    },
                    f,
                )

    def set_download_dir(self, new_download_dir: str) -> None:
        self._download_dir = new_download_dir

    def get_download_dir(self) -> str:
        return self._download_dir

    def new_pdf(self, file: "werkzeug.datastructures.FileStorage") -> bool:
        try:
            pil_image = Image.open(file)
            pil_image.save(
                os.path.join(".history", datetime.now().strftime(self._default_name))
            )
            return True

        except Exception as e:
            print(e)
            return False

    def save_file_info(self, request):
        title = request["title"]
        time = request["datetime"]

        with open(self.history_path, "rw") as f:
            history = yaml.load(f)

            while title in history.keys():
                title = title + "_new"

            history["received_files"] += {"title": title, "time": time}
            yaml.dump(history, f)
