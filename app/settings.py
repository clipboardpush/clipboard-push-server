import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
PASSWORD_HASH_FILE = os.path.join(DATA_DIR, 'admin_password.hash')

R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID', 'YOUR_ACCOUNT_ID_HERE')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY_HERE')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', 'YOUR_SECRET_KEY_HERE')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', 'clipboard-man-relay')
DASHBOARD_R2_BUCKET = os.environ.get('DASHBOARD_R2_BUCKET', 'clipboard-push-relay')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')

_flask_secret = os.environ.get('FLASK_SECRET_KEY', '')
_is_production = os.environ.get('FLASK_DEBUG', '0') != '1'
if not _flask_secret and _is_production:
    raise RuntimeError(
        'FLASK_SECRET_KEY environment variable is not set. '
        'Set a strong random key before running in production.'
    )
FLASK_SECRET_KEY = _flask_secret or 'dev_secret_key'

# FCM: path to Firebase service account JSON (leave empty to disable FCM)
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', '')

# File storage backend: 'r2' (default) or 'local'
STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'r2')
LOCAL_STORAGE_PATH = os.environ.get('LOCAL_STORAGE_PATH', os.path.join(DATA_DIR, 'uploads'))
LOCAL_STORAGE_BASE_URL = os.environ.get('LOCAL_STORAGE_BASE_URL', 'http://localhost:5055')
