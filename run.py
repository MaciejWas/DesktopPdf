import os
import requests
import multiprocessing

from DesktopPdf import app
from DesktopPdf.configuration import get_server_port


def run_chrome():
    port = get_server_port()
    link = "http://" + app.pass_manager.local_ip + ":" + str(port)
    os.system("google-chrome --app=" + link)
    requests.get(link + "/shutdown")


def run_app():
    port = get_server_port()
    app.run(host="0.0.0.0", port=port)


def main():
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        chrome_process = multiprocessing.Process(target=run_chrome)
        chrome_process.start()

    run_app()

if __name__ == "__main__":
    main()
