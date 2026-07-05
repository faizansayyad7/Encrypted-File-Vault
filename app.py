from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import hashlib
import base64
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ENCRYPT_FOLDER = "encrypted"
DECRYPT_FOLDER = "decrypted"

for folder in [UPLOAD_FOLDER, ENCRYPT_FOLDER, DECRYPT_FOLDER]:
    os.makedirs(folder, exist_ok=True)


def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        file = request.files["file"]
        password = request.form["password"]
        action = request.form["action"]

        filename = file.filename
        upload_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(upload_path)

        key = generate_key(password)
        cipher = Fernet(key)

        with open(upload_path, "rb") as f:
            data = f.read()

        try:

            if action == "encrypt":

                encrypted_data = cipher.encrypt(data)

                output_path = os.path.join(
                    ENCRYPT_FOLDER,
                    filename + ".enc"
                )

                with open(output_path, "wb") as f:
                    f.write(encrypted_data)

                return send_file(
                    output_path,
                    as_attachment=True
                )

            elif action == "decrypt":

                decrypted_data = cipher.decrypt(data)

                output_path = os.path.join(
                    DECRYPT_FOLDER,
                    filename.replace(".enc", "")
                )

                with open(output_path, "wb") as f:
                    f.write(decrypted_data)

                return send_file(
                    output_path,
                    as_attachment=True
                )

        except:
            message = "Wrong Password or Invalid File"

    return render_template(
        "index.html",
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)