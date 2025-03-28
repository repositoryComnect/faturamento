from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#from flask_pymongo import PyMongo  # Adicione esta linha

# Instâncias das extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Banco PostgreSQL para dados de negócio
#db_pg = SQLAlchemy()

