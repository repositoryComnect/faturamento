from flask import render_template, Blueprint, jsonify, request, redirect, url_for, session
from application.models.models import Vendedor, Revenda, db
from sqlalchemy import text
from datetime import datetime
import re

revendas_bp = Blueprint('revendas_bp', __name__)

@revendas_bp.route('/api/vendedores')
def api_vendedores():
    vendedores = Vendedor.query.filter_by(ativo=True).order_by(Vendedor.id).all()
    return jsonify([{'codigo': v.codigo, 'nome': v.nome} for v in vendedores])

@revendas_bp.route('/delete/revendas', methods=['POST'])
def delete_revendas():
    codigo = request.form.get('codigo')
    try:
        db.session.execute(text("DELETE FROM revendas WHERE codigo = :codigo"),
            {'codigo': codigo})
        db.session.commit()

    except Exception as e:
        print(f"Alerta: Não foi possível realizar a exclusão do produto: {str(e)}")
    
    return redirect(url_for(('home_bp.render_revendas')))

@revendas_bp.route('/set/revendas', methods=['POST'])
def set_revendas():
    empresa_id = session.get('empresa')
    try:
        revenda_data = {
            'codigo': request.form.get('codigo_revenda'),
            'nome': request.form.get('nome_revenda'),
            'id_conta': request.form.get('id_conta'),
            'tipo_conta': request.form.get('tipo_conta'),
            'status': request.form.get('status'),
            'cnpj': request.form.get('cnpj'),
            'telefone': request.form.get('telefone'),
            'email': request.form.get('email'),
            'ie': request.form.get('ie'),
            'cep': request.form.get('cep'),
            'endereco': request.form.get('endereco'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'empresa_id': empresa_id,
        }

        vendedor_id = request.form.get('vendedor_selecionado')
        nova_revenda = Revenda(**revenda_data)
        db.session.add(nova_revenda)
        db.session.commit()

        if vendedor_id:
            vendedor = Vendedor.query.get(int(vendedor_id))
            if vendedor:
                vendedor.revenda_id = nova_revenda.id
                db.session.commit()

        return redirect(url_for('home_bp.render_revendas'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar revenda: {str(e)}',
            'error_details': str(e)
        }), 500
   
@revendas_bp.route('/get/revendas', methods=['GET'])
def get_revendas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10  
        
        offset = (page - 1) * per_page
        resultado = db.session.execute(
            text("SELECT * FROM revendas ORDER BY nome LIMIT :limit OFFSET :offset"),
            {'limit': per_page, 'offset': offset}
        )
        
        revendas = [dict(row._mapping) for row in resultado]
        total = db.session.execute(text("SELECT COUNT(*) FROM revendas")).scalar()

        return render_template(
            'listar_revendas.html',
            revendas=revendas,
            page=page,
            per_page=per_page,
            total=total
        )

    except Exception as e:
        print(f"Erro ao listar revendas: {str(e)}")
        return render_template(
            'listar_revendas.html',
            revendas=[],
            page=1,
            per_page=10,
            total=0,
            error=f"Não foi possível carregar as revendas: {str(e)}"
        )

@revendas_bp.route('/get/id/revendas', methods=['GET'])
def get_id_revendas():
    search_term = request.args.get('search', '').strip()
    
    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    try:
        query = text("""
            SELECT * FROM revendas
            WHERE nome LIKE :term 
            OR codigo LIKE :term 
            OR cnpj LIKE :term
            """)

        result = db.session.execute(query, {'term': f'%{search_term}%'})
        revendas = [dict(row._asdict()) for row in result]

        # Acrescentando total, página e itens por página
        total = len(revendas)
        page = 1
        per_page = total  # ou defina um valor fixo, ex: 10

        return render_template(
            'listar_revendas.html',
            revendas=revendas,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500

@revendas_bp.route('/proximo_codigo_revenda', methods=['GET'])
def proximo_codigo_revenda():
    try:
        # Busca todas as revendas com código preenchido
        revendas = Revenda.query.with_entities(Revenda.codigo).all()

        numeros = []
        for rev in revendas:
            if rev.codigo:
                match = re.search(r'\d+', rev.codigo)
                if match:
                    numeros.append(int(match.group()))
        
        proximo = max(numeros) + 1 if numeros else 1
        codigo_formatado = f"R{proximo:04d}"  # Exemplo: R0001, R0002...

        return jsonify({'proximo_codigo_revenda': codigo_formatado})

    except Exception as e:
        print(f"Erro ao gerar código de revenda: {e}")
        return jsonify({'error': 'Erro ao gerar o próximo código de revenda'}), 500
