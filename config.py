import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'random-hardcoded-string-102839yr1ewqouir0178f290ashg98pzhaf087dshg0'
