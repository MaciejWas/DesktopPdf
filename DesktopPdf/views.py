from flask import request, render_template, redirect
from functools import wraps
import os
import base64

from DesktopPdf.forms import NewPassForm, LogInForm, PhotoForm
from DesktopPdf.configuration import get_local_ip, get_server_port
from DesktopPdf import app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged_in = app.pass_manager.validate_ip(request.remote_addr)
        if not logged_in:
            app.logger.info("Failed log in attempt from", request.remote_addr)
            return redirect("/login")
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def should_be_index():
    return redirect("/index")


@app.route("/index")
@login_required
def index():
    return render_template(
        "index.html",
        password=app.pass_manager.get_password(),
        ip=get_local_ip(),
        port=get_server_port(),
    )


@app.route("/login", methods=["GET", "POST"])
def login_site():
    app.logger.info("Address", request.remote_addr, "is trying to log in.")

    form = LogInForm()
    wrong_password_message = ""

    # Login logic
    if request.method == "POST":
        password_is_valid = app.pass_manager.validate_password(form.password._value())
        if password_is_valid:
            app.logger.info("Successful log in from", request.remote_addr)
            app.pass_manager.register_ip(request.remote_addr)
            return redirect("/index")
        else:
            app.logger.info("Unsuccessful log in from", request.remote_addr)
            wrong_password_message = "Wrong password!"

    return render_template(
        "login.html",
        title="Login",
        form=form,
        wrong_password_message=wrong_password_message,
    )


@app.route("/pass/", methods=["GET", "POST"])
@login_required
def password():
    form = NewPassForm()

    if request.method == "POST":
        app.pass_manager.set_password(form.password._value())
        return redirect("/index")

    return render_template("pass.html", title="Change Password", form=form)


@app.route("/upload-image", methods=["GET", "POST"])
@login_required
def upload_image():
    form = PhotoForm()
    if request.method == "POST":
        photo_data = form.photo.data
        app.file_manager.new_pdf(photo_data)
    return render_template("/upload_image.html", form=form)


@app.route("/files/", methods=["GET"])
@login_required
def files():
    download_folder = app.file_manager.save_folder
    downloaded_files = os.listdir(download_folder)
    files = []
    for file in downloaded_files:
        with open(os.path.join(download_folder, file), "rb") as f:
            files.append(
                {"name": file, "b64": base64.b64encode(f.read()).decode("ascii")}
            )

    return render_template("files.html", files=files)

@app.route("/shutdown/", methods=["GET"])
@login_required
def shutdown():
    shutdown_function = request.environ.get("werkzeug.server.shutdown")
    shutdown_function()
    return "Server shut down"
