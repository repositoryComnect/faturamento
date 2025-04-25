from flask import Blueprint, jsonify, render_template, request
from application.models.models import db, Contrato, Cliente, Plano, Produto
from flask_login import login_required
from sqlalchemy import text, extract, func
from datetime import datetime


home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/api/chart_data')
def chart_data():
    try:
        # Exemplo para PostgreSQL (ajuste conforme seu banco de dados)
        cadastros_por_mes = db.session.query(
            extract('month', Contrato.cadastramento).label('month'),
            func.count(Contrato.id).label('count')
        ).group_by(
            extract('month', Contrato.cadastramento)
        ).order_by(
            extract('month', Contrato.cadastramento)
        ).all()
        
        # Mapear números de mês para nomes
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        
        # Preparar os dados para o gráfico
        data = [{
            "month": meses.get(int(month), "Desconhecido"),
            "count": count
        } for month, count in cadastros_por_mes]
        
        return jsonify(data)
        
    except Exception as e:
        print(f"Erro ao gerar dados do gráfico: {str(e)}")
        return jsonify({"error": "Erro ao gerar dados do gráfico"}), 500


@home_bp.route('/api/chart_pie')
def chart_pie():
    try:
        # Consulta para contar cadastros por status
        status_counts = db.session.query(
            Contrato.estado_contrato,
            func.count(Contrato.id).label('count')
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
def render_planos():
    planos = db.session.execute(db.select(Plano).limit(1)).scalar_one_or_none()
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Itens por página
    
    # Consulta paginada
    planos_paginados = Plano.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('planos.html', plano=planos, planos=planos_paginados.items, pagination=planos_paginados)




@home_bp.route('/ferramentas', methods=['GET'])
def render_titulos():
    return render_template('ferramentas.html')


@home_bp.route('/produtos', methods=['GET'])
def render_produtos():
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Itens por página
    
    # Consulta paginada
    produtos_paginados = Produto.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('produtos.html', produtos=produtos_paginados.items, pagination=produtos_paginados)



@home_bp.route('/comis_rev', methods=['GET'])
def render_comis_rev():
    return render_template('comis_rev.html')

@home_bp.route('/comis_resp', methods=['GET'])
def render_comis_resp():
    return render_template('comis_resp.html')

@home_bp.route('/dashboard_contratos', methods=['GET'])
@login_required
def render_dashboard():
    return render_template('dashboard_contratos.html')

@home_bp.route('/instalacoes', methods=['GET'])
def render_instalacoes():
    return render_template('instalacoes.html')

@home_bp.route('/equipamentos', methods=['GET'])
def render_equipamentos():
    return render_template('equipamentos.html')