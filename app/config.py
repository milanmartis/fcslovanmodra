import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://poktwcytjzkyew:5bdb99586baef51b1216188e45bb88c9e1af011a78e3a6d609e4938c2f60002a@ec2-52-23-81-126.compute-1.amazonaws.com:5432/db3uoc7j05udub'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'milanmartis@gmail.com'
    MAIL_PASSWORD = 'iighwhrmbkxxaazk'