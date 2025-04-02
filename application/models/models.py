# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inicializa o db, que será importado no app.py
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Revenda(db.Model):
    __tablename__ = 'revendas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    razao_social = db.Column(db.String(100), nullable=False)
    nome_fantasia = db.Column(db.String(100))
    cnpj = db.Column(db.String(18), unique=True)
    ie = db.Column(db.String(20))
    im = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    
    vendedores = db.relationship('Vendedor', backref='revenda_associada', lazy=True)
    clientes = db.relationship('Cliente', backref='vendedor_associado', lazy=True)

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    revenda_id = db.Column(db.Integer, db.ForeignKey('revendas.id'))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    
    clientes = db.relationship('Cliente', backref='vendedor', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
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
    tipo = db.Column(db.String(30))
    cnpj = db.Column(db.String(18))
    ie = db.Column(db.String(20))
    im = db.Column(db.String(20))
    
    # Dados comerciais
    revenda_nome = db.Column(db.String(100))  
    vendedor_nome = db.Column(db.String(100))  # Renomeado para evitar conflito
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
    
    # Endereço de cobrança
    cobranca_cep = db.Column(db.String(10))
    cobranca_endereco = db.Column(db.String(200))
    cobranca_complemento = db.Column(db.String(100))
    cobranca_bairro = db.Column(db.String(100))
    cobranca_cidade = db.Column(db.String(100))
    cobranca_estado = db.Column(db.String(2))
    cobranca_tipo = db.Column(db.String(50))
    
    # Condições comerciais
    cliente_revenda = db.Column(db.Boolean, default=False)
    fator_juros = db.Column(db.Numeric(5, 2))
    estado_atual = db.Column(db.String(30))
    data_estado = db.Column(db.Date)
    
    # Plano
    plano_nome = db.Column(db.String(100))
    dia_vencimento = db.Column(db.Integer)
    motivo_estado = db.Column(db.String(200))
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'))
    revenda_id = db.Column(db.Integer, db.ForeignKey('revendas.id'))
    observacao = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    
    contratos = db.relationship('Contrato', backref='cliente', lazy=True)
    instalacoes = db.relationship('Instalacao', backref='cliente', lazy=True)

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco_base = db.Column(db.Numeric(10, 2))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

class Contrato(db.Model):
    __tablename__ = 'contratos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Dados básicos
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cadastramento = db.Column(db.Date)
    atualizacao = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    id_matriz_portal = db.Column(db.String(50))
    responsavel = db.Column(db.String(100))
    
    # Dados do cliente
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
    estado_contrato = db.Column(db.String(30))
    data_estado = db.Column(db.Date)
    motivo_estado = db.Column(db.String(200))
    
    # Relacionamentos
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    produtos = db.relationship('Produto', secondary='contratos_produtos', backref=db.backref('contratos', lazy=True))
    instalacoes = db.relationship('Instalacao', backref='contrato', lazy=True)
    notas_fiscais = db.relationship('NotaFiscal', backref='contrato', lazy=True)

class ContratoProduto(db.Model):
    __tablename__ = 'contratos_produtos'
    
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'), primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), primary_key=True)
    quantidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Numeric(10, 2))
    desconto = db.Column(db.Numeric(5, 2), default=0)

class Instalacao(db.Model):
    __tablename__ = 'instalacoes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'))
    numero_serie = db.Column(db.String(50))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    data_instalacao = db.Column(db.Date)
    data_retirada = db.Column(db.Date)
    status = db.Column(db.String(20), default='ativo')
    observacao = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    
    titulos = db.relationship('TituloInstalacao', backref='instalacao', lazy=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))

class NotaFiscal(db.Model):
    __tablename__ = 'notas_fiscais'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'))
    numero = db.Column(db.String(50), unique=True, nullable=False)
    serie = db.Column(db.String(10))
    data_emissao = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='pendente')
    chave_acesso = db.Column(db.String(50))
    xml = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    
    produtos = db.relationship('Produto', secondary='produtos_notas', backref=db.backref('notas_fiscais', lazy=True))

class ProdutoNota(db.Model):
    __tablename__ = 'produtos_notas'
    
    nota_id = db.Column(db.Integer, db.ForeignKey('notas_fiscais.id'), primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), primary_key=True)
    quantidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Numeric(10, 2))
    desconto = db.Column(db.Numeric(5, 2), default=0)

class TituloInstalacao(db.Model):
    __tablename__ = 'titulos_instalacoes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instalacao_id = db.Column(db.Integer, db.ForeignKey('instalacoes.id'))
    numero_parcela = db.Column(db.Integer)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date)
    status = db.Column(db.String(20), default='pendente')
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())