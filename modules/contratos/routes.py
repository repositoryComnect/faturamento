from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, session
from application.models.models import Contrato, db, Cliente, Produto, Plano, ContratoProduto, Revenda, cliente_contrato
from datetime import datetime, date
from sqlalchemy import text
import re

contratos_bp = Blueprint('contratos_bp', __name__)

@contratos_bp.route('/proximo_numero_contrato', methods=['GET'])
def proximo_numero_contrato():
    # Busca o último número de contrato ordenado por valor numérico
    contratos = Contrato.query.all()
    
    # Extraí apenas os números válidos (ex: "C0001", "C0023")
    numeros = []
    for c in contratos:
        match = re.search(r'\d+', c.numero)
        if match:
            numeros.append(int(match.group()))
    
    proximo = max(numeros) + 1 if numeros else 1
    numero_formatado = f"C{proximo:04d}"  # ex: C0001, C0002
    
    return jsonify({'proximo_numero': numero_formatado})

@contratos_bp.route('/produtos_ativos', methods=['GET'])
def produtos_ativos():
    empresa_id = session.get('empresa')
    produtos = Produto.query.filter_by(ativo='Ativo', empresa_id=empresa_id).order_by(Produto.nome).all()
    resultado = [
    {
        'id': p.id,
        'nome': p.nome,
        'preco_base': float(p.preco_base) if p.preco_base is not None else 0.0
    }
    for p in produtos
]
    return jsonify(resultado)

@contratos_bp.route('/planos_ativos', methods=['GET'])
def planos_ativos():
    empresa_id = session.get('empresa')
    planos = Plano.query.filter_by(empresa_id=empresa_id).order_by(Plano.nome).all()
    resultado = [{'id': p.id, 'nome': p.nome, 'valor': str(p.valor)} for p in planos]
    return jsonify(resultado)

@contratos_bp.route('/contratos/delete', methods=['POST'])
def delete_contrato():
    numero = request.form.get('numero')
    action = request.form.get('action')

    try:
        if not numero:
            return jsonify({'error': True, 'message': 'Número do contrato não foi informado'}), 400

        contrato = db.session.execute(text("SELECT id, numero FROM contratos WHERE numero = :numero"), {'numero': numero}).fetchone()

        if not contrato:
            return jsonify({'error': True, 'message': f'Contrato {numero} não encontrado'}), 404

        contrato_id = contrato[0]

        if action == 'check':
            count = db.session.execute(text("SELECT COUNT(*) FROM cliente_contrato WHERE contrato_id = :id"), {'id': contrato_id}).scalar()
            return jsonify({
                'success': True,
                'hasClients': count > 0,
                'count': count,
                'contrato': {
                    'id': contrato_id,
                    'numero': contrato[1],
                    'sequencia': contrato_id
                }
            })

        elif action == 'unlink':
            # Excluindo dependências primeiro
            db.session.execute(text("DELETE FROM cliente_contrato WHERE contrato_id = :id"), {'id': contrato_id})
            db.session.execute(text("DELETE FROM contrato_plano WHERE contrato_id = :id"), {'id': contrato_id})
            db.session.execute(text("DELETE FROM contratos_produtos WHERE contrato_id = :id"), {'id': contrato_id})
            db.session.commit()
            return jsonify({'success': True, 'message': f'Contrato {numero} desvinculado com sucesso'})

        elif action == 'delete':
            # Excluindo dependências primeiro
            db.session.execute(text("DELETE FROM cliente_contrato WHERE contrato_id = :id"), {'id': contrato_id})
            db.session.execute(text("DELETE FROM contrato_plano WHERE contrato_id = :id"), {'id': contrato_id})
            db.session.execute(text("DELETE FROM contratos_produtos WHERE contrato_id = :id"), {'id': contrato_id})

            # Agora, excluindo o contrato
            db.session.execute(text("DELETE FROM contratos WHERE id = :id"), {'id': contrato_id})
            db.session.commit()

            return jsonify({'success': True, 'message': f'Contrato {numero} excluído com sucesso'})

        return jsonify({'error': True, 'message': 'Ação inválida'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': f'Erro no servidor: {str(e)}'}), 500

@contratos_bp.route('/buscar_contrato', methods=['POST'])
def buscar_contrato():
    data = request.get_json()
    termo = data.get('termo', '')
    empresa_id = session.get('empresa')

    if not termo:
        return jsonify({'success': False, 'error': 'Nenhum termo enviado'})
    
    def format_date(date):
            return date.strftime('%d/%m/%Y') if date else None

    # Aqui buscamos pelo número do contrato, razão social, nome fantasia ou ID do contrato
    contrato = Contrato.query.filter(
        Contrato.empresa_id == empresa_id, (
        (Contrato.numero.ilike(f"%{termo}%")) |
        (Contrato.razao_social.ilike(f"%{termo}%")) |
        (Contrato.nome_fantasia.ilike(f"%{termo}%")) |
        (Contrato.id_matriz_portal.ilike(f"%{termo}%"))
    )).first()

    if contrato:
        return jsonify({
            'success': True,
            'contrato': {
                'numero': contrato.numero,
                'registration': format_date(contrato.cadastramento),
                'atualizacao': format_date(contrato.atualizacao),
                'razao_social': contrato.razao_social or None,
                'nome_fantasia': contrato.nome_fantasia or None,
                'contato': contrato.contato or None,
                'address_email': contrato.email or None,
                'telefone': contrato.telefone or None,
                'tipo': contrato.tipo or None,
                'id_matriz_portal': contrato.id_matriz_portal or None,
                'responsavel': contrato.responsavel or None,
                'zip_code_cep': contrato.cep or None,
                'cnpj_cpf': contrato.cnpj_cpf or None,
                'endereco': contrato.endereco or None,
                'complemento': contrato.complemento or None,
                'bairro': contrato.bairro or None,
                'cidade': contrato.cidade or None,
                'estado': contrato.estado or None,
                'fator_juros': contrato.fator_juros or None,
                #'plano_nome': contrato.plano_nome or None,
                #'valor_plano': contrato.valor_plano or None,
                #'valor_contrato': contrato.valor_contrato or None,
                'dia_vencimento': contrato.dia_vencimento or None,
                'data_estado': contrato.data_estado if contrato.data_estado else None,
                'motivo_estado': contrato.motivo_estado or None,
                'estado_contrato': contrato.estado_contrato or None
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Contrato não encontrado para esta empresa.'})

@contratos_bp.route('/contratos/alterar', methods=['POST'])
def alterar_contrato():
    def parse_date(date_str):
        if not date_str:
            return None
        try:
            day, month, year = map(int, date_str.split('/'))
            return f"{year}-{month:02d}-{day:02d}"
        except:
            return None

    try:
        numero = request.form.get('contract_number')
        razao_social = request.form.get('company_name')
        nome_fantasia = request.form.get('trade_name')
        atualizacao = parse_date(request.form.get('update_datetime_edit'))
        tipo = request.form.get('type')
        responsavel = request.form.get('responsible')
        contato = request.form.get('contact')
        email = request.form.get('email')
        telefone = request.form.get('phone')
        cep = request.form.get('cep')
        endereco = request.form.get('address')
        complemento = request.form.get('complement')
        bairro = request.form.get('neighborhood')
        cidade = request.form.get('city')
        estado = request.form.get('state')
        dia_vencimento = request.form.get('last_day')
        fator_juros = request.form.get('interest_rate_factor')
        id_matriz_portal  = request.form.get('id_matriz_portal')
        contrato_revenda = request.form.get('revenda_selecionada')

        # Tratamento seguro do campo
        faturamento_contrato_raw = request.form.get('contract_value')
        faturamento_contrato = (
            int(faturamento_contrato_raw) if faturamento_contrato_raw and faturamento_contrato_raw.strip() else None
        )

        estado_contrato = request.form.get('current_state')
        data_estado = request.form.get('state_date')
        motivo_estado = request.form.get('reason')

        if not numero:
            return jsonify({'success': False, 'message': 'Número do contrato é obrigatório'}), 400

        db.session.execute(
            text("""
                UPDATE contratos SET
                    razao_social = :razao_social,
                    nome_fantasia = :nome_fantasia,
                    tipo = :tipo,
                    atualizacao = :atualizacao,
                    responsavel = :responsavel,
                    contato = :contato,
                    email = :email,
                    telefone = :telefone,
                    cep = :cep,
                    endereco = :endereco,
                    complemento = :complemento,
                    bairro = :bairro,
                    cidade = :cidade,
                    estado = :estado,
                    dia_vencimento = :dia_vencimento,
                    fator_juros = :fator_juros,
                    contrato_revenda = :contrato_revenda,
                    faturamento_contrato = :faturamento_contrato,
                    estado_contrato = :estado_contrato,
                    data_estado = :data_estado,
                    motivo_estado = :motivo_estado,
                    atualizacao = CURRENT_TIMESTAMP
                WHERE numero = :numero
            """),
            {
                'numero': numero,
                'razao_social': razao_social,
                'nome_fantasia': nome_fantasia,
                'tipo': tipo,
                'atualizacao': atualizacao,
                'responsavel': responsavel,
                'contato': contato,
                'email': email,
                'telefone': telefone,
                'cep': cep,
                'endereco': endereco,
                'complemento': complemento,
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado,
                'dia_vencimento': dia_vencimento,
                'fator_juros': fator_juros,
                'contrato_revenda': contrato_revenda,
                'faturamento_contrato': faturamento_contrato,
                'estado_contrato': estado_contrato,
                'data_estado': data_estado,
                'motivo_estado': motivo_estado, 
                'id_matriz_portal': id_matriz_portal,
            }
        )
        db.session.commit()

        return redirect(url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar contrato: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar contrato: {str(e)}'
        }), 500

@contratos_bp.route('/listar/contratos')
def listar_contratos():
    try:
        empresa_id = session.get('empresa')
        page = request.args.get('page', 1, type=int)
        per_page = 10  
        
        offset = (page - 1) * per_page
        resultado = db.session.execute(
            text("SELECT * FROM contratos WHERE empresa_id = :empresa_id ORDER BY numero LIMIT :limit OFFSET :offset"),
            {'empresa_id': empresa_id, 'limit': per_page, 'offset': offset}
        )
        
        contratos = [dict(row._mapping) for row in resultado]
        total = db.session.execute(
            text("SELECT COUNT(*) FROM contratos WHERE empresa_id = :empresa_id"),
            {'empresa_id': empresa_id}).scalar()

        # Para depuração: print os dados de contratos e total
        print("Contratos:", contratos)
        print("Total:", total)
        
        return render_template('listar_contratos.html', 
                               contratos=contratos,
                               page=page,
                               per_page=per_page,
                               total=total)
        
    except Exception as e:
        print(f"Erro ao listar contratos: {str(e)}")
        return render_template('listar_contratos.html', 
                               error=f"Não foi possível carregar os contratos: {str(e)}")

@contratos_bp.route('/contratos/buscar-por-numero/<numero>', methods=['GET'])
def buscar_contrato_por_numero(numero):
    empresa_id = session.get('empresa')
    if not empresa_id:
        return jsonify({'error': 'Empresa não selecionada'}), 400

    try:
        # Filtra pelo número e pela empresa da session
        contrato = Contrato.query.filter_by(numero=numero, empresa_id=empresa_id).first()
        
        if not contrato:
            return jsonify({'error': f'Contrato {numero} não encontrado'}), 404

        def format_date(date):
            return date.strftime('%d/%m/%Y') if date else None

        data = {
            'id': contrato.id,
            'numero': contrato.numero,
            'razao_social': contrato.razao_social or None,
            'nome_fantasia': contrato.nome_fantasia or None,
            'atualizacao': format_date(contrato.atualizacao),
            'cadastramento': format_date(contrato.cadastramento),
            'tipo': contrato.tipo or None,
            'contato': contrato.contato or None,
            'id_matriz_portal': contrato.id_matriz_portal or None,
            'email': contrato.email or None,
            'telefone': contrato.telefone or None,
            'responsavel': contrato.responsavel or None,
            'cep': contrato.cep or None,
            'cnpj_cpf': contrato.cnpj_cpf or None,
            'revenda': contrato.revenda or None,
            'vendedor': contrato.vendedor or None,
            'endereco': contrato.endereco or None,
            'complemento': contrato.complemento or None,
            'bairro': contrato.bairro or None,
            'cidade': contrato.cidade or None,
            'estado': contrato.estado or None,
            'dia_vencimento': contrato.dia_vencimento or None,
            'fator_juros': float(contrato.fator_juros) if contrato.fator_juros else None,
            'contrato_revenda': contrato.contrato_revenda or None,
            'faturamento_contrato': contrato.faturamento_contrato or None,
            'estado_contrato': contrato.estado_contrato or None,
            'data_estado': format_date(contrato.data_estado),
            'motivo_estado': contrato.motivo_estado or None,
        }

        # Clientes associados
        data['clientes'] = [{
            'nome_fantasia': c.nome_fantasia or None,
            'razao_social': c.razao_social or None,
            'cnpj': c.cnpj or None,
            'atividade': c.atividade or None,
            'cidade': c.cidade or None,
            'estado_atual': c.estado_atual or None,
            'numero_contrato_cadastrado': c.numero_contrato
        } for c in contrato.clientes] if contrato.clientes else []

        # Planos associados (N:N)
        data['planos'] = [{
            'id': p.id,
            'codigo': p.codigo,
            'nome': p.nome,
            'valor': float(p.valor),
            'status': 'Ativo'
        } for p in contrato.planos] if contrato.planos else []

        # Produtos associados via tabela intermediária
        associacoes = ContratoProduto.query.filter_by(contrato_id=contrato.id).all()
        data['produtos'] = []
        for assoc in associacoes:
            produto = Produto.query.get(assoc.produto_id)
            if produto:
                data['produtos'].append({
                    'id': produto.id,
                    'nome': produto.nome,
                    'quantidade': assoc.quantidade,
                    'descricao': produto.descricao,
                    'valor_unitario': float(produto.preco_base) if produto.preco_base else 0.00
                })

        return jsonify(data)
    
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({'error': 'Erro ao processar a requisição'}), 500

@contratos_bp.route('/set_contrato', methods=['POST'])
def set_contrato():
    empresa_id = session.get('empresa')
    if not empresa_id:
        return jsonify({
            'success': False,
            'message': 'Empresa não selecionada. Não é possível criar contrato.'
        }), 400

    try:
        db.session.rollback()
        form_data = request.form.to_dict()

        def parse_date(date_str):
            if not date_str:
                return None
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            return None

        def parse_int(value):
            try:
                return int(value) if value else None
            except (ValueError, TypeError):
                return None

        def parse_float(value):
            try:
                return float(value) if value else None
            except (ValueError, TypeError):
                return None

        def parse_bool(value):
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'y', 't')
            return bool(value)

        # Dados principais do contrato
        contrato_data = {
            'numero': form_data.get('numero_contrato'),
            'cadastramento': parse_date(form_data.get('current_datetime')),
            'atualizacao': parse_date(form_data.get('update_datetime')),
            'tipo': form_data.get('tipo_contrato'),
            'id_matriz_portal': form_data.get('portal_id'),
            'responsavel': form_data.get('responsavel'),
            'cnpj_cpf': form_data.get('cnpj'),
            'tipo_pessoa': form_data.get('people_type'),
            'revenda': form_data.get('revenda_selecionada'),
            'vendedor': form_data.get('vendedor_selecionado'),
            'razao_social': form_data.get('razao_social'),
            'nome_fantasia': form_data.get('nome_fantasia'),
            'contato': form_data.get('contato'),
            'email': form_data.get('email'),
            'telefone': form_data.get('telefone'),
            'cep': form_data.get('cep'),
            'endereco': form_data.get('endereco'),
            'complemento': form_data.get('complemento'),
            'bairro': form_data.get('bairro'),
            'cidade': form_data.get('cidade'),
            'estado': form_data.get('uf'),
            'dia_vencimento': parse_int(form_data.get('dia_vencimento')),
            'fator_juros': parse_float(form_data.get('fator_juros')),
            'contrato_revenda': parse_bool(form_data.get('contrato_revenda')),
            'faturamento_contrato': parse_bool(form_data.get('faturamento_contrato')),
            'estado_contrato': form_data.get('estado_contrato'),
            'data_estado': parse_date(form_data.get('date_status')),
            'motivo_estado': form_data.get('motivo_estado'),
            'empresa_id': session.get('empresa') 
        }

        # Verifica se contrato já existe
        if Contrato.query.filter_by(numero=contrato_data['numero']).first():
            return jsonify({
                'success': False,
                'message': 'Já existe um contrato com este número'
            }), 400

        # Cria contrato
        novo_contrato = Contrato(**contrato_data)
        db.session.add(novo_contrato)
        db.session.commit()

        # Associa produto
        produto_id = form_data.get('produto_id')
        if produto_id:
            produto = Produto.query.get(produto_id)
            if produto:
                contrato_produto = ContratoProduto(
                    contrato_id=novo_contrato.id,
                    produto_id=produto.id,
                    quantidade=1,
                    valor_unitario=produto.preco_base
                )
                db.session.add(contrato_produto)
                db.session.commit()

        # Associa plano
        plano_id = form_data.get('plano_id')
        if plano_id:
            plano = Plano.query.get(int(plano_id))
            if plano:
                novo_contrato.planos.append(plano)
                db.session.commit()

            cliente_id = request.form.get('cliente_selecionado')

        # Se um cliente foi selecionado, associar
        if cliente_id:
            try:
                cliente_id_int = int(cliente_id)
                stmt = cliente_contrato.insert().values(
                    cliente_id=cliente_id_int,
                    contrato_id=novo_contrato.id
                )
                db.session.execute(stmt)
                db.session.commit()
            except ValueError:
                # Cliente ID inválido (ex: string não numérica)
                print(f"ID de cliente inválido: {cliente_id}")

        # Ajusta auto_increment (opcional)
        try:
            db.session.execute(
                text("ALTER TABLE contratos AUTO_INCREMENT = :id"),
                {'id': novo_contrato.id + 1}
            )
            db.session.commit()
        except Exception as e:
            print(f"Alerta: Não foi possível realizar o autoincremento: {str(e)}")

        return redirect(url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar contrato: {str(e)}',
            'error_details': str(e)
        }), 500

@contratos_bp.route('/api/contrato/<int:contract_id>/produtos', methods=['GET'])
def get_contrato_produtos(contract_id):
    associações = ContratoProduto.query.filter_by(contrato_id=contract_id).all()
    
    produtos = []
    for assoc in associações:
        produto = Produto.query.get(assoc.produto_id)
        produtos.append({
            'id': produto.id,
            'nome': produto.nome,
            'descricao': produto.descricao,
            'quantidade': assoc.quantidade,
            'preco_unitario': float(assoc.valor_unitario or 0),
            'status': produto.status  # Assumindo que Produto tem esse campo
        })
    
    return jsonify({'status': 'success', 'produtos': produtos})

@contratos_bp.route('/get/id/contatos', methods=['GET'])
def get_id_contratos():
    search_term = request.args.get('search', '').strip()
    empresa_id = session.get('empresa')

    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    if not empresa_id:
        return jsonify({'erro': 'Empresa não definida na sessão'}), 400

    try:
        query = text("""
            SELECT * FROM contratos
            WHERE empresa_id = :empresa_id
              AND (
                    razao_social LIKE :term_like
                 OR numero = :term_exact
                 OR nome_fantasia LIKE :term_like
                 OR cnpj_cpf LIKE :term_like
              )
        """)

        params = {
            'empresa_id': empresa_id,
            'term_exact': search_term,
            'term_like': f'%{search_term}%',
        }

        result = db.session.execute(query, params)
        contratos = [dict(row._mapping) for row in result]

        total = len(contratos)
        page = 1
        per_page = total

        return render_template(
            'listar_contratos.html',
            contratos=contratos,
            total=total,
            page=page,
            per_page=per_page
        )

    except Exception as e:
        return jsonify({'erro': str(e), 'sucesso': False}), 500

@contratos_bp.route('/revendas_ativas', methods=['GET'])
def get_revendas_ativas():
    revendas = Revenda.query.filter_by(status='Ativo').order_by(Revenda.nome).all()
    resultado = [r.nome for r in revendas]
    return jsonify(resultado)

@contratos_bp.route('/get/list/clientes', methods=['GET'])
def get_list_clientes():
    empresa_id = session.get('empresa')

    if not empresa_id:
        return jsonify({'erro': 'Empresa não definida na sessão'}), 401

    # Filtra clientes ativos e pertencentes à empresa da sessão
    clientes = Cliente.query.filter_by(
        estado_atual='Ativo',
        empresa_id=empresa_id
    ).order_by(Cliente.razao_social).all()

    resultado = [{'id': c.id, 'razao_social': c.razao_social} for c in clientes]
    return jsonify(resultado)

@contratos_bp.route('/vincular-clientes', methods=['POST'])
def vincular_clientes():
    try:
        db.session.begin()

        # 1. Obter o contrato pelo número ou ID
        contrato_id = request.form.get('selecione_contrato')
        contrato = Contrato.query.get(contrato_id)

        if not contrato:
            raise ValueError("Contrato não encontrado.")

        # 2. Obter lista de IDs dos clientes a serem associados
        cliente_ids = request.form.getlist('cliente_ids')
        clientes_nao_encontrados = []

        for cliente_id in cliente_ids:
            cliente = Cliente.query.get(cliente_id)
            if cliente:
                # Verifica se já está associado
                if cliente not in contrato.clientes:
                    contrato.clientes.append(cliente)
            else:
                clientes_nao_encontrados.append(cliente_id)

        if clientes_nao_encontrados:
            raise ValueError(f"Clientes não encontrados: {', '.join(map(str, clientes_nao_encontrados))}")

        db.session.commit()
        flash('Clientes associados com sucesso.', 'success')
        return redirect(url_for('home_bp.render_contratos'))

    except ValueError as ve:
        db.session.rollback()
        flash(str(ve), 'danger')
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        flash('Erro ao associar clientes ao contrato.', 'danger')
        print(f"Erro: {e}")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

@contratos_bp.route('/get/clientes_por_contrato/<int:contrato_id>', methods=['GET'])
def clientes_por_contrato(contrato_id):
    contrato = Contrato.query.get(contrato_id)
    if not contrato:
        return jsonify([]), 404

    clientes = contrato.clientes
    return jsonify([{'id': c.id, 'razao_social': c.razao_social} for c in clientes])

@contratos_bp.route('/desvincular-clientes', methods=['POST'])
def desvincular_clientes():
    try:
        contrato_id = request.form.get('contrato_id')
        cliente_ids = request.form.getlist('cliente_ids')

        contrato = Contrato.query.get(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")

        for cliente_id in cliente_ids:
            cliente = Cliente.query.get(cliente_id)
            if cliente and cliente in contrato.clientes:
                contrato.clientes.remove(cliente)

        db.session.commit()
        flash("Clientes desvinculados com sucesso.", "success")
        return redirect(url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        flash("Erro ao desvincular clientes do contrato.", "danger")
        print(f"Erro ao desvincular: {e}")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

@contratos_bp.route('/vincular-planos', methods=['POST'])
def vincular_planos():
    empresa_id = session.get('empresa')
    try:
        db.session.begin()

        # 1. Obter o contrato pelo ID
        contrato_id = request.form.get('contrato_id')
        contrato = Contrato.query.filter_by.get(contrato_id)

        if not contrato:
            raise ValueError("Contrato não encontrado.")

        # 2. Obter lista de IDs dos planos a serem associados
        plano_ids = request.form.getlist('plano_ids')
        planos_nao_encontrados = []

        for plano_id in plano_ids:
            plano = Plano.query.get(plano_id)
            if plano:
                # Verifica se já está associado
                if plano not in contrato.planos:
                    contrato.planos.append(plano)
            else:
                planos_nao_encontrados.append(plano_id)

        if planos_nao_encontrados:
            raise ValueError(f"Planos não encontrados: {', '.join(map(str, planos_nao_encontrados))}")

        db.session.commit()
        flash('Planos associados com sucesso.', 'success')
        return redirect(url_for('home_bp.render_contratos'))

    except ValueError as ve:
        db.session.rollback()
        flash(str(ve), 'danger')
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        flash('Erro ao associar planos ao contrato.', 'danger')
        print(f"Erro: {e}")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

@contratos_bp.route('/desvincular-planos', methods=['POST'])
def desvincular_planos():
    try:
        db.session.begin()

        contrato_id = request.form.get('contrato_id')
        plano_ids = request.form.getlist('planos_ids')  # nome do campo no formulário HTML

        contrato = Contrato.query.get(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")

        if not plano_ids:
            raise ValueError("Nenhum plano selecionado para desvincular.")

        planos_removidos = []
        for plano_id in plano_ids:
            plano = Plano.query.get(plano_id)
            if plano and plano in contrato.planos:
                contrato.planos.remove(plano)
                planos_removidos.append(plano.nome)

        db.session.commit()

        flash(f"Planos desvinculados com sucesso: {', '.join(planos_removidos)}", "success")
        return redirect(url_for('home_bp.render_contratos'))

    except ValueError as ve:
        db.session.rollback()
        flash(str(ve), "danger")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao desvincular planos: {e}")
        flash("Erro ao desvincular planos do contrato.", "danger")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

@contratos_bp.route('/get/planos_por_contrato/<int:contrato_id>', methods=['GET'])
def planos_por_contrato(contrato_id):
    contrato = Contrato.query.get(contrato_id)
    if not contrato:
        return jsonify([]), 404

    planos = contrato.planos
    return jsonify([
        {
            'id': plano.id,
            'nome': plano.nome,
            'valor': str(plano.valor)
        } for plano in planos
    ])

@contratos_bp.route('/vincular-produtos', methods=['POST'])
def vincular_produtos():
    try:
        empresa_id = session.get('empresa')
        contrato_id = request.form.get('contrato_id')
        produto_ids = request.form.getlist('produto_ids')

        contrato = Contrato.query.get(contrato_id)
        if not contrato:
            flash("Contrato não encontrado.", "danger")
            return redirect(request.referrer or url_for('home_bp.render_contratos'))

        for produto_id in produto_ids:
            produto = Produto.query.get(produto_id)
            if produto:
                if produto not in contrato.produtos:
                    contrato.produtos.append(produto)

        db.session.commit()
        flash("Produtos vinculados com sucesso!", "success")
        return redirect(url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao vincular produtos: {str(e)}", "danger")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

@contratos_bp.route('/get/produtos_por_contrato/<int:contrato_id>', methods=['GET'])
def produtos_por_contrato(contrato_id):
    contrato = Contrato.query.get(contrato_id)
    if not contrato:
        return jsonify([]), 404

    produtos = contrato.produtos
    return jsonify([
        {
            'id': produto.id,
            'nome': produto.nome,
        } for produto in produtos
    ])

@contratos_bp.route('/desvincular-produtos', methods=['POST'])
def desvincular_produtos():
    try:
        contrato_id = request.form.get('contrato_id')
        produto_ids = request.form.getlist('produto_ids')

        contrato = Contrato.query.get(contrato_id)
        if not contrato:
            flash("Contrato não encontrado.", "danger")
            return redirect(request.referrer or url_for('home_bp.render_contratos'))

        for produto_id in produto_ids:
            produto = Produto.query.get(produto_id)
            if produto in contrato.produtos:
                contrato.produtos.remove(produto)

        db.session.commit()
        #flash("Produtos desvinculados com sucesso!", "success")
        return redirect(url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        #flash(f"Erro ao desvincular produtos: {str(e)}", "danger")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

@contratos_bp.route('/list/contratos_ativos', methods=['GET'])
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