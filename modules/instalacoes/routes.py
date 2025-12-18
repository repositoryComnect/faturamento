from flask import Blueprint, jsonify, request, redirect, url_for, flash, render_template, session
from application.models.models import Instalacao, db
from datetime import datetime, date
import re
from modules.instalacoes.utils import parse_date
from sqlalchemy import text


instalacoes_bp = Blueprint('instalacoes_bp', __name__)

@instalacoes_bp.route('/insert/instalacoes', methods=['POST'])
def insert_instalacoes():
    empresa_id = session.get('empresa')
    form_data = request.form.to_dict()

    cliente_id = form_data.get('cliente_selecionado_instalacao')

    instalacao_data = {
        'codigo_instalacao': form_data.get('cod_instalacao'),
        'razao_social': form_data.get('company'),  
        'id_portal': form_data.get('id_portal'),
        'cadastramento': parse_date(form_data.get('cadastramento_instalacao')),  
        'status': form_data.get('status'),
        'cep': form_data.get('cep'),
        'cidade': form_data.get('cidade'),
        'endereco': form_data.get('endereco'),
        'bairro': form_data.get('bairro'),
        'uf': form_data.get('uf'),
        'observacao': form_data.get('observacao'),
        'cliente_id': int(cliente_id),
        'empresa_id': empresa_id
    }

    if Instalacao.query.filter_by(
        codigo_instalacao=instalacao_data['codigo_instalacao']
    ).first():
        return jsonify({
            'success': False,
            'message': 'Já existe uma instalação com este código.'
        }), 400

    nova_instalacao = Instalacao(**instalacao_data)
    db.session.add(nova_instalacao)
    db.session.commit()

    return redirect(url_for('home_bp.render_instalacoes'))

@instalacoes_bp.route('/proximo_codigo_instalacao', methods=['GET'])
def proximo_codigo_instalacao():
    instalacoes = Instalacao.query.all()
    
    numeros = []
    for inst in instalacoes:
        # Extrai o número do código instalacao, assumindo padrão com dígitos
        match = re.search(r'\d+', inst.codigo_instalacao)
        if match:
            numeros.append(int(match.group()))
    
    proximo = max(numeros) + 1 if numeros else 1
    codigo_formatado = f"I{proximo:04d}"  # ex: I0001, I0002
    
    return jsonify({'proximo_codigo_instalacao': codigo_formatado})

@instalacoes_bp.route('/delete/instalacoes', methods=['POST'])
def delete_instalacao():
    codigo = request.form.get('delete_codigo_instalacao')
    
    if not codigo:
        flash("Código da instalação não fornecido.", "danger")
        return redirect(request.referrer or url_for('instalacoes_bp.listar_instalacoes'))
    
    instalacao = Instalacao.query.filter_by(codigo_instalacao=codigo).first()
    
    if not instalacao:
        flash(f"Instalação com código {codigo} não encontrada.", "warning")
        return redirect(request.referrer or url_for('instalacoes_bp.listar_instalacoes'))
    
    try:
        db.session.delete(instalacao)
        db.session.commit()
        flash(f"Instalação {codigo} excluída com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir instalação: {str(e)}", "danger")
    
    return redirect(request.referrer or url_for('instalacoes_bp.listar_instalacoes'))

@instalacoes_bp.route('/get/instalacoes', methods=['GET'])
def get_instalacoes():
    empresa_id = session.get('empresa')
    search_term = request.args.get('search', '').strip()

    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido', 'sucesso': False}), 400

    try:
        query = text("""
            SELECT * FROM instalacoes
            WHERE empresa_id = :empresa_id
                AND (
                    codigo_instalacao LIKE :term 
                    OR razao_social LIKE :term
                )
            ORDER BY codigo_instalacao
        """)

        result = db.session.execute(query, {
            'term': f'%{search_term}%',
            'empresa_id': empresa_id
        })

        instalacoes = []
        for row in result:
            inst = dict(row._mapping)
            
            if isinstance(inst.get("cadastramento"), (date, datetime)):
                inst["cadastramento"] = inst["cadastramento"].strftime("%d/%m/%Y")

            instalacoes.append(inst)

        if not instalacoes:
            return jsonify({'erro': 'Nenhuma instalação encontrada para esse termo.', 'sucesso': False}), 200

        return jsonify({
            'sucesso': True,
            'instalacoes': instalacoes
        }), 200

    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500

@instalacoes_bp.route('/get/instalacoes/vinculo', methods=['GET'])
def get_instalacoes_vinculo():
    empresa_id = session.get('empresa')

    try:
        instalacoes = (
            Instalacao.query
            .filter(
                Instalacao.empresa_id == empresa_id,
                Instalacao.status == 'ativo'
            )
            .order_by(Instalacao.codigo_instalacao)
            .all()
        )

        dados = [
            {
                'id': inst.id,
                'codigo_instalacao': inst.codigo_instalacao,
                'razao_social': inst.razao_social
            }
            for inst in instalacoes
        ]

        return jsonify({
            'sucesso': True,
            'instalacoes': dados
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@instalacoes_bp.route('/vincular/instalacoes-cliente', methods=['POST'])
def vincular_instalacoes_cliente():
    try:
        cliente_id = request.form.get('cliente_selecionado_instalacao_vinculo')
        instalacoes_ids = request.form.getlist('instalacao_id')
        empresa_id = session.get('empresa')

        if not cliente_id or not instalacoes_ids:
            return jsonify({
                'sucesso': False,
                'erro': 'Cliente ou instalações não informados'
            }), 400

        instalacoes = (
            Instalacao.query
            .filter(
                Instalacao.id.in_(instalacoes_ids),
                Instalacao.empresa_id == empresa_id
            )
            .all()
        )

        if not instalacoes:
            return jsonify({
                'sucesso': False,
                'erro': 'Instalações não encontradas'
            }), 404

        for inst in instalacoes:
            inst.cliente_id = cliente_id

        db.session.commit()

        return redirect(url_for('home_bp.render_instalacoes'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500
    
@instalacoes_bp.route('/listar/instalacoes')
def listar_instalacoes():
    empresa_id = session.get('empresa')
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10

        offset = (page - 1) * per_page

        resultado = db.session.execute(
            text("SELECT * FROM instalacoes WHERE empresa_id = :empresa_id ORDER BY codigo_instalacao LIMIT :limit OFFSET :offset"),
            {'empresa_id': empresa_id, 'limit': per_page, 'offset': offset}
        )

        instalacoes = [dict(row._mapping) for row in resultado]

        total = db.session.execute(text(f"SELECT COUNT(*) FROM instalacoes WHERE empresa_id = {empresa_id}")).scalar()

        return render_template('/listar/listar_instalacoes.html',
                               instalacoes=instalacoes,
                               page=page,
                               per_page=per_page,
                               total=total)
    except Exception as e:
        print(f"Erro ao listar instalações: {str(e)}")
        return render_template('/listar/listar_instalacoes.html', 
                               error=f"Não foi possível carregar as instalações: {str(e)}")