# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inicializa o db, que será importado no app.py
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Modelo Cliente (PostgreSQL)
class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados básicos
    numero_contato = db.Column(db.String(20))
    sequencia = db.Column(db.String(20))
    cadastramento = db.Column(db.Date)
    atualizacao = db.Column(db.Date)
    razao_social = db.Column(db.String(100), nullable=False)
    nome_fantasia = db.Column(db.String(100))
    contato_principal = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    
    # Dados jurídicos
    tipo = db.Column(db.String(30))  # Pessoa Jurídica/Física
    cnpj = db.Column(db.String(18))
    ie = db.Column(db.String(20))
    im = db.Column(db.String(20))
    
    # Dados comerciais
    revenda = db.Column(db.String(100))
    vendedor = db.Column(db.String(100))
    tipo_servico = db.Column(db.String(50))
    localidade = db.Column(db.String(50))
    regiao = db.Column(db.String(50))
    atividade = db.Column(db.String(50))
    
    # Endereço
    cep = db.Column(db.String(10))
    endereco = db.Column(db.String(200))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    
    # Endereço de cobrança (separado)
    cobranca_cep = db.Column(db.String(10))
    cobranca_endereco = db.Column(db.String(200))
    cobranca_complemento = db.Column(db.String(100))
    cobranca_bairro = db.Column(db.String(100))
    cobranca_cidade = db.Column(db.String(100))
    cobranca_estado = db.Column(db.String(2))
    cobranca_tipo = db.Column(db.String(50))  # Igual/Diferente
    
    # Condições comerciais
    cliente_revenda = db.Column(db.Boolean, default=False)
    fator_juros = db.Column(db.Numeric(5, 2))
    estado_atual = db.Column(db.String(30))  # ATIVO/CANCELADO
    data_estado = db.Column(db.Date)
    
    # Plano
    plano_nome = db.Column(db.String(100))
    dia_vencimento = db.Column(db.Integer)
    motivo_estado = db.Column(db.String(200))
    
    # Relacionamentos
    contratos = db.relationship('Contrato', backref='cliente', lazy=True)
    instalacoes = db.relationship('Instalacao', backref='cliente', lazy=True)

# Modelo Contrato (PostgreSQL)
class Contrato(db.Model):
    __tablename__ = 'contratos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados básicos
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cadastramento = db.Column(db.Date)
    atualizacao = db.Column(db.Date)
    tipo = db.Column(db.String(50))  # Hardware/Software/etc
    id_matriz_portal = db.Column(db.String(50))
    responsavel = db.Column(db.String(100))
    
    # Dados do cliente (redundantes para facilitar consultas)
    razao_social = db.Column(db.String(100))
    nome_fantasia = db.Column(db.String(100))
    contato = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    
    # Endereço
    cep = db.Column(db.String(10))
    endereco = db.Column(db.String(200))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    
    # Endereço de cobrança
    cobranca_cep = db.Column(db.String(10))
    cobranca_endereco = db.Column(db.String(200))
    cobranca_complemento = db.Column(db.String(100))
    cobranca_bairro = db.Column(db.String(100))
    cobranca_cidade = db.Column(db.String(100))
    cobranca_estado = db.Column(db.String(2))
    
    # Condições do contrato
    dia_vencimento = db.Column(db.Integer)
    fator_juros = db.Column(db.Numeric(5, 2))
    contrato_revenda = db.Column(db.Boolean, default=False)
    faturamento_contrato = db.Column(db.Boolean, default=False)
    estado_contrato = db.Column(db.String(30))  # ATIVO/CANCELADO
    data_estado = db.Column(db.Date)
    motivo_estado = db.Column(db.String(200))
    
    # Relacionamentos
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    planos = db.relationship('PlanoContrato', backref='contrato', lazy=True)

# Tabelas auxiliares
class Instalacao(db.Model):
    __tablename__ = 'instalacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_serie = db.Column(db.String(50))
    data_cadastramento = db.Column(db.Date)
    data_instalacao = db.Column(db.Date)
    data_retirada = db.Column(db.Date)
    data_substituicao = db.Column(db.Date)
    plano_nome = db.Column(db.String(100))
    estado_atual = db.Column(db.String(30))
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))

class PlanoContrato(db.Model):
    __tablename__ = 'planos_contrato'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    valor_plano = db.Column(db.Numeric(10, 2))
    valor_contrato = db.Column(db.Numeric(10, 2))
    
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'))