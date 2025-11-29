import functools
import jwt
from dotenv import load_dotenv
import os
from flask import request, jsonify
import requests
from datetime import datetime
load_dotenv()
CF_CERT_URL = f"https://{os.getenv('CF_URL_CDN_CGI_CERTS')}/cdn-cgi/access/certs"
CERT_KYS = requests.get(CF_CERT_URL).json()
CF_AUDIENCE_ID = os.getenv('CF_AUD_ID')
ENV = os.getenv('ENV','prod')
def require_cf_token(fn):
    @functools.wraps(fn)
    def wrapper(*args,**kwargs):
        if ENV=='dev':
            return fn(*args,**kwargs)
        else:
            token = request.headers.get("Cf-Access-Jwt-Assertion") or request.cookies.get("CF_Authorization")
            if not token:
                return jsonify({
                    "error":"missing token"
                }),401
            headers = jwt.get_unverified_header(token)
            try:
                key = next(k for k in CERT_KYS["keys"] if k["kid"]==headers["kid"])
            except StopIteration:
                return jsonify(
                    {
                        "success":False,
                        "message":"invalid key id"
                    }
                ),401
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            try:
                decoded = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=CF_AUDIENCE_ID)
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "message": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"success": False, "message": "Invalid token"}), 401
            custom = decoded.get("custom",{}) or {}
            request.cf_identity={
                "email":decoded.get("email"),
                "user":custom.get("preferred_username") or custom.get("upn") or decoded.get("email"),
                "raw":decoded
            }
            return fn(*args,**kwargs)
    return wrapper