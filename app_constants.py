from dotenv import load_dotenv
load_dotenv()
import os

# JWT
JWT_SECRET = os.getenv('JWT_SECRET')

# Application (client) ID of app registration
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
# Application's generated client secret: never check this into source control!
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")

# You can configure your authority via environment variable
# Defaults to a multi-tenant app in world-wide cloud
MICROSOFT_AUTHORITY = os.getenv("MICROSOFT_AUTHORITY", "https://login.microsoftonline.com/common")

MICROSOFT_REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
MICROSOFT_GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
MICROSOFT_SCOPE = ["User.ReadBasic.All"]

# Tells the Flask-session extension to store sessions in the filesystem
SESSION_TYPE = "filesystem"
# Using the file system will not work in most production systems,
# it's better to use a database-backed session store instead.

# Where SEC filings are stored
SEC_DIRECTORY = os.getenv('SEC_DIRECTORY')

# URI to connect MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')

# Cloudflare Login parameters
CF_AUDIENCE_ID = os.getenv('CF_AUD_ID')
CF_CERT_URL = f"https://{os.getenv('CF_URL_CDN_CGI_CERTS')}/cdn-cgi/access/certs"

# API KEYS and URIs for some financial metrics.
ALPHA_VANTAGE_API_KEY  = os.getenv('ALPHA_VANTAGE_API_KEY')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
FRED_API_KEY = os.getenv('FRED_API_KEY')
TWELVE_API_KEY = os.getenv('TWELVE_API_KEY')
TWELVE_URI = os.getenv('TWELVE_URI')
CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')


# AI API KEYS AND URIs
GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
DEEP_SEEK_API_KEY = os.getenv('DEEP_SEEK_API_KEY')


# LOGGER
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# EMAIL SERVICE 
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# DEV Testing authentication
EMAIL_DEV = os.getenv('EMAIL_DEV')
USER_DEV = os.getenv('USER_DEV')

# ENVIRONMENT SCENARIO TO OVERRIDE AUTH
CURRENT_ENVIRONMENT = os.getenv('CURRENT_ENVIRONMENT')

# WEB Sockets
WS_SOCKET_URI = os.getenv('VITE_WS_SERVER')

# REDIS
REDIS_SERVER_URI = os.getenv('REDIS_SERVER_URI')

# FLASK DEBUG
FLASK_DEBUG = os.getenv("FLASK_DEBUG")