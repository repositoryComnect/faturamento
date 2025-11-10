from flask import Blueprint, jsonify, render_template, request, session
from application.models.models import db, Contrato, Cliente, Plano, Produto
from flask_login import login_required
from sqlalchemy import text, extract, func
from datetime import datetime

dashboard_bp = Blueprint('dashboard_bp', __name__)


@dashboard_bp.route('/contratosChart')
def contratosChart():
    empresa_id = session.get('empresa')
    try:
        engine = db.get_engine()
        engine_name = engine.dialect.name

        # Função para extrair mês dependendo do banco
        if engine_name == 'sqlite':
            month_func = db.func.strftime('%m', Contrato.cadastramento)
        elif engine_name == 'postgresql':
            month_func = db.func.extract('month', Contrato.cadastramento)
        else:  # mysql, mariadb, etc.
            month_func = db.func.month(Contrato.cadastramento)

        # Query: contar contratos por mês e status
        cadastros = db.session.query(
            month_func.label('month'),
            Contrato.estado_contrato.label('status'),
            db.func.count(Contrato.id).label('count')
        ).filter(
            Contrato.cadastramento != None,
            Contrato.empresa_id == empresa_id
        ).group_by('month', 'status').order_by('month').all()

        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        # Organiza os dados por mês
        data_dict = {}
        for month, status, count in cadastros:
            month_name = meses.get(int(month), "Desconhecido")
            if month_name not in data_dict:
                data_dict[month_name] = {'ativo': 0, 'suspenso': 0, 'cancelado': 0}
            data_dict[month_name][status.lower()] = count

        # Transformar em lista para JS
        data = []
        for month_name, counts in data_dict.items():
            data.append({
                'month': month_name,
                'ativo': counts.get('ativo', 0),
                'suspenso': counts.get('suspenso', 0),
                'cancelado': counts.get('cancelado', 0)
            })

        return jsonify(data)

    except Exception as e:
        import traceback
        erro_detalhado = traceback.format_exc()
        print(erro_detalhado)
        return jsonify({"error": str(e), "trace": erro_detalhado}), 500





@dashboard_bp.route('/statusChart')
def statusChart():
    empresa_id = session.get('empresa')
    try:
        # Consulta para contar cadastros por status
        status_counts = db.session.query(
            Contrato.estado_contrato,
            func.count(Contrato.id).label('count')).filter(
                Contrato.empresa_id == empresa_id,
        ).group_by(
            Contrato.estado_contrato
        ).all()
        
        # Mapear os dados para o formato esperado pelo gráfico
        data = []
        status_mapping = {
            'ativo': 'Ativos',
            'suspenso': 'Suspensos',
            'bloqueado': 'Bloqueados'
            # Adicione outros status conforme necessário
        }
        
        for status, count in status_counts:
            status_name = status_mapping.get(status.lower(), status.capitalize())
            data.append({
                'status': status_name,
                'count': count,
                #'color': get_color_for_status(status.lower())
            })
        
        return jsonify(data)
        
    except Exception as e:
        print(f"Erro ao gerar dados do gráfico de pizza: {str(e)}")
        return jsonify({"error": "Erro ao gerar dados do gráfico"}), 500