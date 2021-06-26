from flask import request, render_template, redirect
from functools import wraps
import os
import base64
import zlib

from DesktopPdf.forms import LogInForm, PhotoForm
from DesktopPdf.configuration import get_local_ip, get_server_port
from DesktopPdf import app


def find_deduplicated_files():
    save_dir = app.file_manager.save_folder
    pdf_paths = [
        os.path.join("pdfs", fname) for fname in os.listdir(save_dir)\
        if (fname.endswith(".pdf")) and ("temporary" not in fname)
    ]

    files = [
        app.file_manager.search_for_pdf(path) for path in pdf_paths
    ]

    files = sorted(files, key=lambda x: x["date_created"], reverse=True)

    deduplicated_files = []
    for f in files:
        if f not in deduplicated_files:
            deduplicated_files.append(f)

    return deduplicated_files

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
def should_be_gallery():
    return redirect("/gallery")


@app.route("/gallery")
@login_required
def gallery():
    files = find_deduplicated_files()

    return render_template(
        "gallery.html",
        password=app.pass_manager.get_password(),
        ip=get_local_ip(),
        port=get_server_port(),
        focus="gallery",
        files=files
    )

@app.route("/options", methods=["GET", "POST"])
@login_required
def options():
    if request.method == "POST":
        if request.form.get("default") == "1":
            app.settings_manager.restore_default()

        elif request.form.get("deletedb") == "1":
            app.file_manager.purge_database()

        else:
            app.pass_manager.update(form=request.form)
            app.file_manager.update(form=request.form)
            app.settings_manager.update(form=request.form)

        if app.settings_manager.remember:
            print("Saving settings")
            app.settings_manager.save_settings()



    return render_template(
        "options.html",
        focus="options",
        current_password=app.pass_manager.get_password(),
        current_default_filename=app.file_manager.get_default_filename(),
        current_date_format=app.file_manager.get_date_format(),
        sharpen="checked" if app.file_manager.sharpen else "",
        grayscale="checked" if app.file_manager.grayscale else "",
        rotate="checked" if app.file_manager.rotate else "",
        remember="checked" if app.settings_manager.remember else "",
    )

@app.route("/login", methods=["GET", "POST"])
def login_site():
    app.logger.info("Address", request.remote_addr, "is trying to log in.")

    wrong_password = False

    # Login logic
    if request.method == "POST":

        user_password = request.form.get("password")
        password_is_valid = app.pass_manager.validate_password(user_password)

        if password_is_valid:
            app.logger.info("Successful log in from", request.remote_addr)
            app.pass_manager.register_ip(request.remote_addr)
            return redirect("/gallery")

        else:
            app.logger.info("Unsuccessful log in from", request.remote_addr)
            wrong_password = True

    return render_template(
        "login.html",
        title="Login",
        wrong_password=wrong_password
    )


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    form = PhotoForm()
    uploaded = False
    if request.method == "POST":
        photo_data = form.photo.data
        if photo_data is not None:
            app.file_manager.new_temporary_pdf(photo_data)

        if request.form.get("merge") == "1":
            print(request.form)
            description = request.form.get("description")
            print("Description:", description)
            app.file_manager.merge_temporary_pdfs(description)
            uploaded = True

    temporary_files = [
        f for f in os.listdir(app.file_manager.save_folder)\
        if (f.endswith(".pdf")) and ("temporary" in f)
    ]

    return render_template(
        "/upload.html",
        photo_form=form,
        focus="upload",
        temporary_files=temporary_files,
        no_temp = len(temporary_files) == 0,
        uploaded=uploaded
    )


# @app.route("/downloads/", methods=["GET"])
# @login_required
# def files():
    # download_folder = app.file_manager.save_folder
    # downloaded_files = os.listdir(download_folder)
    # files = []
    # for file in downloaded_files:
    #     with open(os.path.join(download_folder, file), "rb") as f:
    #         files.append(
    #             {"name": file, "b64": base64.b64encode(f.read()).decode("ascii")}
    #         )

    # return render_template("downloads.html") #, files=files)

@app.route("/shutdown", methods=["GET"])
@login_required
def shutdown():
    shutdown_function = request.environ.get("werkzeug.server.shutdown")
    shutdown_function()
    return "Server shut down"
