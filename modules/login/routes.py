from flask import Blueprint, request, render_template, redirect, flash, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required
from settings.extensions import db
from application.models.models import User, Empresa
import bcrypt
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)
# Crie o objeto admin

## ------------------------------------------- Bloco Rotas Login -------------------------------------------------------------------------------------------- ##

@login_bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('dashboard.html')


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado!', 'danger')
            return redirect(url_for('authenticate.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('authenticate.login'))

    return render_template('register.html')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        empresa = request.form.get('empresa')

        print(f"Tentando fazer login com: {username} e senha: {password}")

        # Busca o usuário no banco de dados
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"Usuário encontrado: {username}")
        else:
            print(f"Usuário {username} não encontrado no banco de dados.")

        # Verifique se a senha armazenada no banco corresponde à senha fornecida
        if user and user.password == password:
            print(f"Senha correta para o usuário {username}. Login bem-sucedido.")
            login_user(user)  # Autentica o usuário

            # Armazena o nome de usuário na sessão
            session['username'] = user.username
            session['empresa'] = empresa  # ID da empresa fica armazenado aqui

            print(f"Empresa ID armazenado na session: {empresa}")

            # Redireciona para a página inicial (home)
            return redirect(url_for('login.home'))  # Redireciona para a rota 'home'
        else:
            print("Credenciais inválidas ou senha incorreta.")
            flash('Credenciais inválidas. Tente novamente.', 'danger')  # Exibe mensagem de erro

    return render_template('login.html')  # Renderiza o template de login

@login_bp.route('/getEmpresa', methods=['GET'])
def get_empresa():
    try:
        # Busca todas as empresas ativas
        empresas = Empresa.query.filter_by(status='ativo').all()
        
        # Formata os dados para JSON
        empresas_data = []
        for empresa in empresas:
            empresas_data.append({
                'id': empresa.id,
                'nome_fantasia': empresa.nome_fantasia,
                'nome_empresa': empresa.nome_empresa,
                'cnpj': empresa.cnpj
            })
        
        return jsonify(empresas_data)
    
    except Exception as e:
        print(f"Erro ao buscar empresas: {e}")
        return jsonify([]), 500
    
@login_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('username', None)  # Remover o 'username' da sessão, se existir
    logout_user()
    return render_template('login.html')


