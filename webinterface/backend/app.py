import os

from flask import Flask
from flask_cors import CORS
from scans import bp
app = Flask(__name__)
# The API receives AWS credentials: only accept calls from the local React app.
CORS(app, origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")])
os.makedirs('scans', exist_ok=True)
app.register_blueprint(bp, url_prefix='/scans')

if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=os.getenv("FLASK_DEBUG") == "1")