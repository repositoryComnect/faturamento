from flask import render_template, Blueprint, jsonify, request, redirect, url_for, session
from application.models.models import  db, Vendedor
from sqlalchemy import text
from datetime import datetime
import re


vendedores_bp = Blueprint('vendedores_bp', __name__)

@vendedores_bp.route('/insert/vendedores', methods=['POST'])
def insert_vendedores():
    empresa_id = session.get('empresa')
    try:
        revenda_data = {
            'codigo': request.form.get('codigo'),
            'nome': request.form.get('nome_vendedor'),
            'cpf': request.form.get('cpf_vendedor'),
            'telefone': request.form.get('telefone_vendedor'),
            'email': request.form.get('email_vendedor'),
            'ativo': request.form.get('status') == '1',
            'empresa_id' : empresa_id
        }

        novo_vendedor = Vendedor(**revenda_data)
        db.session.add(novo_vendedor)
        db.session.commit()

        return redirect(url_for('home_bp.render_vendedores'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar vendedor: {str(e)}',
            'error_details': str(e)
        }), 500

@vendedores_bp.route('/get/vendedores', methods=['GET'])
def get_vendedores():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10  
        
        offset = (page - 1) * per_page
        resultado = db.session.execute(
            text("SELECT * FROM vendedores ORDER BY nome LIMIT :limit OFFSET :offset"),
            {'limit': per_page, 'offset': offset}
        )
        
        vendedores = [dict(row._mapping) for row in resultado]
        total = db.session.execute(text("SELECT COUNT(*) FROM vendedores")).scalar()

        return render_template(
            '/listar/listar_vendedores.html',
            vendedores=vendedores,
            page=page,
            per_page=per_page,
            total=total
        )

    except Exception as e:
        print(f"Erro ao listar vendedores: {str(e)}")
        return render_template(
            '/listar/listar_revendas.html',
            vendedores=[],
            page=1,
            per_page=10,
            total=0,
            error=f"Não foi possível carregar os vendedores: {str(e)}")

@vendedores_bp.route('/proximo_codigo_vendedor', methods=['GET'])
def proximo_codigo_vendedor():
    try:
        # Busca todas as revendas com código preenchido
        vendedores = Vendedor.query.with_entities(Vendedor.codigo).all()

        numeros = []
        for vend in vendedores:
            if vend.codigo:
                match = re.search(r'\d+', vend.codigo)
                if match:
                    numeros.append(int(match.group()))
        
        proximo = max(numeros) + 1 if numeros else 1
        codigo_formatado = f"V{proximo:04d}"  # Exemplo: R0001, R0002...

        return jsonify({'proximo_codigo_vendedor': codigo_formatado})

    except Exception as e:
        print(f"Erro ao gerar código do vendedor: {e}")
        return jsonify({'error': 'Erro ao gerar o próximo código do vendedor'}), 500

@vendedores_bp.route('/delete/vendedores', methods=['POST'])
def delete_vendedores():
    codigo = request.form.get('codigo')
    try:
        db.session.execute(text("DELETE FROM vendedores WHERE codigo = :codigo"),
            {'codigo': codigo})
        db.session.commit()

    except Exception as e:
        print(f"Alerta: Não foi possível realizar a exclusão do vendedor: {str(e)}")
    
    return redirect(url_for(('home_bp.render_vendedores')))