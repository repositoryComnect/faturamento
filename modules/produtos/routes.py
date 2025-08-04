from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from application.models.models import Produto, db
from datetime import datetime
from sqlalchemy import text
import re

produtos_bp = Blueprint('produtos_bp', __name__)

@produtos_bp.route('/set/produtos', methods=['POST'])
def set_produtos():
    try:
        produto_data = {
            'codigo': request.form.get('codigo'),
            'nome': request.form.get('nome'),
            'descricao': request.form.get('descricao'),
            'preco_base': request.form.get('preco_base'),
            'ativo': request.form.get('status'),    
            }
        
        if Produto.query.filter_by(codigo=produto_data['codigo']).first():
            return jsonify({
                'success': False,
                'message': 'Já existe um produto com este código'
            }), 400
        
        novo_produto = Produto(**produto_data)
        db.session.add(novo_produto)
        db.session.commit()
        
        try:
            db.session.execute(
                "ALTER TABLE produtos AUTO_INCREMENT = : id",
                {'id': novo_produto.id + 1}
            )
            db.session.commit()
        except Exception as e:
            print(f"Alerta: Não foi possível realizar o autoincremento: {str(e)}")
        
        return redirect(url_for(('home_bp.render_produtos')))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar Produto: {str(e)}',
            'error_details': str(e)
        }), 500
    
@produtos_bp.route('/delete/produto', methods=['POST'])
def delete_produtos():
    codigo = request.form.get('codigo')

    try:
        db.session.execute(text("DELETE FROM produtos WHERE codigo = :codigo"),
            {'codigo': codigo})
        db.session.commit()

    except Exception as e:
        print(f"Alerta: Não foi possível realizar a exclusão do produto: {str(e)}")
    
    return redirect(url_for(('home_bp.render_produtos')))

@produtos_bp.route('/proximo_codigo_produto', methods=['GET'])
def proximo_codigo_produto():
    # Busca todos os produtos cadastrados
    produtos = Produto.query.all()
    
    numeros = []
    for produto in produtos:
        # Extrai número do código do produto, assumindo padrão como "P0001", "P0010", etc.
        match = re.search(r'\d+', produto.codigo or '')
        if match:
            numeros.append(int(match.group()))
    
    proximo = max(numeros) + 1 if numeros else 1
    codigo_formatado = f"P{proximo:04d}"  # ex: P0001, P0002, etc.
    
    return jsonify({'proximo_codigo_produto': codigo_formatado})    