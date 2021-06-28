import os
import requests
import multiprocessing
import platform
import argparse

from DesktopPdf import app
from DesktopPdf.configuration import get_server_port

parser = argparse.ArgumentParser()
parser.add_argument('--test-login', type=bool, help='Start app with empty IP whitelist.')
args = parser.parse_args()

def run_chrome():
    port = get_server_port()
    link = "http://" + app.pass_manager.local_ip + ":" + str(port)
    if platform.system() == "Linux":
        os.system("google-chrome --app=" + link)
        requests.get(link + "/shutdown")

    elif platform.system() == "Windows":
        os.system("start chrome --app=" + link)

    else:
        raise Exception("Chrome GUI is not implemented for your OS.")


def run_app(test_login):
    port = get_server_port()

    if test_login:
        app.pass_manager.purge_whitelist()

    app.run(host="0.0.0.0", port=port)


def main(test_login):
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        chrome_process = multiprocessing.Process(target=run_chrome)
        chrome_process.start()

    run_app(test_login)

if __name__ == "__main__":
    main(args.test_login)
