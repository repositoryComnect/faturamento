from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from application.models.models import db, Plano, Contrato, Produto, Cliente
from sqlalchemy import text
from datetime import datetime
import re

planos_bp = Blueprint('planos_bp', __name__)

@planos_bp.route('/get/planos', methods=['GET'])
def get_planos():
    empresa_id = session.get('empresa')
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Itens por página
    offset = (page - 1) * per_page

    # Consulta paginada
    resultado = db.session.execute(
        text("SELECT * FROM planos WHERE empresa_id = :empresa_id ORDER BY id LIMIT :limit OFFSET :offset"),
        {"empresa_id": empresa_id,"limit": per_page, "offset": offset}
    )
    planos = [dict(row._mapping) for row in resultado]

    # Total de registros
    total = db.session.execute(text("SELECT COUNT(*) FROM planos")).scalar()

    # Criar dicionário de paginação
    pagination = {
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,  # arredonda para cima
        'has_prev': page > 1,
        'has_next': page * per_page < total,
        'prev_num': page - 1,
        'next_num': page + 1
    }

    return render_template(
        'listar_planos.html',
        planos=planos,
        page=page,
        per_page=per_page,
        total=total,
        pagination=pagination  # <-- ENVIA PARA O TEMPLATE
    )

@planos_bp.route('/insert/planos', methods=['POST'])
def insert_planos():
    empresa_id = session.get('empresa')
    try:
        db.session.rollback()
        form_data = request.form.to_dict()

        def parse_float(valor):
            try:
                return float(str(valor).replace(',', '.'))
            except (ValueError, TypeError):
                return 0.0

        # Pega dados do formulário
        codigo = form_data.get('codigo')
        nome = form_data.get('nome')
        valor_base = parse_float(form_data.get('valor', 0))
        id_produto = form_data.get('id_produto')
        produto_id = form_data.get('produto_id')
        qtd_produto = int(form_data.get('qtd_produto') or 0)
        contrato_id = form_data.get('contrato_id')

        # Cálculo do valor com base na quantidade e produto vinculado (se preço já não foi calculado no front)
        produto = None  # ✅ inicializa
        base_valor_produto = None

        if produto_id:
            produto = Produto.query.get(int(produto_id))
            base_valor_produto = produto.preco_base
            if produto and produto.preco_base and qtd_produto > 0:
                valor_base = float(produto.preco_base) * qtd_produto

        # Aliquota
        aliquota_sp = parse_float(form_data.get('aliquota_sp_licenca'))
        cod_servico_sp = form_data.get('cod_servico_sp_licenca')
        desc_nf_licenca = form_data.get('desc_nf_licenca')
        desc_boleto_licenca = form_data.get('desc_boleto_licenca')

        # Cálculo de imposto (caso deseje expandir futuramente com outras alíquotas)
        valor_com_imposto = valor_base + (valor_base * aliquota_sp / 100) if aliquota_sp > 0 else valor_base

        # Criação do plano
        plano_data = {
            'codigo': codigo,
            'nome': nome,
            'valor': round(valor_com_imposto, 2),
            'licenca_valor': round(valor_base, 2),
            'id_portal': id_produto,
            'desc_boleto_licenca': desc_boleto_licenca,
            'aliquota_sp_licenca': aliquota_sp,
            'cod_servico_sp_licenca': cod_servico_sp,
            'produto': produto.nome if produto else None,
            'valor_base_produto' : base_valor_produto,
            'qtd_produto' : qtd_produto,
            'desc_nf_licenca': desc_nf_licenca,
            'data_criacao': datetime.now(),
            'data_atualizacao': datetime.now(),
            'empresa_id': empresa_id
        }

        novo_plano = Plano(**plano_data)
        db.session.add(novo_plano)
        db.session.commit()

        # Vincular contrato (muitos-para-muitos)
        if contrato_id:
            contrato = Contrato.query.get(int(contrato_id))
            if contrato:
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
    empresa_id = session.get('empresa')

    if not empresa_id:
        return jsonify({'erro': 'Empresa não definida na sessão'}), 401

    # Filtra os contratos da empresa logada
    contratos = Contrato.query.filter_by(empresa_id=empresa_id).order_by(Contrato.numero).all()

    resultado = [
        {'id': c.id, 'numero': c.numero, 'razao_social': c.razao_social}
        for c in contratos
    ]
    
    return jsonify(resultado)

@planos_bp.route('/clientes_ativos_planos', methods=['GET'])
def clientes_ativos_planos():
    empresa_id = session.get('empresa')

    if not empresa_id:
        return jsonify({'erro': 'Empresa não definida na sessão'}), 401

    # Filtra os contratos da empresa logada
    clientes = Cliente.query.filter_by(empresa_id=empresa_id).order_by(Cliente.sequencia).all()

    resultado = [
        {'id': c.id, 'sequencia': c.sequencia, 'razao_social': c.razao_social}
        for c in clientes
    ]
    
    return jsonify(resultado)

@planos_bp.route('/get/id/planos', methods=['GET'])
def get_list_planos():
    empresa_id = session.get('empresa')
    search_term = request.args.get('search', '').strip()
    
    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    try:
        query = text("""
            SELECT * FROM planos
            WHERE empresa_id = :empresa_id
                     AND ( codigo LIKE :term 
               OR nome LIKE :term 
                     )
        """)

        result = db.session.execute(query, {'term': f'%{search_term}%', 'empresa_id': f'%{empresa_id}%'})
        planos = [dict(row._asdict()) for row in result]

        # Acrescentando total, página e itens por página
        total = len(planos)
        page = 1
        per_page = 5  # ou defina um valor fixo, ex: 10
        
        return render_template('listar_planos.html', planos=planos, total=total, page=page, per_page=per_page)  # Fixed variable name
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500

@planos_bp.route('/delete/planos', methods=['POST'])
def delete_planos():
    codigo = request.form.get('delete_codigo_plano')
    print(f"Código recebido para exclusão: {codigo}")
    
    try:
        # 1. Buscar ID do plano
        plano_id_result = db.session.execute(
            text("SELECT id FROM planos WHERE codigo = :codigo"),
            {'codigo': codigo}
        ).first()

        if not plano_id_result:
            flash('Plano não encontrado com esse código.', 'error')
            print("Plano não encontrado.")
            return redirect(url_for('home_bp.render_planos'))

        plano_id = plano_id_result[0]
        print(f"✅ Plano encontrado com ID: {plano_id}")

        # 2. Deletar vínculos na tabela contrato_plano
        deleted_links = db.session.execute(
            text("DELETE FROM contrato_plano WHERE plano_id = :plano_id"),
            {'plano_id': plano_id}
        )
        print(f"Vínculos removidos: {deleted_links.rowcount}")

        # 3. Deletar o plano
        deleted_plan = db.session.execute(
            text("DELETE FROM planos WHERE id = :plano_id"),
            {'plano_id': plano_id}
        )
        print(f"🗑️ Plano deletado? {deleted_plan.rowcount > 0}")

        db.session.commit()
        flash('Plano excluído com sucesso', 'success')

    except Exception as e:
        db.session.rollback()
        print(f"🚨 Erro ao excluir plano: {str(e)}")
        flash('Erro ao tentar excluir o plano.', 'error')

    return redirect(url_for('home_bp.render_planos'))

@planos_bp.route('/proximo_codigo_plano', methods=['GET'])
def proximo_codigo_plano():
    # Busca o último número de contrato ordenado por valor numérico
    planos = Plano.query.all()
    
    # Extraí apenas os números válidos (ex: "C0001", "C0023")
    numeros = []
    for p in planos:
        match = re.search(r'\d+', p.codigo)
        if match:
            numeros.append(int(match.group()))
    
    proximo = max(numeros) + 1 if numeros else 1
    numero_formatado = f"P{proximo:04d}"  # ex: C0001, C0002
    
    return jsonify({'proximo_codigo': numero_formatado})

@planos_bp.route('/planos/get_produtos', methods=['POST'])
def get_produtos():
    produtos = Produto.query.order_by(Produto.codigo).all()
    resultado = [{'id': p.id, 'codigo': p.codigo, 'nome': p.nome, 'preco_base': p.preco_base} for p in produtos]
    return jsonify(resultado) 



    