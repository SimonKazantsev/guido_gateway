from cryptography.hazmat.primitives import serialization


def read_public_key():
    with open(file="public.pem", mode="rb") as file:
        public_key = serialization.load_pem_public_key(file.read())
    return public_key
