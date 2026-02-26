import os

from app import app, socketio


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    socketio.run(app, host='0.0.0.0', port=5055, debug=debug, use_reloader=False)
