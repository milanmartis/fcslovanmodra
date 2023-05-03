import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    # STRIPE_PUBLIC_KEY = 'pk_test_51MmCv4Kr9xveA3fncXrGfjTAyE7kSZzdkir0Ardq5glAiX0Y5JuOyjpRCVsF5bgB2emOWgTgOwaQuSlGvtkFKJdJ00K7sRAnSr'
    # STRIPE_SECRET_KEY = 'sk_test_51MmCv4Kr9xveA3fnSEoa9FuoOGUW5W8XDpJ4Dz1ynpEyw3DCQrBiwIDSMDb7oMwplHKPZcA2KYGHqyS8r821agUT00tjpuKDmQ'
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    



    
