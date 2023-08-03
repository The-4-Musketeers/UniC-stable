from tempfile import mkdtemp


# GOOGLE_CLIENT_ID = "get your Google OAuth client ID from the Google developer console and put it here"
# GOOGLE_CLIENT_SECRET = "get your client secret key from the Google developer console and put it here"
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"
TEMPLATES_AUTO_RELOAD = True
