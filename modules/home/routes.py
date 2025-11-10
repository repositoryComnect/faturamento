from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash
from application.models.models import db, Contrato, Cliente, Plano, Produto, Vendedor, Empresa
from flask_login import login_required
from sqlalchemy import text, extract, func
from datetime import datetime

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/contratos', methods=['GET'])
@login_required
def render_contratos():
    empresa_id = session.get('empresa')
    try:
        contrato = db.session.execute(
            db.select(Contrato).filter_by(empresa_id=empresa_id).limit(1)
        ).scalar_one_or_none()

        return render_template('contratos.html', contrato=contrato)
        
    except Exception as e:
        print(f"Erro ao acessar contratos: {str(e)}")
        return render_template('contratos.html', contrato=None)

@home_bp.route('/clientes', methods=['GET'])
@login_required
def render_clientes():
    empresa_id = session.get('empresa')
    try:
        cliente = (
            Cliente.query
            .filter(
                Cliente.empresa_id == empresa_id,
                Cliente.estado_atual != 'Arquivado'
            )
            .first()
        )
      
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
    empresa_id = session.get('empresa')

    page = request.args.get('page', 1, type=int)
    per_page = 10 

    try:
        plano = db.session.execute(
            db.select(Plano).filter_by(empresa_id=empresa_id).limit(1)
        ).scalar_one_or_none()

        # Consulta paginada filtrada por empresa
        planos_paginados = Plano.query.filter_by(empresa_id=empresa_id)\
                                      .order_by(Plano.id)\
                                      .paginate(page=page, per_page=per_page, error_out=False)

        return render_template(
            'planos.html',
            plano=plano,
            planos=planos_paginados.items,
            pagination=planos_paginados
        )
    except Exception as e:
        print(f"Erro ao carregar planos: {str(e)}")
        return render_template('planos.html', plano=None, planos=[], pagination=None)

@home_bp.route('/ferramentas', methods=['GET'])
@login_required
def render_ferramentas():
    return render_template('ferramentas.html')

@home_bp.route('/produtos', methods=['GET'])
@login_required
def render_produtos():
    empresa_id = session.get('empresa')
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Itens por página
    
    # Consulta paginada com filtro por empresa
    produtos_paginados = Produto.query \
        .filter_by(empresa_id=empresa_id) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'produtos.html',
        produtos=produtos_paginados.items,
        pagination=produtos_paginados
    )

@home_bp.route('/revendas', methods=['GET'])
@login_required
def render_revendas():
    vendedores = Vendedor.query.filter_by(ativo=True).order_by(Vendedor.nome).all()
    return render_template('revendas.html', vendedores=vendedores)

@home_bp.route('/notas', methods=['GET'])
@login_required
def render_notas_fiscais():
    return render_template('notas.html')

@home_bp.route('/dashboard', methods=['GET'])
@login_required
def render_dashboard():
    return render_template('dashboard.html')

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

@home_bp.route('/trocar_empresa', methods=['POST'])
@login_required
def trocar_empresa():
    empresa_atual_id = session.get('empresa')

    # Busca todas as empresas ativas, ordenadas por ID
    empresas_ativas = Empresa.query.filter_by(status='ativo').order_by(Empresa.id).all()

    if not empresas_ativas:
        flash("Nenhuma empresa ativa encontrada.", "warning")
        return redirect(url_for('login.home'))

    # Lista só com os IDs das empresas
    ids_empresas = [str(emp.id) for emp in empresas_ativas]

    # Se a empresa atual está na lista, pega o próximo ID (ou o primeiro se for a última)
    if empresa_atual_id in ids_empresas:
        index_atual = ids_empresas.index(empresa_atual_id)
        proximo_index = (index_atual + 1) % len(ids_empresas)
        nova_empresa_id = ids_empresas[proximo_index]
    else:
        # Se empresa atual não está na lista, define a primeira da lista
        nova_empresa_id = ids_empresas[0]

    session['empresa'] = nova_empresa_id
    print(f"Empresa alterada para: {session['empresa']}")

    return redirect(url_for('login.home'))

@home_bp.route('/faturamento', methods=['GET'])
@login_required
def render_faturamento():
    empresa_id = session.get('empresa')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # contratos por página

    contratos_paginados = Contrato.query.filter_by(estado_contrato="Ativo", empresa_id=empresa_id).order_by(Contrato.id.desc()).paginate(page=page, per_page=per_page)

    current_month = datetime.now().month
    current_year = datetime.now().year

    return render_template(
        'faturamento.html',
        contratos=contratos_paginados.items,
        pagination=contratos_paginados,
        current_month=current_month,
        current_year=current_year
    )