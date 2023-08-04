import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://bjgwuwmontdjxx:867570147e6ec9e0a17e4a6e98996354c3c4a4b73a46093f627f33e3cf24300c@ec2-44-208-206-97.compute-1.amazonaws.com:5432/d64vv023g375ce'
    MAIL_SERVER = 'smtp.m1.websupport.sk'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
        



    
