import io                                                 # byte stream buffer
import socket                                             # network socket to find local ip
import string                                             # character sets for token
import random                                             # random generator for tokens
import qrcode                                             # qr image generator library


def get_laptop_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create udp socket
        s.connect(("8.8.8.8", 80))                        # dummy route lookup
        ip = s.getsockname()[0]                           # extract local machine ip
        s.close()                                         # close socket
        return ip                                         # return active network ip
    except Exception:
        return "127.0.0.1"                                # fallback to localhost


def create_random_token():
    characters = string.ascii_uppercase + string.digits    # capital letters and numbers
    return "".join(random.choices(characters, k=6))       # 6-character random token


def generate_qr_image(url):
    qr = qrcode.make(url)                                 # generate qr code object
    buffer = io.BytesIO()                                 # create memory buffer
    qr.save(buffer, format="PNG")                         # write png bytes to buffer
    return buffer.getvalue()                              # return raw image bytes
