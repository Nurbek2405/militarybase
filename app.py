from flask import Flask
from models import db
from routes import register_routes
from sqlalchemy.exc import OperationalError
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'

db.init_app(app)
register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            sys.exit(1)
    app.run(debug=True, host='0.0.0.0', port=8080)