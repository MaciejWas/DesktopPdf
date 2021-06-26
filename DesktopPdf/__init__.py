from flask import Flask
from DesktopPdf.managers import PassManager, FileManager, SettingsManager
from flask_bootstrap import Bootstrap

app = Flask (__name__)

app.config.from_object("DesktopPdf.configuration.Config")

Bootstrap(app)

app.pass_manager = PassManager()
app.file_manager = FileManager()
app.settings_manager = SettingsManager(
    pass_manager=app.pass_manager,
    file_manager=app.file_manager,
)

app.settings_manager.load_settings()

import DesktopPdf.views
