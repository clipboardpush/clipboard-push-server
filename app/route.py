import time as pytime

from flask import request, jsonify, render_template, redirect, url_for, flash, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash


def register_routes(
    app,
    *,
    ADMIN_PASSWORD,
    User,
    get_serialized_sessions,
    os,
    logger,
    s3_client,
    R2_BUCKET_NAME,
    get_r2_bucket_usage,
    DASHBOARD_R2_BUCKET,
    empty_r2_bucket,
    debug_signal_log,
    CLIENT_SESSIONS,
    socketio,
    ALLOWED_ACTIVITY_TYPES,
    emit_activity_log,
    verify_password,
    PASSWORD_HASH_FILE,
):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            if verify_password(password):
                user = User('admin')
                login_user(user, remember=remember)
                return redirect(url_for('dashboard'))

            flash('Invalid password')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', client_sessions=get_serialized_sessions())

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return "Clipboard Push Relay Server is Running (Port 5055). <a href='/login'>Login</a>"

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.png',
            mimetype='image/vnd.microsoft.icon',
        )

    @app.route('/change_password', methods=['POST'])
    @login_required
    def change_password():
        current = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not verify_password(current):
            flash('Current password is incorrect.')
            return redirect(url_for('dashboard'))

        if new_pw != confirm:
            flash('New password and confirmation do not match.')
            return redirect(url_for('dashboard'))

        if len(new_pw) < 8:
            flash('New password must be at least 8 characters.')
            return redirect(url_for('dashboard'))

        new_hash = generate_password_hash(new_pw)
        hash_dir = os.path.dirname(PASSWORD_HASH_FILE)
        os.makedirs(hash_dir, exist_ok=True)
        with open(PASSWORD_HASH_FILE, 'w', encoding='utf-8') as f:
            f.write(new_hash)

        logger.info('Admin password changed successfully.')
        flash('Password changed successfully.')
        return redirect(url_for('dashboard'))

    @app.route('/api/dashboard/r2_usage', methods=['GET'])
    @login_required
    def api_dashboard_r2_usage():
        try:
            usage = get_r2_bucket_usage(DASHBOARD_R2_BUCKET)
            usage['updated_at_epoch_ms'] = int(pytime.time() * 1000)
            return jsonify(usage)
        except Exception as e:
            logger.error(f"Failed to get R2 usage for dashboard: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/dashboard/r2_empty', methods=['POST'])
    @login_required
    def api_dashboard_r2_empty():
        try:
            result = empty_r2_bucket(DASHBOARD_R2_BUCKET)
            usage = get_r2_bucket_usage(DASHBOARD_R2_BUCKET)
            return jsonify(
                {
                    'result': result,
                    'usage': usage,
                    'updated_at_epoch_ms': int(pytime.time() * 1000),
                }
            )
        except Exception as e:
            logger.error(f"Failed to empty R2 bucket for dashboard: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/file/upload_auth', methods=['POST'])
    def generate_upload_url():
        data = request.json
        filename = data.get('filename')
        content_type = data.get('content_type', 'application/octet-stream')

        if not filename:
            return jsonify({'error': 'Filename required'}), 400

        object_name = f"{int(pytime.time())}_{filename}"

        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': R2_BUCKET_NAME,
                    'Key': object_name,
                    'ContentType': content_type,
                },
                ExpiresIn=300,
            )

            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': R2_BUCKET_NAME, 'Key': object_name},
                ExpiresIn=3600,
            )

            return jsonify(
                {
                    'upload_url': presigned_url,
                    'download_url': download_url,
                    'file_key': object_name,
                    'expires_in': 300,
                }
            )
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/relay', methods=['POST'])
    def relay_message():
        try:
            content = request.json
            room = content.get('room')
            event = content.get('event')
            data = content.get('data')
            sender_id = content.get('sender_id') or content.get('client_id')

            debug_signal_log('http_rx', content, room=room, event=event, sender=sender_id, sid='http')

            if not room or not event or data is None:
                return jsonify({'error': 'Missing room, event, or data'}), 400

            skip_sids = []
            if sender_id and sender_id in CLIENT_SESSIONS:
                skip_sids = list(CLIENT_SESSIONS[sender_id])
                logger.info(f"Skipping sids for sender {sender_id}: {skip_sids}")

            if skip_sids:
                socketio.emit(event, data, room=room, skip_sid=skip_sids)
            else:
                socketio.emit(event, data, room=room)

            debug_signal_log('http_tx', data, room=room, event=event, sender=sender_id or 'API', sid='http')
            logger.info(f"Relayed HTTP message to room {room}: event={event}, skipped={len(skip_sids)}")

            activity_type = event if event in ALLOWED_ACTIVITY_TYPES else 'api_relay'
            emit_activity_log(activity_type, room, sender_id or 'API', f"Event: {event}")

            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            logger.error(f"Relay error: {e}")
            return jsonify({'error': str(e)}), 500
