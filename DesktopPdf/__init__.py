print("__init__")

from flask import Flask
from DesktopPdf.managers import PassManager, FileManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object("DesktopPdf.configuration.Config")

bootstrap = Bootstrap(app)
app.pass_manager = PassManager()
app.file_manager = FileManager()

import DesktopPdf.views
