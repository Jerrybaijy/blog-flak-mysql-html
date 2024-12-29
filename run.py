from app import create_app, db
import logging

logging.basicConfig(level=logging.INFO)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 