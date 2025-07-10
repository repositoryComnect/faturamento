from flask import Blueprint, jsonify, render_template, request
from application.models.models import db, Contrato, Cliente, Plano, Produto, Vendedor
from flask_login import login_required
from sqlalchemy import text, extract, func
from datetime import datetime

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/contratos', methods=['GET'])
@login_required
def render_contratos():
    try:
        contrato = db.session.execute(db.select(Contrato).limit(1)).scalar_one_or_none()
        if contrato:
            return render_template('contratos.html', contrato=contrato)
        else:
            return render_template('contratos.html', contrato=None)
        
    except Exception as e:
        print(f"Erro ao acessar contratos: {str(e)}")
        return render_template('contratos.html', contrato=None)
    
@home_bp.route('/clientes', methods=['GET'])
@login_required
def render_clientes():
    try:
        # Usando a nova sintaxe do SQLAlchemy 2.0
        cliente = Cliente.query.first()        
        if cliente:
            return render_template('clientes.html', cliente=cliente)
        else:
            return render_template('clientes.html', cliente=None)
    except Exception as e:
        print(f"Erro ao acessar clientes: {str(e)}")
        return render_template('clientes.html', cliente=None)

@home_bp.route('/planos', methods=['GET'])
@login_required
def render_planos():
    planos = db.session.execute(db.select(Plano).limit(1)).scalar_one_or_none()
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Itens por página
    
    # Consulta paginada
    planos_paginados = Plano.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('planos.html', plano=planos, planos=planos_paginados.items, pagination=planos_paginados)

@home_bp.route('/ferramentas', methods=['GET'])
@login_required
def render_ferramentas():
    return render_template('ferramentas.html')

@home_bp.route('/produtos', methods=['GET'])
@login_required
def render_produtos():
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Itens por página
    
    # Consulta paginada
    produtos_paginados = Produto.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('produtos.html', produtos=produtos_paginados.items, pagination=produtos_paginados)

@home_bp.route('/revendas', methods=['GET'])
@login_required
def render_revendas():
    vendedores = Vendedor.query.filter_by(ativo=True).order_by(Vendedor.nome).all()
    return render_template('revendas.html', vendedores=vendedores)

@home_bp.route('/notas', methods=['GET'])
@login_required
def render_notas_fiscais():
    return render_template('notas.html')

@home_bp.route('/dashboard_contratos', methods=['GET'])
@login_required
def render_dashboard():
    return render_template('dashboard_contratos.html')

@home_bp.route('/vendedores', methods=['GET'])
@login_required
def render_vendedores():
    return render_template('vendedores.html')

@home_bp.route('/titulos', methods=['GET'])
@login_required
def render_titulos():
    return render_template('titulos.html')

@home_bp.route('/instalacoes', methods=['GET'])
@login_required
def render_instalacoes():
    return render_template('instalacoes.html')

@home_bp.route('/faturamento', methods=['GET'])
@login_required
def render_faturamento():
    return render_template('faturamento.html')