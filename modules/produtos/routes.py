from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, session
from application.models.models import Produto, db, Plano
from datetime import datetime
from sqlalchemy import text
import re

produtos_bp = Blueprint('produtos_bp', __name__)

@produtos_bp.route('/set/produtos', methods=['POST'])
def set_produtos():
    empresa_id = session.get('empresa')
    try:
        produto_data = {
            'codigo': request.form.get('codigo_produto'),
            'nome': request.form.get('nome'),
            'descricao': request.form.get('descricao'),
            'preco_base': request.form.get('preco_base'),
            'ativo': request.form.get('status'),
            'empresa_id' : empresa_id,    
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

@produtos_bp.route('/vincular/produto/planos', methods=['POST'])
def vincular_produto_planos():
    plano_id = request.form.get('plano_vincular_produto')
    produto_id = request.form.get('vincular_produto_id')

    if not plano_id or not produto_id:
        return jsonify({
            'success': False,
            'message': 'Plano ID e Produto ID são obrigatórios'
        }), 400

    try:
        produto = Produto.query.filter_by(id=produto_id).first()
        plano = Plano.query.filter_by(id=plano_id).first()
        
        if not produto:
            return jsonify({
                'success': False,
                'message': f'Produto com ID {produto_id} não encontrado'
            }), 404
            
        if not plano:
            return jsonify({
                'success': False,
                'message': f'Plano com ID {plano_id} não encontrado'
            }), 404
        
        nome_produto = produto.nome
        
        if len(nome_produto) > 20:
            print(f"Aviso: Nome do produto tem {len(nome_produto)} caracteres, será truncado para 20")
            nome_produto = nome_produto[:20]
        
        plano.produto = nome_produto      
        db.session.flush()
        db.session.commit()
        db.session.refresh(plano)
        
        return redirect(url_for(('home_bp.render_planos')))

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao vincular produto ao plano: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao vincular produto ao plano: {str(e)}',
            'error_details': str(e)
        }), 500

@produtos_bp.route('/desvincular/produto/planos', methods=['POST'])
def desvincular_produto_planos():
   
    plano_id = request.form.get('desvincular_plano_id_produtos')  
    produto_ids = request.form.getlist('produto_ids')
        
    try:
        plano = Plano.query.filter_by(id=plano_id).first()
        
        if not plano:
            flash('Plano não encontrado', 'error')
            return redirect(url_for('home_bp.render_planos'))
        
        plano.produto = None
        plano.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        flash('Produto desvinculado do plano com sucesso!', 'success')
        return redirect(url_for('home_bp.render_planos'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao desvincular produto: {str(e)}', 'error')
        return redirect(url_for('home_bp.render_planos'))

@produtos_bp.route('/get/planos/produto/<int:plano_id>')
def get_planos_produtos(plano_id):
    try:
        plano = Plano.query.get(plano_id)
        
        if not plano:
            return jsonify({
                'success': False,
                'message': f'Plano com ID {plano_id} não encontrado'
            }), 404
        
        if not plano.produto:
            return jsonify({
                'success': True,
                'produtos': [],
                'message': 'Nenhum produto vinculado a este plano'
            }), 200
        
        produtos = Produto.query.filter(Produto.nome.like(f"%{plano.produto}%")).all()
        
        
        produtos_list = []
        for produto in produtos:
            produtos_list.append({
                'id': produto.id,
                'nome': produto.nome,
                'descricao': produto.descricao if hasattr(produto, 'descricao') else '',
                'codigo': produto.codigo if hasattr(produto, 'codigo') else '',
            })
        
        return jsonify({
            'success': True,
            'produtos': produtos_list,
            'plano_info': {
                'id': plano.id,
                'nome': plano.nome,
                'produto_vinculado': plano.produto
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar produtos do plano: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar produtos: {str(e)}'
        }), 500

@produtos_bp.route('/proximo_codigo_produto', methods=['GET'])
def proximo_codigo_produto():
    produtos = Produto.query.all()
    
    numeros = []
    for produto in produtos:
        match = re.search(r'\d+', produto.codigo or '')
        if match:
            numeros.append(int(match.group()))
    
    proximo = max(numeros) + 1 if numeros else 1
    codigo_formatado = f"P{proximo:04d}" 
    
    return jsonify({'proximo_codigo_produto': codigo_formatado})    