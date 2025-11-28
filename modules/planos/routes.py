from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from application.models.models import db, Plano, Contrato, Produto, Cliente, contrato_plano
from sqlalchemy import text
from datetime import datetime
from modules.utils.utils import formatar_telefone, safe_float, safe_date, parse_date, formatar_cep, formatar_cpf_cnpj

from modules.planos.utils import montar_dict_plano, parse_float
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
    
@planos_bp.route('/edit/planos', methods=['POST'])
def edit_planos():
    empresa_id = session.get('empresa')
    try:
        form_data = request.form.to_dict()

        # Obter o código do plano enviado pelo formulário
        codigo = form_data.get('atualizar_codigo_plano')

        if not codigo:
            return jsonify({'success': False, 'message': 'Código do plano não enviado'}), 400

        # Buscar o plano existente pelo código
        plano = Plano.query.filter_by(codigo=codigo, empresa_id=empresa_id).first()

        if not plano:
            return jsonify({'success': False, 'message': 'Plano não encontrado'}), 404

        # Dados do formulário
        plano.nome = form_data.get('atualizar_nome_plano')
        valor_base = parse_float(form_data.get('atualizar_valor_plano', 0))
        plano.licenca_valor = round(valor_base, 2)

        plano.id_portal = form_data.get('atualizar_id_portal_plano')

        # Aliquota
        aliquota_sp = parse_float(form_data.get('atualizar_aliquota_plano'))
        plano.aliquota_sp_licenca = aliquota_sp

        plano.desc_boleto_licenca = form_data.get('descricao_boleto_plano')
        plano.cod_servico_sp_licenca = form_data.get('atualizar_codigo_servico_plano')
        plano.desc_nf_licenca = form_data.get('atualizar_descricao_nf_plano')

        # REAPLICA O CÁLCULO DO VALOR FINAL
        if aliquota_sp > 0:
            plano.valor = round(valor_base + (valor_base * aliquota_sp / 100), 2)
        else:
            plano.valor = round(valor_base, 2)

        # Atualizar campo de atualização
        plano.data_atualizacao = datetime.now()

        db.session.commit()
        return redirect(url_for('home_bp.render_planos'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao editar plano: {str(e)}'
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
    print(f"Código recebido para arquivamento: {codigo}")

    try:
        plano = Plano.query.filter_by(codigo=codigo).first()

        if not plano:
            flash('Plano não encontrado com esse código.', 'error')
            print("Plano não encontrado.")
            return redirect(url_for('home_bp.render_planos'))

        # Soft delete
        plano.status = 'Arquivado'
        plano.data_atualizacao = datetime.utcnow()  # se quiser atualizar a data

        db.session.commit()

        print(f"Plano {codigo} marcado como arquivado.")
        flash('Plano arquivado com sucesso', 'success')

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao arquivar plano: {str(e)}")
        flash('Erro ao tentar arquivar o plano.', 'error')

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

@planos_bp.route('/planos/proximo/<codigo_atual>', methods=['GET'])
def proximo_plano(codigo_atual):
    empresa_id = session.get('empresa')
    if not empresa_id:
        return jsonify({'error': 'Empresa não selecionada'}), 400

    try:
        # Localizar o plano atual
        plano_atual = (
            Plano.query
            .filter_by(codigo=codigo_atual, empresa_id=empresa_id)
            .first()
        )

        if not plano_atual:
            return jsonify({'error': 'Plano atual não encontrado'}), 404

        # Buscar o próximo
        plano = (
            Plano.query
            .filter(
                Plano.id > plano_atual.id,
                Plano.empresa_id == empresa_id
            )
            .order_by(Plano.id.asc())
            .first()
        )

        if not plano:
            return jsonify({}), 200

        # =================================================================
        # BUSCAR CONTRATOS VINCULADOS AO PLANO (MESMA LÓGICA DO buscar-por-codigo)
        # =================================================================
        contratos = (
            db.session.query(Contrato)
            .join(contrato_plano, Contrato.id == contrato_plano.c.contrato_id)
            .filter(contrato_plano.c.plano_id == plano.id)
            .filter(Contrato.empresa_id == empresa_id)
            .all()
        )

        contratos_json = []
        for c in contratos:
            contratos_json.append({
                'id': c.id,
                'numero': c.numero,
                'razao_social': c.razao_social,
                'nome_fantasia': c.nome_fantasia,
                'contato': c.contato,
                'email': c.email,
                'telefone': c.telefone,
                'cnpj_cpf': formatar_cpf_cnpj(c.cnpj_cpf),
                'cidade': c.cidade,
                'estado': c.estado,
                'tipo': c.tipo,
                'status': c.estado_contrato,
                'dia_vencimento': c.dia_vencimento,
                'plano_codigo': plano.codigo
            })

        retorno = montar_dict_plano(plano)
        retorno['contratos'] = contratos_json

        return jsonify(retorno)

    except Exception as e:
        import traceback
        traceback.print_exc()   
        return jsonify({'error': str(e)}), 500


@planos_bp.route('/planos/buscar-por-codigo/<codigo>', methods=['GET'])
def buscar_plano_por_codigo(codigo):
    empresa_id = session.get('empresa')

    try:
        plano = db.session.execute(
            db.select(Plano).filter_by(codigo=codigo, empresa_id=empresa_id)
        ).scalar_one_or_none()

        if not plano:
            return jsonify({'error': 'Plano não encontrado'}), 404

        # ==========================================
        # BUSCAR CONTRATOS VINCULADOS AO PLANO
        # ==========================================
        contratos = (
            db.session.query(Contrato)
            .join(contrato_plano, Contrato.id == contrato_plano.c.contrato_id)
            .filter(contrato_plano.c.plano_id == plano.id)
            .filter(Contrato.empresa_id == empresa_id)
            .all()
        )

        contratos_json = []
        for c in contratos:
            contratos_json.append({
                'id': c.id,
                
                # CAMPOS REAIS EXISTENTES NA TABELA
                'numero': c.numero,
                'razao_social': c.razao_social,
                'nome_fantasia': c.nome_fantasia,
                'contato': c.contato,
                'email': c.email,
                'telefone': c.telefone,
                'cnpj_cpf': formatar_cpf_cnpj(c.cnpj_cpf),
                'cidade': c.cidade,
                'estado': c.estado,
                'tipo': c.tipo,
                'status': c.estado_contrato,
                'dia_vencimento': c.dia_vencimento,

                # VALOR DO CONTRATO
                #'valor': float(getattr(c, 'valor_total', 0)) if getattr(c, 'valor_total', None) not in (None, "") else 0,

                # INFO DO PLANO
                'plano_codigo': plano.codigo
            })

        # ==========================================
        # RETORNAR O PLANO (JÁ COM OS CONTRATOS)
        # ==========================================
        retorno = montar_dict_plano(plano)        # usa sua função
        retorno['contratos'] = contratos_json                # sobrepõe com campos reais

        return jsonify(retorno)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500



@planos_bp.route('/listagem/planos/popup', methods=['GET'])
def planos_listagem_ativos():
    empresa_id = session.get('empresa')

    if not empresa_id:
        return jsonify({'erro': 'Empresa não definida na sessão'}), 401

    # Filtra planos da empresa
    planos = Plano.query.filter_by(empresa_id=empresa_id).order_by(Plano.codigo).all()

    resultado = [
        {
            'id': p.id,
            'codigo': p.codigo,
            'nome': p.nome,
            'valor': float(p.valor) if p.valor else 0.0
        }
        for p in planos
    ]

    return jsonify(resultado)

@planos_bp.route('/buscar_plano', methods=['POST'])
def buscar_plano():
    data = request.get_json()
    termo = data.get('termo', '')
    empresa_id = session.get('empresa')

    if not termo:
        return jsonify({'success': False, 'error': 'Nenhum termo enviado'})

    plano = Plano.query.filter(
        Plano.empresa_id == empresa_id, (
        (Plano.codigo.ilike(f"%{termo}%")) |
        (Plano.nome.ilike(f"%{termo}%"))
    )).first()

    if plano:
        return jsonify({
            'success': True,
            'plano': {
                "codigo": plano.codigo,
                "nome": plano.nome,
                "valor": plano.valor,
                "id_produto_portal": plano.id_portal,
                "licenca_valor": plano.licenca_valor,
                "produto": plano.produto,
                "qtd_produto": plano.qtd_produto,
                "desc_boleto_licenca": plano.desc_boleto_licenca,
                "aliquota_sp_licenca": plano.aliquota_sp_licenca,
                "cod_servico_sp_licenca": plano.cod_servico_sp_licenca,
                "desc_nf_licenca": plano.desc_nf_licenca,
                "valor_base_produto": plano.valor_base_produto,

                # só a data
                "cadastramento": plano.data_criacao.strftime("%d/%m/%Y") if plano.data_criacao else "",
                "atualizacao": plano.data_atualizacao.strftime("%d/%m/%Y") if plano.data_atualizacao else ""
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Plano não encontrado'})

    