from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from modules.login.routes import login_bp
from modules.home.routes import home_bp
from modules.clientes.routes import cliente_bp
from modules.contratos.routes import contratos_bp
from modules.produtos.routes import produtos_bp
from modules.dashboard.routes import dashboard_bp
from modules.revendas.routes import revendas_bp
from modules.vendedores.routes import vendedores_bp
from modules.instalacoes.routes import instalacoes_bp
from flask_migrate import Migrate
from modules.planos.routes import planos_bp
from application.models.models import db, User
import os

# Inicializa o Flask app
app = Flask(__name__)

# Registre suas blueprints aqui

app.register_blueprint(login_bp)
app.register_blueprint(home_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(contratos_bp)
app.register_blueprint(planos_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(revendas_bp)
app.register_blueprint(vendedores_bp)
app.register_blueprint(instalacoes_bp)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%40Slink1205@localhost/faturamento'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Inicializa o db com o app
db.init_app(app)
migrate = Migrate(app, db)

# Inicialização do LoginManager
login_manager = LoginManager(app)

# Configuração do LoginManager
login_manager.login_view = 'login.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Criação do banco e usuário admin
with app.app_context():
    db.create_all()
    
    # Verifica se o usuário admin já existe
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
        app.run(host='0.0.0.0', port=9000, debug=True)
