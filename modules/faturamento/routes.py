from flask import Blueprint, jsonify, redirect, render_template, request, session
from datetime import datetime
from application.models.models import Contrato

faturamento_bp = Blueprint('faturamento_bp', __name__, url_prefix='/faturamento')

@faturamento_bp.route('/return/contratos', methods=['GET'])
def return_contratos():
    empresa_id = session.get('empresa')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # contratos por página

    contratos_paginados = Contrato.query.filter_by(estado_contrato="Ativo", empresa_id=empresa_id).order_by(Contrato.id.desc()).paginate(page=page, per_page=per_page)

    current_month = datetime.now().month
    current_year = datetime.now().year

    return render_template(
        'faturamento/faturamento.html',
        contratos=contratos_paginados.items,
        pagination=contratos_paginados,
        current_month=current_month,
        current_year=current_year
    )