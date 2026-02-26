import logging
import os

from dotenv import load_dotenv
load_dotenv()

import boto3
import urllib3
from botocore.config import Config
from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

from .auth import User, load_password_hash, register_user_loader, verify_password
from .route import register_routes
from .services.r2_service import empty_r2_bucket, get_r2_bucket_usage

from .settings import (
    ADMIN_PASSWORD,
    DASHBOARD_R2_BUCKET,
    FLASK_SECRET_KEY,
    PASSWORD_HASH_FILE,
    R2_ACCESS_KEY_ID,
    R2_ACCOUNT_ID,
    R2_BUCKET_NAME,
    R2_SECRET_ACCESS_KEY,
)
from .signal_core import (
    ALLOWED_ACTIVITY_TYPES,
    CLIENT_JOINED_AT_MS,
    CLIENT_LAST_SEEN_MS,
    CLIENT_NETWORK_META,
    CLIENT_PROBE_META,
    CLIENT_ROOMS,
    CLIENT_SESSIONS,
    CLIENT_TYPES,
    CLIENT_DEVICE_NAMES,
    PENDING_LAN_PROBES,
    ROOM_CLIENT_ORDER,
    ROOM_LAST_PROBE,
    TRANSFER_CONTEXTS,
    bind_runtime,
    broadcast_room_stats,
    current_time_ms,
    debug_signal_log,
    detach_sid_from_tracking,
    emit_activity_log,
    emit_room_state_changed,
    enforce_room_capacity,
    ensure_protocol_version,
    get_all_room_states,
    get_client_from_sid,
    get_or_create_transfer_context,
    get_room_lan_state,
    get_serialized_sessions,
    instruct_finish,
    instruct_upload_relay,
    is_sender_authorized_for_room,
    normalize_client_type,
    parse_signal_payload,
    remove_client_from_room_order,
    resolve_signal_context,
    transfer_decision_timeout_worker,
    trigger_lan_probe_if_ready,
    update_client_network_meta,
    update_client_probe_meta,
    update_transfer_state,
)
from .socket_events import register_socket_events


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
register_user_loader(login_manager)

socketio = SocketIO(app, cors_allowed_origins='*')
bind_runtime(socketio, logger)

# Eagerly initialise FCM so startup errors surface immediately (non-fatal)
from .services.fcm_service import _ensure_initialized as _fcm_init
_fcm_init()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto',
    verify=False,
)

try:
    logger.info(f'Verifying R2 Connection to bucket: {R2_BUCKET_NAME}...')
    s3_client.head_bucket(Bucket=R2_BUCKET_NAME)
    logger.info('R2 Connection Successful!')
except Exception as e:
    logger.error(f'R2 Connection Failed: {e}')


def get_r2_bucket_usage_bound(bucket_name):
    return get_r2_bucket_usage(s3_client, bucket_name)


def empty_r2_bucket_bound(bucket_name):
    return empty_r2_bucket(s3_client, bucket_name)


register_routes(
    app,
    ADMIN_PASSWORD=ADMIN_PASSWORD,
    User=User,
    get_serialized_sessions=get_serialized_sessions,
    os=os,
    logger=logger,
    s3_client=s3_client,
    R2_BUCKET_NAME=R2_BUCKET_NAME,
    get_r2_bucket_usage=get_r2_bucket_usage_bound,
    DASHBOARD_R2_BUCKET=DASHBOARD_R2_BUCKET,
    empty_r2_bucket=empty_r2_bucket_bound,
    debug_signal_log=debug_signal_log,
    CLIENT_SESSIONS=CLIENT_SESSIONS,
    socketio=socketio,
    ALLOWED_ACTIVITY_TYPES=ALLOWED_ACTIVITY_TYPES,
    emit_activity_log=emit_activity_log,
    verify_password=verify_password,
    PASSWORD_HASH_FILE=PASSWORD_HASH_FILE,
)

register_socket_events(
    socketio,
    logger=logger,
    CLIENT_SESSIONS=CLIENT_SESSIONS,
    detach_sid_from_tracking=detach_sid_from_tracking,
    get_serialized_sessions=get_serialized_sessions,
    normalize_client_type=normalize_client_type,
    get_all_room_states=get_all_room_states,
    CLIENT_TYPES=CLIENT_TYPES,
    CLIENT_DEVICE_NAMES=CLIENT_DEVICE_NAMES,
    CLIENT_LAST_SEEN_MS=CLIENT_LAST_SEEN_MS,
    current_time_ms=current_time_ms,
    CLIENT_JOINED_AT_MS=CLIENT_JOINED_AT_MS,
    update_client_network_meta=update_client_network_meta,
    update_client_probe_meta=update_client_probe_meta,
    CLIENT_ROOMS=CLIENT_ROOMS,
    remove_client_from_room_order=remove_client_from_room_order,
    ROOM_LAST_PROBE=ROOM_LAST_PROBE,
    broadcast_room_stats=broadcast_room_stats,
    emit_room_state_changed=emit_room_state_changed,
    ROOM_CLIENT_ORDER=ROOM_CLIENT_ORDER,
    enforce_room_capacity=enforce_room_capacity,
    trigger_lan_probe_if_ready=trigger_lan_probe_if_ready,
    get_client_from_sid=get_client_from_sid,
    CLIENT_NETWORK_META=CLIENT_NETWORK_META,
    emit_activity_log=emit_activity_log,
    PENDING_LAN_PROBES=PENDING_LAN_PROBES,
    parse_signal_payload=parse_signal_payload,
    resolve_signal_context=resolve_signal_context,
    debug_signal_log=debug_signal_log,
    ensure_protocol_version=ensure_protocol_version,
    is_sender_authorized_for_room=is_sender_authorized_for_room,
    get_or_create_transfer_context=get_or_create_transfer_context,
    get_room_lan_state=get_room_lan_state,
    instruct_upload_relay=instruct_upload_relay,
    update_transfer_state=update_transfer_state,
    transfer_decision_timeout_worker=transfer_decision_timeout_worker,
    TRANSFER_CONTEXTS=TRANSFER_CONTEXTS,
    instruct_finish=instruct_finish,
)


__all__ = ['app', 'socketio']





