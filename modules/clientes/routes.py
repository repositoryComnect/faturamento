from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from application.models.models import db, Cliente, Contrato, cliente_contrato, Revenda, Instalacao
from sqlalchemy import text
from datetime import datetime
from modules.clientes.utils import parse_date, format_date, montar_dict_cliente
from modules.utils.utils import formatar_cpf_cnpj, formatar_cep, formatar_telefone
import re

cliente_bp = Blueprint('cliente_bp', __name__)

@cliente_bp.route('/clientes/buscar-por-numero/<sequencia>', methods=['GET'])
def buscar_cliente_por_contrato(sequencia):
    empresa_id = session.get('empresa')
    try:
        cliente = (
            Cliente.query
            .filter(
                Cliente.sequencia == sequencia,
                Cliente.empresa_id == empresa_id,
                Cliente.estado_atual != 'Arquivado'
            )
            .first()
        )

        if not cliente:
            return jsonify({'error': f'Cliente {sequencia} não encontrado'}), 404

        data = {
            'sequencia': cliente.sequencia,
            'cadastramento': format_date(cliente.cadastramento),
            'atualizacao': format_date(cliente.atualizacao),
            'razao_social': cliente.razao_social or None,
            'nome_fantasia': cliente.nome_fantasia or None,
            'contato': cliente.contato_principal or None,
            'email': cliente.email or None,
            'telefone': formatar_telefone(cliente.telefone or None),
            'tipo': cliente.tipo or None,
            'cnpj_cpf': formatar_cpf_cnpj(cliente.cnpj_cpf or None),
            'im': cliente.im or None,
            'ie': cliente.ie or None,
            'revenda_nome': cliente.revenda_nome or None,
            'vendedor_nome': cliente.vendedor_nome or None,
            'tipo_servico': cliente.tipo_servico or None,
            'localidade': cliente.localidade or None,
            'regiao': cliente.regiao or None,
            'atividade': cliente.atividade or None,
            'cep': formatar_cep(cliente.cep or None),
            'endereco': cliente.endereco or None,
            'complemento': cliente.complemento or None,
            'bairro': cliente.bairro or None,
            'cidade': cliente.cidade or None,
            'cep_cobranca': cliente.cep_cobranca or None,
            'endereco_cobranca': cliente.endereco_cobranca or None,
            'cidade_cobranca': cliente.cidade_cobranca or None,
            'telefone_cobranca': cliente.telefone_cobranca or None,
            'bairro_cobranca': cliente.bairro_cobranca or None,
            'uf_cobranca': cliente.uf_cobranca or None,
            'estado': cliente.estado or None,
            'fator_juros': float(cliente.fator_juros) if cliente.fator_juros else None,
            'plano_nome': cliente.plano_nome or None,
            'observacao': cliente.observacao or None,
            'data_estado': format_date(cliente.data_estado) or None,
            'dia_vencimento': cliente.dia_vencimento or None,

            # Lista de instalações
            'instalacoes': [
                {
                    'id': inst.id,
                    'codigo_instalacao': inst.codigo_instalacao,
                    'razao_social': inst.razao_social,
                    'cep': inst.cep,
                    'endereco': inst.endereco,
                    'bairro': inst.bairro,
                    'cidade': inst.cidade,
                    'uf': inst.uf,
                    'cadastramento': format_date(inst.cadastramento),
                    'id_portal': inst.id_portal,
                    'status': inst.status,
                    'observacao': inst.observacao or '',
                    'valor_plano': float(getattr(inst, 'valor_plano', 0.00))
                }
                for inst in cliente.instalacoes
            ],

            # Lista de contratos
            'contratos': [
                {
                    'id': c.id,
                    'numero': c.numero,
                    'razao_social': c.razao_social,
                    'nome_fantasia': c.nome_fantasia,
                    'contato': c.contato,
                    'email': c.email,
                    'telefone': c.telefone,
                    'tipo': c.tipo,
                    'estado_contrato': c.estado_contrato,
                    'dia_vencimento': c.dia_vencimento,
                    'fator_juros': float(c.fator_juros) if c.fator_juros else None,
                    'data_estado': format_date(c.data_estado),
                    'revenda': c.revenda,
                    'vendedor': c.vendedor,

                    # Ajustado para N:N → pega o primeiro plano
                    'plano_id': c.planos[0].id if c.planos else None,
                    'plano_nome': c.planos[0].nome if c.planos else None,
                    'valor_plano': float(c.planos[0].valor) if c.planos and c.planos[0].valor else None,

                    # Ajustado também para produtos N:N
                    'produto_id': c.produtos[0].id if c.produtos else None,
                    'produto_nome': c.produtos[0].nome if c.produtos else None
                }
                for c in cliente.contratos
            ]
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/desvincular-instalacoes', methods=['POST'])
def desvincular_instalacoes():
    cliente_id = request.form.get('cliente_id')
    instalacao_ids = request.form.getlist('instalacao_ids')

    if not cliente_id or not instalacao_ids:
        flash('Cliente ou instalações não selecionados.', 'danger')
        return redirect(request.referrer)

    try:
        for inst_id in instalacao_ids:
            instalacao = Instalacao.query.get(inst_id)
            if instalacao and instalacao.cliente_id == int(cliente_id):
                instalacao.cliente_id = None
                db.session.add(instalacao)

        db.session.commit()
        flash(f'{len(instalacao_ids)} instalação(ões) desvinculada(s) com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao desvincular instalações: ' + str(e), 'danger')

    return redirect(request.referrer)

@cliente_bp.route('/get/clientes_com_instalacoes', methods=['GET'])
def get_clientes_com_instalacoes():
    clientes = (
        db.session.query(Cliente)
        .join(Instalacao)
        .filter(Instalacao.cliente_id == Cliente.id)
        .distinct()
        .all()
    )
    return jsonify([
        {'id': cliente.id, 'sequencia': cliente.sequencia, 'razao_social': cliente.razao_social}
        for cliente in clientes
    ])

@cliente_bp.route('/delete/cliente', methods=['POST'])
def delete_cliente():
    sequencia = request.form.get('numero')  # Agora esperamos a sequência
    action = request.form.get('action')  # 'check', 'unlink' ou 'delete'
    
    try:
        # Verificação de parâmetro
        if not sequencia:
            return jsonify({
                'error': True,
                'message': 'Número sequencial do cliente não foi informado'
            }), 400

        # Busca o cliente APENAS pela sequência
        query = """
            SELECT id, numero_contrato, razao_social, sequencia 
            FROM clientes 
            WHERE sequencia = :sequencia
        """
        cliente = db.session.execute(text(query), {'sequencia': sequencia}).fetchone()

        if not cliente:
            return jsonify({
                'error': True,
                'message': f'Cliente com sequência {sequencia} não encontrado. Verifique o número.'
            }), 404

        cliente_id = cliente[0]  # ID do cliente encontrado

        if action == 'check':
            # Verifica contratos vinculados
            contract_count = db.session.execute(
                text("SELECT COUNT(*) FROM cliente_contrato WHERE cliente_id = :cliente_id"),
                {'cliente_id': cliente_id}
            ).scalar()
            
            return jsonify({
                'success': True,
                'hasContracts': contract_count > 0,
                'count': contract_count,
                'cliente': {
                    'id': cliente_id,
                    'sequencia': cliente[3],  # Campo sequencia
                    'numero_contrato': cliente[1],  # Número do contrato
                    'razao_social': cliente[2]  # Razão social
                }
            })
        
        elif action == 'unlink':
            # Desvincula todos os contratos
            db.session.execute(
                text("DELETE FROM cliente_contrato WHERE cliente_id = :cliente_id"),
                {'cliente_id': cliente_id}
            )
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Contratos desvinculados do cliente {sequencia}'
            })
        
        elif action == 'delete':
            # Remove o cliente
            db.session.execute(
                text("UPDATE clientes SET estado_atual = 'Arquivado' WHERE id = :cliente_id"),
                {'cliente_id': cliente_id}
            )
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Cliente {sequencia} excluído com sucesso'
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': True,
            'message': f'Erro no servidor: {str(e)}'
        }), 500

@cliente_bp.route('/api/cliente/has-contracts')
def has_contracts():
    numero = request.args.get('numero')
    
    if not numero:
        return jsonify({'error': 'Número do cliente não fornecido'}), 400
    
    try:
        # Primeiro obtém o ID do cliente
        cliente_id = db.session.execute(
            text("SELECT id FROM clientes WHERE numero_contrato = :numero"),
            {'numero': numero}
        ).scalar()

        if not cliente_id:
            return jsonify({'hasContracts': False, 'count': 0})

        # Conta os contratos na tabela associativa
        count = db.session.execute(
            text("SELECT COUNT(*) FROM cliente_contrato WHERE cliente_id = :cliente_id"),
            {'cliente_id': cliente_id}
        ).scalar()

        return jsonify({
            'hasContracts': count > 0,
            'count': count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/api/contratos/numeros')
def get_numeros_contrato():
    empresa_id = session.get('empresa')
    if not empresa_id:
        return jsonify({'error': 'ID da empresa não encontrado na sessão'}), 400

    try:
        contratos = (
            Contrato.query
            .with_entities(
                Contrato.numero,
                Contrato.razao_social,
                Contrato.nome_fantasia
            )
            .filter(Contrato.empresa_id == empresa_id)
            .order_by(Contrato.numero)
            .all()
        )

        return jsonify([
            {
                'numero': c.numero,
                'razao_social': c.razao_social,
                'nome_fantasia': c.nome_fantasia
            } for c in contratos
        ])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/set/cliente', methods=['POST'])
def set_cliente():
    try:
        db.session.begin()

        cliente_data = {
            'numero_contrato': request.form.get('contract_number'),
            'sequencia': request.form.get('sequencia_cliente'),
            'cadastramento': parse_date(request.form.get('registration')),
            'atualizacao': parse_date(request.form.get('update')),
            'razao_social': request.form.get('company_name', '').strip(),
            'nome_fantasia': request.form.get('trade_name', '').strip(),
            'tipo': request.form.get('type'),
            'cnpj_cpf': request.form.get('cnpj_cpf_cliente', '').strip(),
            'ie': request.form.get('ie', '').strip(),
            'im': request.form.get('im', '').strip(),
            'contato_principal': request.form.get('contact', '').strip(),
            'email': request.form.get('address_email', '').strip(),
            'telefone': request.form.get('phone', '').strip(),
            'estado_atual': request.form.get('estado_atual', 'Ativo'),
            'revenda_nome': request.form.get('revenda_selecionada_client', '').strip(),
            'vendedor_nome': request.form.get('vendedor_selecionado_client', '').strip(),
            'tipo_servico': request.form.get('tipo_servico'),
            'localidade': request.form.get('localidade', '').strip(),
            'regiao': request.form.get('regiao', '').strip(),
            'atividade': request.form.get('atividade', '').strip(),
            'cep': request.form.get('zip_code_cep', '').strip(),
            'endereco': request.form.get('address', '').strip(),
            'complemento': request.form.get('complement', '').strip(),
            'bairro': request.form.get('neighborhood', '').strip(),
            'cidade': request.form.get('city', '').strip(),
            'estado': request.form.get('state'),
            'cep_cobranca': request.form.get('cep_cobranca'),
            'endereco_cobranca': request.form.get('endereco_cobranca'),
            'cidade_cobranca': request.form.get('cidade_cobranca'),
            'telefone_cobranca': request.form.get('telefone_cobranca'),
            'bairro_cobranca': request.form.get('bairro_cobranca'),
            'uf_cobranca': request.form.get('uf_cobranca'),
            'fator_juros': float(request.form.get('fator_juros', 0)),
            'data_estado': parse_date(request.form.get('date_estate')),
            'dia_vencimento': int(request.form.get('dia_vencimento', 10)),
            'plano_nome': request.form.get('plano', '').strip(),
            'motivo_estado': request.form.get('motivo_estado', '').strip(),
            'observacao': request.form.get('observacao', '').strip(),
            'empresa_id': session.get('empresa')
        }

        novo_cliente = Cliente(**cliente_data)
        db.session.add(novo_cliente)
        db.session.flush() 

        # 2. Associar contratos selecionados ao novo cliente
        numeros_contratos = request.form.getlist('contratos_associados')
        contratos_nao_encontrados = []

        for numero_contrato in numeros_contratos:
            contrato = Contrato.query.filter_by(numero=numero_contrato).first()

            if not contrato:
                contratos_nao_encontrados.append(numero_contrato)
                continue

            if contrato.cliente_id is None:
                contrato.cliente_id = novo_cliente.id

                db.session.execute(
                    cliente_contrato.insert().values(
                        cliente_id=novo_cliente.id,
                        contrato_id=contrato.id
                    )
                )
            else:
                contratos_nao_encontrados.append(numero_contrato)

        if contratos_nao_encontrados:
            raise ValueError(
                f"Contrato já possui cliente vinculado ou não encontrado: "
                f"{', '.join(contratos_nao_encontrados)}"
            )

        db.session.commit()

        try:
            db.session.execute(
                text("ALTER TABLE clientes AUTO_INCREMENT = :id"),
                {'id': novo_cliente.id + 1}
            )
            db.session.commit()
        except Exception:
            print("Não foi possível realizar o ajuste do AUTO_INCREMENT")

        return redirect(url_for('home_bp.render_clientes'))

    except ValueError as ve:
        db.session.rollback()
        flash(f"Erro de validação: {str(ve)}", "error")
        return redirect(request.referrer or url_for('home_bp.render_clientes'))

    except Exception as e:
        db.session.rollback()
        flash("Ocorreu um erro ao criar o cliente. Por favor, tente novamente.", "error")
        print(f"Erro: {e}")
        return redirect(request.referrer or url_for('home_bp.render_clientes'))

@cliente_bp.route('/update/cliente', methods=['POST'])
def update_cliente():
    try:
        db.session.execute(
            text("""
            UPDATE clientes SET
                cadastramento = :cadastramento,
                atualizacao = :atualizacao,
                razao_social = :razao_social,
                nome_fantasia = :nome_fantasia,
                tipo = :tipo,
                cnpj_cpf = :cnpj_cpf,
                ie = :ie,
                im = :im,
                email = :email,
                telefone = :telefone,
                cep = :cep,
                endereco = :endereco,
                complemento = :complemento,
                bairro = :bairro,
                cidade = :cidade,
                estado = :estado,
                fator_juros = :fator_juros,
                estado_atual = :estado_atual,
                data_estado = :data_estado,
                dia_vencimento = :dia_vencimento,
                plano_nome = :plano_nome,
                observacao = :observacao,
                atualizacao = CURRENT_TIMESTAMP
            WHERE sequencia = :sequencia
            """),
            {
                'sequencia': request.form.get('sequel'),
                'cadastramento': parse_date(request.form.get('registry')),
                'atualizacao': parse_date(request.form.get('registry_update')),
                'razao_social': request.form.get('razao_social_editar_popup'),
                'nome_fantasia': request.form.get('second_name'),
                'tipo': request.form.get('type'),
                'cnpj_cpf': request.form.get('cnpj_cpf_editar_popup'),
                'ie': request.form.get('state_registration'),
                'im': request.form.get('municipal_registration'),
                'email': request.form.get('email_address'),
                'telefone': request.form.get('phone_number'),
                'cep': request.form.get('postal_code'),  # se for o endereço principal
                'endereco': request.form.get('street'),
                'complemento': request.form.get('comp'),
                'bairro': request.form.get('neighbor'),
                'cidade': request.form.get('cit'),
                'estado': request.form.get('state_uf'),
                'fator_juros': request.form.get('interest_rate_factor'),
                'estado_atual': request.form.get('current_state'),
                'data_estado': parse_date(request.form.get('state_date')),
                'dia_vencimento': request.form.get('due_day'),
                'plano_nome': request.form.get('plan_name'),
                'observacao': request.form.get('observations'),
            }
        )
        db.session.commit()
        return redirect(url_for('home_bp.render_clientes'))

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar contrato: {str(e)}'
        }), 500

@cliente_bp.route('/buscar_cliente', methods=['POST'])
def buscar_cliente():
    data = request.get_json()
    termo = data.get('termo', '')
    empresa_id = session.get('empresa')
    if not termo:
        return jsonify({'success': False, 'error': 'Nenhum termo enviado'})

    # Aqui busca pela sequência, razão social, nome fantasia ou CNPJ
    cliente = Cliente.query.filter(
        Cliente.empresa_id == empresa_id,(
        (Cliente.sequencia.ilike(f"%{termo}%")) |
        (Cliente.razao_social.ilike(f"%{termo}%")) |
        (Cliente.nome_fantasia.ilike(f"%{termo}%")) |
        (Cliente.cnpj_cpf.ilike(f"%{termo}%"))
    )).first()

    if cliente:
        return jsonify({
            'success': True,
            'cliente': {
                'sequel': cliente.sequencia,
                'cadastramento': format_date(cliente.cadastramento),
                'atualizacao': format_date(cliente.atualizacao),
                'corporate_name': cliente.razao_social or None,
                'second_name': cliente.nome_fantasia or None,
                'contato': cliente.contato_principal or None,
                'email_address': cliente.email or None,
                'phone_number': formatar_telefone(cliente.telefone or None),
                'tipo': cliente.tipo or None,
                'cnpj_cpf': formatar_cpf_cnpj(cliente.cnpj_cpf or None),
                'im': cliente.im or None,
                'ie': cliente.ie or None,
                'revenda_nome': cliente.revenda_nome or None,
                'vendedor_nome': cliente.vendedor_nome or None,
                'tipo_servico': cliente.tipo_servico or None,
                'localidade': cliente.localidade or None,
                'regiao': cliente.regiao or None,
                'atividade': cliente.atividade or None,
                'cep': formatar_cep(cliente.cep or None),
                'street': cliente.endereco or None,
                'comp': cliente.complemento or None,
                'neighbor': cliente.bairro or None,
                'cit': cliente.cidade or None,
                'state_uf': cliente.estado or None,
                'fator_juros': cliente.fator_juros or None,
                'plano_nome': cliente.plano_nome or None,
                'observacao': cliente.observacao or None,
                'data_estado': cliente.data_estado if cliente.data_estado else None,
                'dia_vencimento': cliente.dia_vencimento or None
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Cliente não encontrado'})

@cliente_bp.route('/listar/clientes')
def listar_clientes():
    empresa_id = session.get('empresa')
    # Garante que, mesmo em caso de exceção, estas variáveis existam para o Jinja.
    clientes = []
    page = request.args.get('page', 1, type=int)
    per_page = 10 
    total = 0
    error = None 

    try:
        if not empresa_id:
            raise ValueError("ID da empresa não encontrado na sessão.")
            
        offset = (page - 1) * per_page
        
        # Busca clientes limitados para a página atual
        resultado = db.session.execute(
            text("SELECT * FROM clientes WHERE empresa_id = :empresa_id ORDER BY razao_social LIMIT :limit OFFSET :offset"),
            {'empresa_id': empresa_id, 'limit': per_page, 'offset': offset}
        )
        clientes = [dict(row._mapping) for row in resultado]
        
        # Busca do total de registros (Total de páginas)
        total_resultado = db.session.execute(
            text("SELECT COUNT(*) FROM clientes WHERE empresa_id = :empresa_id"),
            {'empresa_id': empresa_id}
        ).scalar()
        
        # O total pode ser None, garantimos que seja um inteiro (0)
        total = total_resultado if total_resultado is not None else 0
        
    except Exception as e:
        # Define a mensagem de erro. As outras variáveis mantêm seus valores padrão (listas/números vazios).
        print(f"Erro ao listar clientes: {str(e)}")
        error = "Não foi possível carregar os clientes. Por favor, tente novamente mais tarde."

    # Todas as variáveis esperadas pelo template são passadas, garantindo que 'total' sempre exista.
    return render_template('/listar/listar_clientes.html', 
                           clientes=clientes, 
                           page=page, 
                           per_page=per_page, 
                           total=total,
                           error=error)

@cliente_bp.route('/proxima_sequencia_cliente', methods=['GET'])
def proxima_sequencia_cliente():
    clientes = Cliente.query.all()

    numeros = []
    for c in clientes:
        if c.sequencia:
            match = re.search(r'\d+', c.sequencia)
            if match:
                numeros.append(int(match.group()))

    proximo = max(numeros) + 1 if numeros else 1
    sequencia_formatada = f"CL{proximo:04d}"  # Exemplo: CL0001

    return jsonify({'proxima_sequencia': sequencia_formatada})

@cliente_bp.route('/get/id/cliente', methods=['GET'])
def get_id_cliente():
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    try:
        # Monta a consulta principal com filtros
        base_query = """
            FROM clientes
            WHERE razao_social LIKE :term 
               OR sequencia LIKE :term 
               OR nome_fantasia LIKE :term
               OR cnpj_cpf LIKE :term
        """

        params = {'term': f'%{search_term}%', 'limit': per_page, 'offset': offset}

        # Consulta paginada
        full_query = f"SELECT * {base_query} ORDER BY razao_social LIMIT :limit OFFSET :offset"
        result = db.session.execute(text(full_query), params)
        clientes = [dict(row._asdict()) for row in result]

        # Conta total de resultados para paginação
        count_query = f"SELECT COUNT(*) {base_query}"
        total = db.session.execute(text(count_query), {'term': params['term']}).scalar()

        return render_template(
            'listar_clientes.html',
            clientes=clientes,
            total=total,
            page=page,
            per_page=per_page,
            search_term=search_term  # útil para manter o termo no campo de busca
        )

    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500

@cliente_bp.route('/revendas_ativas/cliente', methods=['GET'])
def get_revendas_ativas():
    revendas = Revenda.query.filter_by(status='Ativo').order_by(Revenda.nome).all()
    resultado = [r.nome for r in revendas]
    return jsonify(resultado)

@cliente_bp.route('/vincular-contratos-ao-cliente', methods=['POST'])
def vincular_contratos_ao_cliente():
    try:
        db.session.begin()

        # 1. Cliente selecionado
        cliente_id = request.form.get('selecione_cliente')
        cliente = Cliente.query.get(cliente_id)

        if not cliente:
            raise ValueError("Cliente não encontrado.")

        # 2. Contratos selecionados (multiple)
        contrato_ids = request.form.getlist('contrato_id')

        if not contrato_ids:
            raise ValueError("Nenhum contrato selecionado.")

        contratos_nao_encontrados = []

        # 3. Vincular contratos ao cliente
        for contrato_id in contrato_ids:
            try:
                contrato_id = int(contrato_id)  # Garantir que o id seja um inteiro
                contrato = Contrato.query.get(contrato_id)

                if contrato:
                    contrato.cliente_id = cliente.id
                else:
                    contratos_nao_encontrados.append(contrato_id)
            except ValueError:
                contratos_nao_encontrados.append(contrato_id)

        if contratos_nao_encontrados:
            raise ValueError(
                f"Contratos não encontrados: {', '.join(map(str, contratos_nao_encontrados))}"
            )

        db.session.commit()
        flash('Contratos vinculados ao cliente com sucesso.', 'success')
        return redirect(url_for('home_bp.render_contratos'))

    except ValueError as ve:
        db.session.rollback()
        flash(str(ve), 'danger')
        return redirect(request.referrer or url_for('home_bp.render_contratos'))

    except Exception as e:
        db.session.rollback()
        flash('Erro ao vincular contratos ao cliente.', 'danger')
        print(f"Erro: {e}")
        return redirect(request.referrer or url_for('home_bp.render_contratos'))


@cliente_bp.route('/clientes/<sequencia>')
def render_cliente(sequencia):
    empresa_id = session.get('empresa')
    cliente = Cliente.query.filter_by(sequencia=sequencia, empresa_id=empresa_id).first()
    return render_template('clientes.html', cliente=cliente)

@cliente_bp.route('/insert/instalacoes/cliente', methods=['POST'])
def insert_instalacoes_cliente():
    form_data = request.form.to_dict()
    cliente_id = form_data.get('cliente_selecionado')
    if not cliente_id:
        return jsonify({
            'success': False,
            'message': 'Cliente é obrigatório para vincular à instalação.'
        }), 400

    instalacao_data = {
        'codigo_instalacao': form_data.get('codigo_instalacao'),
        'razao_social': form_data.get('company'),
        'id_portal': form_data.get('id_portal'),
        'cadastramento': parse_date(form_data.get('registry')),
        'status': form_data.get('status'),
        'cep': form_data.get('cep'),
        'cidade': form_data.get('cidade'),
        'endereco': form_data.get('endereco'),
        'bairro': form_data.get('bairro'),
        'uf': form_data.get('uf'),
        'observacao': form_data.get('observacao'),
        'cliente_id': int(cliente_id)
    }

    # Verifica se instalação já existe
    if Instalacao.query.filter_by(codigo_instalacao=instalacao_data['codigo_instalacao']).first():
        return jsonify({
            'success': False,
            'message': 'Já existe uma instalação com este código.'
        }), 400

    nova_instalacao = Instalacao(**instalacao_data)
    db.session.add(nova_instalacao)
    db.session.commit()

    return redirect(url_for('home_bp.render_clientes'))

@cliente_bp.route('/clientes/buscar-por-numero-listagem/<sequencia>', methods=['GET'])
def buscar_cliente_listagem(sequencia):
    empresa_id = session.get('empresa')
    try:
        cliente = (
            Cliente.query
            .filter(
                Cliente.sequencia == sequencia,
                Cliente.empresa_id == empresa_id,
                #Cliente.estado_atual != 'Arquivado'
            )
            .first()
        )

        if not cliente:
            return jsonify({'error': f'Cliente {sequencia} não encontrado'}), 404

        data = {
            'sequencia': cliente.sequencia,
            'cadastramento': format_date(cliente.cadastramento),
            'atualizacao': format_date(cliente.atualizacao),
            'razao_social': cliente.razao_social or None,
            'nome_fantasia': cliente.nome_fantasia or None,
            'contato': cliente.contato_principal or None,
            'email': cliente.email or None,
            'telefone': formatar_telefone(cliente.telefone or None),
            'tipo': cliente.tipo or None,
            'cnpj_cpf': formatar_cpf_cnpj(cliente.cnpj_cpf or None),
            'im': cliente.im or None,
            'ie': cliente.ie or None,
            'revenda_nome': cliente.revenda_nome or None,
            'vendedor_nome': cliente.vendedor_nome or None,
            'tipo_servico': cliente.tipo_servico or None,
            'localidade': cliente.localidade or None,
            'regiao': cliente.regiao or None,
            'atividade': cliente.atividade or None,
            'cep': formatar_cep(cliente.cep or None),
            'endereco': cliente.endereco or None,
            'complemento': cliente.complemento or None,
            'bairro': cliente.bairro or None,
            'cidade': cliente.cidade or None,
            'cep_cobranca': cliente.cep_cobranca or None,
            'endereco_cobranca': cliente.endereco_cobranca or None,
            'cidade_cobranca': cliente.cidade_cobranca or None,
            'telefone_cobranca': cliente.telefone_cobranca or None,
            'bairro_cobranca': cliente.bairro_cobranca or None,
            'uf_cobranca': cliente.uf_cobranca or None,
            'estado': cliente.estado or None,
            'fator_juros': float(cliente.fator_juros) if cliente.fator_juros else None,
            'plano_nome': cliente.plano_nome or None,
            'observacao': cliente.observacao or None,
            'data_estado': format_date(cliente.data_estado) or None,
            'dia_vencimento': cliente.dia_vencimento or None,

            # NOVO: Lista de instalações vinculadas ao cliente
            'instalacoes': [
                {
                    'id': inst.id,
                    'codigo_instalacao': inst.codigo_instalacao,
                    'razao_social': inst.razao_social,
                    'cep': inst.cep,
                    'endereco': inst.endereco,
                    'bairro': inst.bairro,
                    'cidade': inst.cidade,
                    'uf': inst.uf,
                    'cadastramento': format_date(inst.cadastramento),
                    'id_portal': inst.id_portal,
                    'status': inst.status,
                    'observacao': inst.observacao or '',
                    'valor_plano': float(getattr(inst, 'valor_plano', 0.00)),
                }
                for inst in cliente.instalacoes
            ],

            'contratos': [
                {
                    'id': c.id,
                    'numero': c.numero,
                    'razao_social': c.razao_social,
                    'nome_fantasia': c.nome_fantasia,
                    'contato': c.contato,
                    'email': c.email,
                    'telefone': c.telefone,
                    'tipo': c.tipo,
                    'estado_contrato': c.estado_contrato,
                    'dia_vencimento': c.dia_vencimento,
                    'fator_juros': float(c.fator_juros) if c.fator_juros else None,
                    'data_estado': format_date(c.data_estado),
                    'revenda': c.revenda,
                    'vendedor': c.vendedor,

                    # Ajustado para N:N → pega o primeiro plano
                    'plano_id': c.planos[0].id if c.planos else None,
                    'plano_nome': c.planos[0].nome if c.planos else None,
                    'valor_plano': float(c.planos[0].valor) if c.planos and c.planos[0].valor else None,

                    # Ajustado também para produtos N:N
                    'produto_id': c.produtos[0].id if c.produtos else None,
                    'produto_nome': c.produtos[0].nome if c.produtos else None
                }
                for c in cliente.contratos
            ]
        }

        return render_template('clientes.html',
                               cliente = data,
                               instalacoes = data['instalacoes']
                               )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes/proximo/<sequencia>', methods=['GET'])
def buscar_proximo_cliente(sequencia):
    empresa_id = session.get('empresa')

    try:
        atual = (
            Cliente.query
            .filter(
                Cliente.sequencia == sequencia,
                Cliente.empresa_id == empresa_id,
                Cliente.estado_atual != 'Arquivado'
            )
            .first()
        )

        if not atual:
            return jsonify({'error': 'Cliente atual não encontrado'}), 404

        proximo = (
            Cliente.query
            .filter(
                Cliente.sequencia > atual.sequencia,
                Cliente.empresa_id == empresa_id,
                Cliente.estado_atual != 'Arquivado'
            )
            .order_by(Cliente.sequencia.asc())
            .first()
        )

        if not proximo:
            return jsonify({}), 200

        return jsonify(montar_dict_cliente(proximo))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cliente_bp.route('/clientes/buscar-instalacao-listagem/<codigo>', methods=['GET'])
def buscar_instalacao_listagem(codigo):
    empresa_id = session.get('empresa')
    try:
        instalacao = (
            Instalacao.query
            .filter(
                Instalacao.codigo_instalacao == codigo,
                Instalacao.empresa_id == empresa_id,
            )
            .first()
        )

        if not instalacao:
            return jsonify({'error': f'Instalação {codigo} não encontrada'}), 404

        data = {
            'codigo': instalacao.codigo_instalacao,
            'cadastramento': format_date(instalacao.cadastramento),
            'endereco': instalacao.endereco,
            'status': instalacao.status,
            'observacao': instalacao.observacao,
            'cep': instalacao.cep,
            'bairro': instalacao.bairro,
            'uf': instalacao.uf,
            'id_portal': instalacao.id_portal,
            'razao_social': instalacao.razao_social,
        }

        return render_template('instalacoes.html',
                               instalacoes = data,
                               )

    except Exception as e:
        return jsonify({'error': str(e)}), 500