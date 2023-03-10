import os



class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://xxazizetlirofs:d391fd470610436ff0c3091be22724db7034cb636ed424d2794e7074a91cc302@ec2-34-226-11-94.compute-1.amazonaws.com:5432/dugtf9j1q681m'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'milanmartis@gmail.com'
    MAIL_PASSWORD = 'iighwhrmbkxxaazk'