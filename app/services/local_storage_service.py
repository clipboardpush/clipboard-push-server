import glob
import json
import os
import time


def _human_readable(size_bytes):
    b = float(size_bytes)
    for unit in ('B', 'KB', 'MB', 'GB'):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


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


def get_local_storage_usage(storage_path):
    """Returns storage stats dict compatible with R2 usage response format."""
    if not storage_path or not os.path.isdir(storage_path):
        return {
            'bucket': storage_path or '(not configured)',
            'objects_count': 0,
            'total_bytes': 0,
            'total_human': '0 B',
            'scanned_objects': 0,
        }
    total_bytes = 0
    objects_count = 0
    for entry in os.scandir(storage_path):
        if entry.is_file() and not entry.name.endswith('.meta'):
            total_bytes += entry.stat().st_size
            objects_count += 1
    return {
        'bucket': storage_path,
        'objects_count': objects_count,
        'total_bytes': total_bytes,
        'total_human': _human_readable(total_bytes),
        'scanned_objects': objects_count,
    }


def clear_storage(storage_path):
    """Delete all files in storage. Returns {'deleted_objects': n, 'reclaimed_human': '...'}."""
    if not storage_path or not os.path.isdir(storage_path):
        return {'deleted_objects': 0, 'reclaimed_human': '0 B'}
    deleted = 0
    reclaimed = 0
    for entry in os.scandir(storage_path):
        if entry.is_file():
            try:
                size = entry.stat().st_size
                os.remove(entry.path)
                if not entry.name.endswith('.meta'):
                    deleted += 1
                    reclaimed += size
            except Exception:
                pass
    return {'deleted_objects': deleted, 'reclaimed_human': _human_readable(reclaimed)}


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
