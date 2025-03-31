class Config:
    # Server settings
    HOST = "0.0.0.0"
    PORT = 58353
    RELOAD = True

    # API settings
    TITLE = "Codeforces Stats API"
    DESCRIPTION = "A FastAPI app for the Codeforces Stats"
    VERSION = "1.0.0"

    # Environment settings
    ENV = "production"  # or "development"
    
    @classmethod
    def is_dev(cls):
        return cls.ENV == "development"

    @classmethod
    def get_host(cls):
        return cls.HOST if cls.is_dev() else "127.0.0.1"
    
    @classmethod
    def get_port(cls):
        return cls.PORT if cls.is_dev() else 8000
