import datetime
decoded = {
  "aud": [
    "2b826b05700c18c4aeb0d6b68d7dda6b651ea8cd69974d77dcaf4051b0a85b01"
  ],
  "email": "n954466@outlook.com",
  "account_id": "fe6305946bffc8a4fa70d17ec31ec2bf",
  "exp": 1751759943,
  "iat": 1751758143,
  "nbf": 1751758143,
  "iss": "https://dahoncho.cloudflareaccess.com",
  "sub": "de2cbab1-c9b0-5a99-8bae-53f53db9cab3",
  "identity": {
    "id": "6WYakXqfX8s8-p5qUfxRFkc-NhE4ynqAi1U1_v_l5EU",
    "name": "n954466",
    "email": "n954466@outlook.com",
    "amr": [
      "pwd",
      "mfa"
    ],
    "oidc_fields": {
      "preferred_username": "n954466@outlook.com"
    },
    "idp": {
      "id": "d5324eb7-e2be-4d38-9aed-390d8c33e2bb",
      "type": "azureAD"
    },
    "geo": {
      "country": "US"
    },
    "user_uuid": "de2cbab1-c9b0-5a99-8bae-53f53db9cab3",
    "account_id": "fe6305946bffc8a4fa70d17ec31ec2bf",
    "iat": 1751758143,
    "ip": "2603:800c:2ef0:3e0:9578:908c:d56:4637",
    "auth_status": "NONE",
    "common_name": "",
    "service_token_id": "",
    "service_token_status": False,
    "is_warp": False,
    "is_gateway": False,
    "mtls_auth": {
      "cert_issuer_ski": "",
      "cert_presented": False,
      "cert_serial": "",
      "cert_issuer_dn": "",
      "auth_status": "NONE"
    },
    "version": 2
  },
  "type": "org",
  "identity_nonce": "vTXBofAZzvKzNDV5"
}

object = {
    "email":decoded.get("email"),
"sub":decoded.get("sub"),
"name":decoded.get("name",'noName'),
"aud":decoded.get("aud"),
"iss":decoded.get("iss"),
"exp":datetime.datetime.fromtimestamp(decoded.get('exp')),
"preferred_username":decoded.get('identity').get('oidc_fields').get('preferred_username'),
"upn":decoded.get('identity').get('oidc_fields').get('upn','')

}


print(object)