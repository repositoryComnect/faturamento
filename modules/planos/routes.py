from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from application.models.models import db, Plano
from sqlalchemy import text
from datetime import datetime


planos_bp = Blueprint('planos_bp', __name__)



@planos_bp.route('/get/planos', methods=['GET'])
def get_planos():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Itens por página
        
        # Consulta com paginação
    offset = (page - 1) * per_page
    resultado = db.session.execute(
        text("SELECT * FROM planos ; "),

        )
        
    planos = [dict(row._mapping) for row in resultado]
    total = db.session.execute(text("SELECT COUNT(*) FROM planos")).scalar()
        
    return render_template('listar_planos.html', planos=planos, page=page, per_page=per_page, total=total)





@planos_bp.route('/insert/planos', methods=['POST'])
def insert_planos():
    try:
        # Verificar e resetar transações pendentes
        db.session.rollback()
        
        # Pegar todos os dados do formulário
        form_data = request.form.to_dict()

        # Converter valores monetários e tratar campos
        nf_sao_paulo = True if form_data.get('nf_sao_paulo') == 'on' else False
        
        plano_data = {
            'codigo': form_data.get('codigo'),
            'nome': form_data.get('nome'),
            'valor': float(form_data.get('valor', 0).replace(',', '.')),
            'id_portal': form_data.get('id_portal'),
            'licenca_descricao': form_data.get('licenca_descricao'),
            'licenca_valor': float(form_data.get('licenca_valor', 0).replace(',', '.')),
            'nf_descricao': form_data.get('nf_descricao'),
            'aliquota': float(form_data.get('aliquota', 0).replace(',', '.')),
            'cod_servico': form_data.get('cod_servico'),
            'nf_sao_paulo': nf_sao_paulo,
            'data_criacao': datetime.now(),
            'data_atualizacao': datetime.now()
        }
        
       
        # Criar novo plano
        novo_plano = Plano(**plano_data)
        
        # Adicionar e commitar no banco
        db.session.add(novo_plano)
        db.session.commit()
        
        return redirect(url_for('home_bp.render_planos'))
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro na conversão de valores: {str(e)}'
        }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar plano: {str(e)}'
        }), 500
    



@planos_bp.route('/get/id/planos', methods=['GET'])
def get_list_planos():
    search_term = request.args.get('search', '').strip()
    
    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    try:
        query = text("""
            SELECT * FROM planos
            WHERE codigo LIKE :term 
               OR nome LIKE :term 
        """)

        result = db.session.execute(query, {'term': f'%{search_term}%'})
        planos = [dict(row._asdict()) for row in result]
        
        return render_template('listar_planos.html', planos=planos)  # Fixed variable name
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500



@planos_bp.route('/delete/planos', methods=['POST'])
def delete_planos():
    codigo = request.form.get('delete_codigo_plano')
    
    try:
        # Primeiro verifica se existem contratos vinculados
        contratos_count = db.session.execute(
            text("SELECT COUNT(*) FROM contratos WHERE plano_id = (SELECT id FROM planos WHERE codigo = :codigo)"),
            {'codigo': codigo}
        ).scalar()
        
        if contratos_count > 0:
            flash('Não é possível excluir: este plano está vinculado a contratos existentes', 'error')
        else:
            db.session.execute(
                text("DELETE FROM planos WHERE codigo = :codigo"),
                {'codigo': codigo}
            )
            db.session.commit()
            flash('Plano excluído com sucesso', 'success')
            
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir plano: {str(e)}")
        flash('Ocorreu um erro ao tentar excluir o plano', 'error')
    
    return redirect(url_for('home_bp.render_planos'))

    