import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://jjtebpcxjhphei:6e6471c9ed987cb9afad268cf13ef38a25c05e304c8a22656c5625b8cbb2aa57@ec2-3-208-74-199.compute-1.amazonaws.com:5432/d6rllm2kitp5nf'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'milanmartis@gmail.com'
    MAIL_PASSWORD = 'iighwhrmbkxxaazk'