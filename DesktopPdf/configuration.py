import socket
import os


class Config(object):
    DEBUG = False
    TESTING = False
    BOOTSTRAP_FONTAWESOME = True
    SECRET_KEY = "DesktopPdf"
    CSRF_ENABLED = True


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    local_ip_address = s.getsockname()[0]
    s.close()
    return local_ip_address


def get_server_port():
    port = int(os.environ.get("PORT", 5000))
    return port
