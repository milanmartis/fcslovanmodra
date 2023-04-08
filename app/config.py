import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    # SQLALCHEMY_DATABASE_URI = 'postesql://bjgwuwmontdjxx:867570147e6ec9e0a17e4a6e98996354c3c4a4b73a46093f627f33e3cf24300c@ec2-44-208-206-97.compute-1.amazonaws.com:5432/d64vv023g375ce'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'milanmartis@gmail.com'
    MAIL_PASSWORD = 'iighwhrmbkxxaazk'