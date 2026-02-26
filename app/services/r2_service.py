def format_bytes_human(num_bytes):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def get_r2_bucket_usage(s3_client, bucket_name):
    paginator = s3_client.get_paginator('list_objects_v2')
    total_bytes = 0
    objects_count = 0
    scanned_objects = 0
    for page in paginator.paginate(Bucket=bucket_name):
        contents = page.get('Contents', [])
        scanned_objects += len(contents)
        for obj in contents:
            total_bytes += int(obj.get('Size', 0))
            objects_count += 1
    return {
        'bucket': bucket_name,
        'objects_count': objects_count,
        'total_bytes': total_bytes,
        'total_human': format_bytes_human(total_bytes),
        'scanned_objects': scanned_objects,
    }


def empty_r2_bucket(s3_client, bucket_name):
    paginator = s3_client.get_paginator('list_objects_v2')
    keys_batch = []
    deleted_objects = 0
    reclaimed_bytes = 0
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            key = obj.get('Key')
            if not key:
                continue
            keys_batch.append({'Key': key})
            deleted_objects += 1
            reclaimed_bytes += int(obj.get('Size', 0))
            if len(keys_batch) == 1000:
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': keys_batch, 'Quiet': True}
                )
                keys_batch = []
    if keys_batch:
        s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': keys_batch, 'Quiet': True}
        )
    return {
        'bucket': bucket_name,
        'deleted_objects': deleted_objects,
        'reclaimed_bytes': reclaimed_bytes,
        'reclaimed_human': format_bytes_human(reclaimed_bytes),
    }
