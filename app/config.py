import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # # SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///fcsm.db'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://bjgwuwmontdjxx:867570147e6ec9e0a17e4a6e98996354c3c4a4b73a46093f627f33e3cf24300c@ec2-44-208-206-97.compute-1.amazonaws.com:5432/d64vv023g375ce'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # STRIPE_PUBLIC_KEY = 'pk_test_51MmCv4Kr9xveA3fncXrGfjTAyE7kSZzdkir0Ardq5glAiX0Y5JuOyjpRCVsF5bgB2emOWgTgOwaQuSlGvtkFKJdJ00K7sRAnSr'
    # STRIPE_SECRET_KEY = 'sk_test_51MmCv4Kr9xveA3fnSEoa9FuoOGUW5W8XDpJ4Dz1ynpEyw3DCQrBiwIDSMDb7oMwplHKPZcA2KYGHqyS8r821agUT00tjpuKDmQ'
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")


    
