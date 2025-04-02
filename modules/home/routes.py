from flask import Blueprint, jsonify, render_template
from application.models.models import db, Contrato
from flask_login import login_required


home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/api/chart_data')
def chart_data():
    data = [
        {"month": "January", "sales": 50},
        {"month": "February", "sales": 75},
        {"month": "March", "sales": 90},
        {"month": "April", "sales": 100},
        {"month": "May", "sales": 125},
        {"month": "June", "sales": 150}
    ]
    return jsonify(data)

@home_bp.route('/contratos', methods=['GET'])
@login_required
def render_contratos():
    try:
        # Usando a nova sintaxe do SQLAlchemy 2.0
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
    return render_template('clientes.html')

@home_bp.route('/instalacoes', methods=['GET'])
def render_instalacoes():
    return render_template('instalacoes.html')

@home_bp.route('/equipamentos', methods=['GET'])
def render_equipamentos():
    return render_template('equipamentos.html')

@home_bp.route('/planos', methods=['GET'])
def render_planos():
    return render_template('planos.html')

@home_bp.route('/cobranca', methods=['GET'])
def render_cobranca():
    return render_template('cobranca.html')

@home_bp.route('/titulos', methods=['GET'])
def render_titulos():
    return render_template('titulos.html')

@home_bp.route('/comis_rev', methods=['GET'])
def render_comis_rev():
    return render_template('comis_rev.html')

@home_bp.route('/comis_resp', methods=['GET'])
def render_comis_resp():
    return render_template('comis_resp.html')

@home_bp.route('/dashboard', methods=['GET'])
@login_required
def render_dashboard():
    return render_template('dashboard.html')