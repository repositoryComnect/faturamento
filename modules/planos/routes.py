from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from application.models.models import db, Plano, Contrato
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
        db.session.rollback()
        form_data = request.form.to_dict()

        nf_sao_paulo = True if form_data.get('nf_sao_paulo') == 'on' else False

        # Ajustar para garantir que o valor é tratado como string antes de aplicar replace
        plano_data = {
            'codigo': form_data.get('codigo'),
            'nome': form_data.get('nome'),
            # Corrigir aqui: garantir que 'valor' seja tratado como string antes do replace
            'valor': float(str(form_data.get('valor', 0)).replace(',', '.')),
            'id_portal': form_data.get('id_portal'),
            'licenca_descricao': form_data.get('licenca_descricao'),
            # Corrigir aqui: garantir que 'licenca_valor' seja tratado como string antes do replace
            'licenca_valor': float(str(form_data.get('licenca_valor', 0)).replace(',', '.')),
            # Corrigir aqui: garantir que 'aliquota' seja tratado como string antes do replace
            'aliquota': float(str(form_data.get('aliquota', 0)).replace(',', '.')),
            'cod_servico': form_data.get('cod_servico'),
            'nf_sao_paulo': nf_sao_paulo,
            'data_criacao': datetime.now(),
            'data_atualizacao': datetime.now()
        }

        # Criar o plano
        novo_plano = Plano(**plano_data)
        db.session.add(novo_plano)
        db.session.commit()

        # Associar com contrato (se selecionado)
        contrato_id = form_data.get('contrato_id')
        if contrato_id:
            contrato = Contrato.query.get(int(contrato_id))
            # Associa o plano ao contrato através da tabela intermediária
            contrato.planos.append(novo_plano)
            db.session.commit()

        return redirect(url_for('home_bp.render_planos'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar plano: {str(e)}'
        }), 500

@planos_bp.route('/contratos_ativos', methods=['GET'])
def contratos_ativos():
    contratos = Contrato.query.order_by(Contrato.numero).all()
    resultado = [{'id': c.id, 'numero': c.numero, 'razao_social': c.razao_social} for c in contratos]
    return jsonify(resultado)    

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

    