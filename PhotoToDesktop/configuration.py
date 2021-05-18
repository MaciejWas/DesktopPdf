import socket
import os


class Config(object):
    """
    Configuration base, for all environments.
    """

    DEBUG = False
    TESTING = False
    BOOTSTRAP_FONTAWESOME = True
    SECRET_KEY = "MINHACHAVESECRETA"
    CSRF_ENABLED = True


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    return local_ip_address


def get_server_port():
    port = int(os.environ.get("PORT", 5000))
    return port
