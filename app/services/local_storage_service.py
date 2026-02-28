import glob
import json
import os
import time


def ensure_storage_dir(path):
    os.makedirs(path, exist_ok=True)


def make_file_key(filename):
    return f"{int(time.time() * 1000)}_{filename}"


def write_file(storage_path, file_key, data: bytes, content_type: str):
    ensure_storage_dir(storage_path)
    with open(os.path.join(storage_path, file_key), 'wb') as f:
        f.write(data)
    with open(os.path.join(storage_path, file_key + '.meta'), 'w') as f:
        json.dump({'content_type': content_type, 'created_at': time.time()}, f)


def read_file(storage_path, file_key):
    """Returns (bytes, content_type) or (None, None) if not found."""
    file_path = os.path.join(storage_path, file_key)
    meta_path = os.path.join(storage_path, file_key + '.meta')
    if not os.path.exists(file_path):
        return None, None
    content_type = 'application/octet-stream'
    if os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                content_type = json.load(f).get('content_type', content_type)
        except Exception:
            pass
    with open(file_path, 'rb') as f:
        return f.read(), content_type


def purge_old_files(storage_path, max_age_s=3600):
    """Delete files older than max_age_s seconds. Returns count of deleted files."""
    if not os.path.isdir(storage_path):
        return 0
    now = time.time()
    deleted = 0
    for meta_path in glob.glob(os.path.join(storage_path, '*.meta')):
        try:
            with open(meta_path) as f:
                created_at = json.load(f).get('created_at', 0)
            if now - created_at > max_age_s:
                file_key = os.path.basename(meta_path)[:-5]  # strip .meta
                data_path = os.path.join(storage_path, file_key)
                if os.path.exists(data_path):
                    os.remove(data_path)
                    deleted += 1
                os.remove(meta_path)
        except Exception:
            pass
    return deleted
