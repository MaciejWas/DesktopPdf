print("__init__")

from flask import Flask
from PhotoToDesktop.managers import PassManager, FileManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object("PhotoToDesktop.configuration.Config")

bootstrap = Bootstrap(app)
app.pass_manager = PassManager()
app.file_manager = FileManager()

import PhotoToDesktop.views
