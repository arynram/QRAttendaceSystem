import io                                                 # for byte buffer
import random                                             # for generating random characters
import socket                                             # for getting local network IP
import string                                             # for uppercase letters and digits
import qrcode                                             # qr code generator library


def get_laptop_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create udp socket
        s.connect(("8.8.8.8", 80))                        # dummy connection to get route
        ip = s.getsockname()[0]                           # extract local ip address
        s.close()                                         # close socket
        return ip                                         # return detected ip
    except Exception:
        return "127.0.0.1"                                # fallback to localhost


def create_random_token():
    chars = string.ascii_uppercase + string.digits        # letters A-Z and digits 0-9
    token = "".join(random.choices(chars, k=6))           # 6-character random token
    return token                                          # return generated token


def generate_qr_image(url):
    qr = qrcode.make(url)                                 # create qr code for url
    buf = io.BytesIO()                                    # create in-memory byte buffer
    qr.save(buf, format="PNG")                            # save qr image as PNG
    return buf.getvalue()                                 # return PNG bytes for streamlit
