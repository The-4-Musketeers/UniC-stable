from tempfile import mkdtemp


GOOGLE_CLIENT_ID = "560689788667-2or0hcftq62kvr8qhik62pjl0lhlatqi.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"
TEMPLATES_AUTO_RELOAD = True