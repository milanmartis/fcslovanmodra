import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()
engine = create_engine(
    os.getenv('SQLALCHEMY_DATABASE_URI'),
    pool_size=100,          # Nastavte veľkosť poolu
    max_overflow=20,       # Nastavte maximálny počet pripojení nad rámec poolu
    pool_timeout=30,       # Nastavte čas čakania na voľné pripojenie
    pool_recycle=3600      # Nastavte čas po ktorom sa pripojenie recykluje (v sekundách)
)

print("Pool size:", engine.pool.size())
print("Max overflow:", engine.pool._max_overflow)
print("Timeout:", engine.pool.timeout())


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=1440)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI =  os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_POOL_SIZE = 100  # Maximálny počet stálych pripojení
    SQLALCHEMY_MAX_OVERFLOW = 20  # Maximálny počet prekročených pripojení nad rámec pool_size
    SQLALCHEMY_POOL_TIMEOUT = 30  # Maximálna doba čakania na pripojenie, v sekundách
    SQLALCHEMY_POOL_RECYCLE = 300  # Interval v sekundách, po ktorom sa pripojenie obnoví
    # SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.m1.websupport.sk'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
    
    ASYNC_DATABASE_URL = os.getenv('ASYNC_DATABASE_URL')



    
