from app import app

if __name__ == "__main__":
    # This is used by WSGI servers like Gunicorn
    app = app
