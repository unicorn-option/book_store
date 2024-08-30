import base64
import hashlib
import hmac
import secrets
import struct
import time


def generate_secret_key(length=32):
    random_bytes = secrets.token_bytes(length)
    return base64.b32encode(random_bytes).decode('utf-8').rstrip('=')


def padding_base32(secret_key):
    # 补齐 Base32  密钥长度至 8 的整数倍
    return '{key}{equal}'.format(key=secret_key, equal='=' * ((8 - len(secret_key) % 8) % 8))


def base36_encode(number):
    # chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    chars = '0123456789ABCDEF'
    result = []
    while number > 0 and len(result) < 6:
        # number, remainder = divmod(number, 36)
        number, remainder = divmod(number, 16)
        result.append(chars[remainder])
    result.reverse()
    return ''.join(result)


def create_totp_token(secret_key):
    # 解码 Base32编码的密钥
    key = base64.b32decode(padding_base32(secret_key), True)

    # 时间步数
    time_counter = int(time.time() // 60)
    time_bytes = struct.pack('>Q', time_counter)

    # HMAC-SHA1
    hmac_hash = hmac.new(key, time_bytes, hashlib.sha1).digest()

    # 动态截取生成 TOTP 令牌
    offset = hmac_hash[-1] & 0x0F
    code = (struct.unpack('>I', hmac_hash[offset : offset + 4])[0] & 0xFFFF_FFFF) % 1_000_000_000

    return base36_encode(code)
