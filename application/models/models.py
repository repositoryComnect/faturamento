from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Inicializa o db, que será importado no app.py
db = SQLAlchemy()

# Tabelas associativas N:N entre Cliente : (Contrato, Plano Produto e Instalações)
cliente_contrato = db.Table(
    'cliente_contrato',
    db.Column('cliente_id', db.Integer, db.ForeignKey('clientes.id'), primary_key=True),
    db.Column('contrato_id', db.Integer, db.ForeignKey('contratos.id'), primary_key=True)
)

# Tabelas associativas N:N entre Contrato : (Plano, Clientes, Produto)
contrato_plano = db.Table(
    'contrato_plano',
    db.Column('contrato_id', db.Integer, db.ForeignKey('contratos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('plano_id', db.Integer, db.ForeignKey('planos.id', ondelete='CASCADE'), primary_key=True)
)

# Enumerations
tipo_agrupamento_enum = ('contrato', 'produto', 'cliente', 'instalacao', 'cnpj')
tipo_faturamento_enum = (
    'individual_contrato', 'individual_cliente', 'individual_instalacao',
    'agrupado_contrato', 'agrupado_produto', 'agrupado_grupo_faturamento'
)
status_fatura_enum = ('pendente', 'pago', 'cancelado')

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cnpj = db.Column(db.String(18), unique=True)  # cnpj
    data_abertura = db.Column(db.Date)
    nome_empresa = db.Column(db.String(100))  # nome_empresa
    nome_fantasia = db.Column(db.String(100))  # nome_fantasia
    cod_desc_principal = db.Column(db.JSON)  # cod_desc_principal
    cod_desc_secundaria = db.Column(db.JSON)  # cod_desc_secundaria
    cod_desc_juridica = db.Column(db.JSON)  # cod_desc_juridica
    logradouro = db.Column(db.String(50))  # logradouro
    numero = db.Column(db.Integer)  # numero
    complemento = db.Column(db.String(50))  # complemento
    cep = db.Column(db.Integer)  # cep
    bairro = db.Column(db.String(30))  # bairro
    municipio = db.Column(db.String(30))  # municipio
    uf = db.Column(db.String(2))  # uf
    email = db.Column(db.String(50))
    telefone = db.Column(db.String(15))  # telefone
    status = db.Column(db.String(10))

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
    codigo = db.Column(db.String(100))
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True)
    ie = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    status = db.Column(db.String(10))
    id_conta = db.Column(db.Integer)
    tipo_conta = db.Column(db.String(20))
    cep = db.Column(db.String(20))
    bairro = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    # Relacionamento com Empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('revendas', lazy=True))

    # Relacionamentos internos
    vendedores = db.relationship('Vendedor', backref='revenda_associada', lazy=True)
    clientes = db.relationship('Cliente', backref='revenda_associada', lazy=True)

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(20))
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # Relacionamento com Revenda
    revenda_id = db.Column(db.Integer, db.ForeignKey('revendas.id'))
    
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    
    # Relacionamento com Empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('vendedores', lazy=True))
    
    # Relacionamento com Cliente
    clientes = db.relationship('Cliente', backref='vendedor', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Dados básicos
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
    cnpj_cpf = db.Column(db.String(18))
    ie = db.Column(db.String(20))
    im = db.Column(db.String(20))
    
    # Dados comerciais
    revenda_nome = db.Column(db.String(100))  
    vendedor_nome = db.Column(db.String(100))
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

    # Endereço Cobrança
    cep_cobranca = db.Column(db.String(15))
    endereco_cobranca = db.Column(db.String(255))
    cidade_cobranca = db.Column(db.String(100))
    telefone_cobranca = db.Column(db.String(20))
    bairro_cobranca = db.Column(db.String(100))
    uf_cobranca = db.Column(db.String(2))
    
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
    
    # Novo campo para número de contrato
    numero_contrato = db.Column(db.String(255))
    
    # Relacionamento com Empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('clientes', lazy=True))
    
    # 🔥 AJUSTE — Relacionamento 1 Cliente → N Contratos
    contratos = db.relationship(
        'Contrato',
        back_populates='cliente',
        lazy=True
    )

    instalacoes = db.relationship('Instalacao', back_populates='cliente', lazy=True)

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco_base = db.Column(db.Numeric(10, 2), default=0.00)
    ativo = db.Column(db.String(20))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    # Relacionamento com Empresa (padronizado)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('produtos', lazy=True))

    # Relacionamento com Contrato através da tabela de junção
    contratos = db.relationship(
        'Contrato',
        secondary='contratos_produtos',
        back_populates='produtos'
    )

class Contrato(db.Model):
    __tablename__ = 'contratos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cadastramento = db.Column(db.Date)
    atualizacao = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    id_matriz_portal = db.Column(db.String(50))
    cnpj_cpf = db.Column(db.String(20))
    tipo_pessoa = db.Column(db.String(40))
    revenda = db.Column(db.String(50))
    vendedor = db.Column(db.String(50))

    # Dados do cliente (snapshot)
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

    # Condições do contrato
    dia_vencimento = db.Column(db.Integer)
    fator_juros = db.Column(db.Numeric(5, 2))
    contrato_revenda = db.Column(db.Boolean, default=False)
    faturamento_contrato = db.Column(db.Boolean, default=False)
    estado_contrato = db.Column(db.String(30))
    data_estado = db.Column(db.Date)
    motivo_estado = db.Column(db.String(50))
    observacao = db.Column(db.String(100))

    # Empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('contratos', lazy=True))

    # Produto padrão
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=True)

    # NOVO — Cliente principal do contrato (1 Cliente → N Contratos)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    cliente = db.relationship('Cliente', back_populates='contratos', lazy=True)

    # Notas fiscais (1:N)
    notas_fiscais = db.relationship('NotaFiscal', backref='contrato', lazy=True)

    # Produtos do contrato (N:N)
    produtos = db.relationship(
        'Produto',
        secondary='contratos_produtos',
        back_populates='contratos'
    )

    # Planos do contrato (N:N)
    planos = db.relationship(
        'Plano',
        secondary=contrato_plano,
        back_populates='contratos',
        lazy=True
    )

    def __repr__(self):
        return f'<Contrato {self.id}>'

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
    
    codigo_instalacao = db.Column(db.String(10))
    razao_social = db.Column(db.String(50))
    cep = db.Column(db.String(50))
    endereco = db.Column(db.String(50))
    bairro = db.Column(db.String(20))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cadastramento = db.Column(db.Date)
    id_portal = db.Column(db.Integer)
    status = db.Column(db.String(20), default='ativo')
    observacao = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    # 🔹 Relacionamento com Empresa (nome de backref ajustado)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('instalacoes', lazy=True))

    # 🔹 Relacionamento com Cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cliente = db.relationship('Cliente', back_populates='instalacoes')

    # 🔹 Relacionamento com títulos
    titulos = db.relationship('TituloInstalacao', backref='instalacao', lazy=True)

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
     # 🔹 Relacionamento com Empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('notas_fiscais', lazy=True))
    
    produtos = db.relationship('Produto', secondary='produtos_notas', backref=db.backref('notas_fiscais', lazy=True))

class ProdutoNota(db.Model):
    __tablename__ = 'produtos_notas'
    
    nota_id = db.Column(db.Integer, db.ForeignKey('notas_fiscais.id'), primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), primary_key=True)
    quantidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Numeric(10, 2))
    desconto = db.Column(db.Numeric(5, 2), default=0)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('produtos_notas', lazy=True))

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
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('titulos_instalacoes', lazy=True))

class Plano(db.Model):
    __tablename__ = 'planos'
    
    # Dados Básicos
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False)  # name="codigo"
    nome = db.Column(db.String(200), nullable=False)  # name="nome"
    valor = db.Column(db.Numeric(10, 2), nullable=False)  # name="valor"
    id_portal = db.Column(db.Integer)  # name="id_produto"
    produto = db.Column(db.String(20))
    qtd_produto = db.Column(db.Integer)
    valor_base_produto = db.Column(db.Numeric(10, 2))

    # ===== SEÇÃO LICENÇA =====
    desc_boleto_licenca = db.Column(db.String(200))  # name="desc_boleto_licenca"
    licenca_valor = db.Column(db.Numeric(10, 2))  # (já existia)
    aliquota_sp_licenca = db.Column(db.Numeric(5, 2))  # name="aliquota_sp_licenca"
    cod_servico_sp_licenca = db.Column(db.String(20))  # name="cod_servico_sp_licenca"
    desc_nf_licenca = db.Column(db.String(200))  # name="desc_nf_licenca" (novo)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('planos', lazy=True))
    

    # Datas
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relacionamento N:N com Contratos
    contratos = db.relationship(
        'Contrato',
        secondary=contrato_plano,
        back_populates='planos',
        lazy=True
    )
    
    def __repr__(self):
        return f'<Plano {self.codigo} - {self.nome}>'
    
class FaturamentoGrupo(db.Model):
    __tablename__ = 'faturamento_grupo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    tipo_agrupamento = db.Column(db.Enum(*tipo_agrupamento_enum, name="tipo_agrupamento_enum"), nullable=False)
    data_criacao = db.Column(db.DateTime)
    empresa = db.Column(db.Integer)

class FaturamentoGrupoClientes(db.Model):
    __tablename__ = 'faturamento_grupo_clientes'
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('faturamento_grupo.id'))
    cliente_id = db.Column(db.Integer)
    empresa = db.Column(db.Integer)

class FaturamentoTipo(db.Model):
    __tablename__ = 'faturamento_tipo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.Enum(*tipo_faturamento_enum, name="tipo_faturamento_enum"), nullable=False)
    descricao = db.Column(db.Text)
    empresa = db.Column(db.Integer)

class FaturamentoVolumeRegra(db.Model):
    __tablename__ = 'faturamento_volume_regra'
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('faturamento_grupo.id'))
    quantidade_min = db.Column(db.Integer)
    quantidade_max = db.Column(db.Integer)
    preco_unitario = db.Column(db.Numeric(10, 2))
    desconto_percentual = db.Column(db.Numeric(5, 2))
    pro_rata = db.Column(db.Boolean, default=False)
    empresa = db.Column(db.Integer)

class FaturamentoTempoRegra(db.Model):
    __tablename__ = 'faturamento_tempo_regra'
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('faturamento_grupo.id'))
    periodo_inicio = db.Column(db.Date)
    periodo_fim = db.Column(db.Date)
    preco = db.Column(db.Numeric(10, 2))
    desconto_por_tempo = db.Column(db.Numeric(5, 2))
    pro_rata = db.Column(db.Boolean, default=False)
    empresa = db.Column(db.Integer)

class FaturamentoUsoRegra(db.Model):
    __tablename__ = 'faturamento_uso_regra'
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('faturamento_grupo.id'))
    descricao = db.Column(db.String(255))
    unidade_medida = db.Column(db.String(50))
    fracao_minima = db.Column(db.Numeric(5, 2))
    preco_por_unidade = db.Column(db.Numeric(10, 2))
    preco_por_fracao = db.Column(db.Numeric(10, 2))
    desconto = db.Column(db.Numeric(5, 2))
    empresa = db.Column(db.Integer)

class FormaPagamento(db.Model):
    __tablename__ = 'forma_pagamento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    empresa = db.Column(db.Integer)

class MetodoPagamento(db.Model):
    __tablename__ = 'metodo_pagamento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    detalhes_extras = db.Column(db.Text)
    empresa = db.Column(db.Integer)

class ContratoPagamentoConfig(db.Model):
    __tablename__ = 'contrato_pagamento_config'
    id = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('forma_pagamento.id'))
    metodo_pagamento_id = db.Column(db.Integer, db.ForeignKey('metodo_pagamento.id'))
    parcelas = db.Column(db.Integer)
    vencimento_dia = db.Column(db.Integer)
    empresa = db.Column(db.Integer)

class Fatura(db.Model):
    __tablename__ = 'fatura'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer)
    contrato_id = db.Column(db.Integer)
    periodo_inicio = db.Column(db.Date)
    periodo_fim = db.Column(db.Date)
    data_emissao = db.Column(db.Date)
    valor_total = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum(*status_fatura_enum, name="status_fatura_enum"))
    empresa = db.Column(db.Integer)

class FaturaItem(db.Model):
    __tablename__ = 'fatura_itens'
    id = db.Column(db.Integer, primary_key=True)
    fatura_id = db.Column(db.Integer, db.ForeignKey('fatura.id'))
    descricao = db.Column(db.String(255))
    tipo_faturamento = db.Column(db.Enum(*tipo_faturamento_enum, name="tipo_faturamento_enum"))
    quantidade = db.Column(db.Numeric(10, 2))
    valor_unitario = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    empresa = db.Column(db.Integer)
