import hashlib
import hmac
from typing import Dict

from src.app.core.config import settings


def generate_signature(params: Dict[str, str]) -> str:
    """生成签名"""
    sorted_params = sorted(params.items())
    encoded_params = '&'.join(f'{key}={value}' for key, value in sorted_params)
    return hmac.new(settings.SECRET_KEY.encode(), encoded_params.encode(), hashlib.sha256).hexdigest()


def verify_signature(params: Dict[str, str], signature: str) -> bool:
    """验证签名"""
    generated_signature = generate_signature(params)
    return hmac.compare_digest(generated_signature, signature)
