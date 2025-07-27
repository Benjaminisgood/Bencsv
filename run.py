# run.py
import argparse
from app import create_app

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask app with custom port.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask app on (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host IP (default: 127.0.0.1)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)