import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from src.app.core.config import settings


def create_rsa_private_public_key(key_size: int = 0) -> tuple[str, str]:
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size or settings.RSA_KEY_SIZE,
        backend=default_backend,
    )

    # 从私钥导出公钥
    public_key = private_key.public_key()

    # 序列化为 PEM 格式
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return pem_private_key.decode('utf-8'), pem_public_key.decode('utf-8')


def get_public_key(str_private_key: str) -> str:
    private_key = serialization.load_pem_private_key(
        str_private_key.encode('utf-8'),
        password=None,
    )

    public_key = private_key.public_key()
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return pem_public_key.decode('utf-8')


def decryption_message(message, str_private_key):
    private_key = serialization.load_pem_private_key(
        str_private_key.encode('utf-8'),
        password=None,
    )

    ciphertext = base64.b64decode(message.encode('utf-8'))
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )
    return plaintext.decode('utf-8')
