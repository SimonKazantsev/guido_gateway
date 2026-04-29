from cryptography.hazmat.primitives import serialization


def read_public_key(file_path: str):
    with open(file=file_path, mode="rb") as file:
        public_key = serialization.load_pem_public_key(file.read())
    return public_key
