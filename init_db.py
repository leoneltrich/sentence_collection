import time
from app import create_app
from app.models import db, Category

app = create_app()

def init_database():
    with app.app_context():
        # Attempt to create tables, handle connection delays from DB container
        max_retries = 5
        for i in range(max_retries):
            try:
                db.create_all()
                print("Database tables created successfully.")
                break
            except Exception as e:
                if i < max_retries - 1:
                    print(f"Database not ready, retrying in 2 seconds... ({e})")
                    time.sleep(2)
                else:
                    raise e

if __name__ == '__main__':
    init_database()