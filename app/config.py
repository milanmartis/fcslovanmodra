import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://bjgwuwmontdjxx:867570147e6ec9e0a17e4a6e98996354c3c4a4b73a46093f627f33e3cf24300c@ec2-44-208-206-97.compute-1.amazonaws.com:5432/d64vv023g375ce'
    MAIL_SERVER = 'smtp.m1.websupport.sk'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'info@fcslovanmodra.sk'
    MAIL_PASSWORD = 'Hq5]Mp4J+T'

    STRIPE_PUBLIC_KEY = 'pk_live_51MmCv4Kr9xveA3fnFTeRJrHFsS7Iz2k2MzPXuWQAOEwOQX7Mg8NTJs8ZnrmXvTgXn9j9Co6RUu5HXu90tgaC6JaL00bFQcpTEJ'
    STRIPE_SECRET_KEY = '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'
        



    
