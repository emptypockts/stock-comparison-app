import functools
from dotenv import load_dotenv
load_dotenv()
import jwt
import os
from typing import Callable, Any
from flask import request, jsonify
import requests
from eacsa_logger import setup_logging,get_logger
setup_logging()
logger = get_logger(__name__)
from datetime import datetime, timedelta
from app_constants import EMAIL_DEV, USER_DEV, CF_AUDIENCE_ID, CF_CERT_URL, CURRENT_ENVIRONMENT
_cert_cache : dict = {}
_cert_cache_expiry : datetime | None = None
CERT_TTL = timedelta(hours=24)

def get_cf_certs()->dict:
    global _cert_cache, _cert_cache_expiry
    now = datetime.now()
    if _cert_cache and _cert_cache_expiry and now < _cert_cache_expiry:
        return _cert_cache
    response = requests.get(CF_CERT_URL, timeout=5)
    response.raise_for_status()
    _cert_cache = response.json()
    _cert_cache_expiry = now + CERT_TTL
    return _cert_cache
 

def require_cf_token(fn:Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args,**kwargs) -> Any:
        if CURRENT_ENVIRONMENT == 'dev':
            logger.info("running in DEV mode")
            request.cf_identity = {
                'email': EMAIL_DEV,
                'user': USER_DEV
            } 
            return fn(*args,**kwargs)
        else:
            logger.info("running prod mode")
            token = request.headers.get("Cf-Access-Jwt-Assertion") or request.cookies.get("CF_Authorization")
            if not token:
                return jsonify({
                    "error": "missing token"
                }),401
            headers = jwt.get_unverified_header(token)
            try:
                keys = get_cf_certs()
                key = next(k for k in keys["keys"] if k["kid"] == headers["kid"])
            except StopIteration:
                return jsonify(
                    {
                        "success": False,
                        "message": "invalid key id"
                    }
                ),401
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            try:
                decoded = jwt.decode(
                token,
                public_key,
                algorithms = ["RS256"],
                audience = CF_AUDIENCE_ID)
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "message": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"success": False, "message": "Invalid token"}), 401
            custom = decoded.get("custom",{}) or {}
            request.cf_identity = {
                "email":decoded.get("email"),
                "user":custom.get("preferred_username") or custom.get("upn") or decoded.get("email"),
                "raw":decoded
            }
            return fn(*args, **kwargs)
    return wrapper
