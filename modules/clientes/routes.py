from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from application.models.models import db, Cliente, Contrato, cliente_contrato, Revenda, Instalacao
from sqlalchemy import text
from datetime import datetime
import re

cliente_bp = Blueprint('cliente_bp', __name__)

'''@cliente_bp.route('/clientes/buscar-por-numero/<sequencia>', methods=['GET'])
def buscar_cliente_por_contrato(sequencia):
    try:
        sequencia = Cliente.query.filter_by(sequencia=sequencia).first()
        if not sequencia:
            return jsonify({'error': f'Cliente {sequencia} não encontrado'}), 404

        # Função auxiliar para formatar datas
        def format_date(date):
            return date.strftime('%d/%m/%Y') if date else None

        data = {
            'sequencia': sequencia.sequencia,
            'cadastramento': format_date(sequencia.cadastramento),
            'atualizacao': format_date(sequencia.atualizacao),
            'razao_social': sequencia.razao_social or None,
            'nome_fantasia': sequencia.nome_fantasia or None,
            'contato': sequencia.contato_principal or None,
            'email': sequencia.email or None,
            'telefone': sequencia.telefone or None,
            'tipo': sequencia.tipo or None,
            'cnpj': sequencia.cnpj or None,
            'im' : sequencia.im or None,
            'ie' : sequencia.ie or None,
            'revenda_nome': sequencia.revenda_nome or None,
            'vendedor_nome': sequencia.vendedor_nome or None,
            'tipo_servico' : sequencia.tipo_servico or None,
            'localidade' : sequencia.localidade or None, 
            'regiao' : sequencia.regiao or None,
            'atividade' : sequencia.atividade or None,
            'cep': sequencia.cep or None,
            'endereco': sequencia.endereco or None,
            'complemento': sequencia.complemento or None,
            'bairro' :sequencia.bairro or None,
            'cidade' : sequencia.cidade or None,
            'cep_cobranca': sequencia.cep_cobranca or None,
            'endereco_cobranca': sequencia.endereco_cobranca or None,
            'cidade_cobranca': sequencia.cidade_cobranca or None,
            'telefone_cobranca': sequencia.telefone_cobranca or None,
            'bairro_cobranca': sequencia.bairro_cobranca or None,
            'uf_cobranca': sequencia.uf_cobranca or None,
            'estado' : sequencia.estado or None,
            'fator_juros': sequencia.fator_juros or None,
            'plano_nome': sequencia.plano_nome or None,
            'observacao': sequencia.observacao or None,
            'data_estado': format_date(sequencia.data_estado) or None,
            'dia_vencimento': sequencia.dia_vencimento or None

            
        }
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500'''


@cliente_bp.route('/clientes/buscar-por-numero/<sequencia>', methods=['GET'])
def buscar_cliente_por_contrato(sequencia):
    empresa_id = session.get('empresa')
    try:
        cliente = Cliente.query.filter_by(sequencia=sequencia, empresa_id=empresa_id).first()
        if not cliente:
            return jsonify({'error': f'Cliente {sequencia} não encontrado'}), 404

        # Função auxiliar para formatar datas
        def format_date(date):
            return date.strftime('%d/%m/%Y') if date else None

        data = {
            'sequencia': cliente.sequencia,
            'cadastramento': format_date(cliente.cadastramento),
            'atualizacao': format_date(cliente.atualizacao),
            'razao_social': cliente.razao_social or None,
            'nome_fantasia': cliente.nome_fantasia or None,
            'contato': cliente.contato_principal or None,
            'email': cliente.email or None,
            'telefone': cliente.telefone or None,
            'tipo': cliente.tipo or None,
            'cnpj': cliente.cnpj or None,
            'im': cliente.im or None,
            'ie': cliente.ie or None,
            'revenda_nome': cliente.revenda_nome or None,
            'vendedor_nome': cliente.vendedor_nome or None,
            'tipo_servico': cliente.tipo_servico or None,
            'localidade': cliente.localidade or None,
            'regiao': cliente.regiao or None,
            'atividade': cliente.atividade or None,
            'cep': cliente.cep or None,
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
                    'valor_plano': float(getattr(inst, 'valor_plano', 0.00))  # Proteção caso não exista
                }
                for inst in cliente.instalacoes
            ]
        }
        print(data)

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
                text("DELETE FROM clientes WHERE id = :cliente_id"),
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
    def parse_date(date_str):
            if not date_str:
                return None
            try:
                for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                return None
            except Exception:
                return None

    try:
        # Iniciar transação (equivalente ao BEGIN TRANSACTION)
        db.session.begin()

        # 1. Inserir o novo cliente (equivalente ao primeiro INSERT)
        cliente_data = {
            'numero_contrato': request.form.get('contract_number'),
            'sequencia': request.form.get('sequencia_cliente'),
            'cadastramento': parse_date(request.form.get('registration')),
            'atualizacao': parse_date(request.form.get('update')),
            'razao_social': request.form.get('company_name', '').strip(),
            'nome_fantasia': request.form.get('trade_name', '').strip(),
            'tipo': request.form.get('type'),
            'cnpj': request.form.get('cnpj_cpf', '').strip(),
            'ie': request.form.get('ie', '').strip(),
            'im': request.form.get('im', '').strip(),
            'contato_principal': request.form.get('contact', '').strip(),
            'email': request.form.get('address_email', '').strip(),
            'telefone': request.form.get('phone', '').strip(),
            'revenda_nome': request.form.get('revenda_selecionada_client', '').strip(),
            'vendedor_nome': request.form.get('vendedor_selecionado_client', '').strip(),
            'tipo_servico': request.form.get('tipo_servico'),
            'localidade': request.form.get('localidade', '').strip(),
            'regiao': request.form.get('regiao', '').strip(),
            'atividade': request.form.get('atividade', '').strip(),
            'cep': request.form.get('zip_code', '').strip(),
            'endereco': request.form.get('address', '').strip(),
            'complemento': request.form.get('complement', '').strip(),
            'bairro': request.form.get('neighborhood', '').strip(),
            'cidade': request.form.get('city', '').strip(),
            'cep_cobranca': request.form.get('cep_cobranca'),
            'endereco_cobranca': request.form.get('endereco_cobranca'),
            'cidade_cobranca': request.form.get('cidade_cobranca'),
            'telefone_cobranca': request.form.get('telefone_cobranca'),
            'bairro_cobranca': request.form.get('bairro_cobranca'),
            'uf_cobranca': request.form.get('uf_cobranca'),
            'estado': request.form.get('state'),
            'fator_juros': float(request.form.get('fator_juros', 0)),
            'estado_atual': request.form.get('estado_atual', 'Ativo'),
            'data_estado': parse_date(request.form.get('date_estate')),
            'dia_vencimento': int(request.form.get('dia_vencimento', 10)),
            'plano_nome': request.form.get('plano', '').strip(),
            'motivo_estado': request.form.get('motivo_estado', '').strip(),
            'observacao': request.form.get('observacao', '').strip(),
            'empresa_id': session.get('empresa')
        }

        # Validação mínima dos campos obrigatórios
        if not cliente_data['razao_social']:
            raise ValueError("Razão Social é obrigatória")
        
        if not cliente_data['cnpj']:
            raise ValueError("CNPJ/CPF é obrigatório")

        novo_cliente = Cliente(**cliente_data)
        db.session.add(novo_cliente)
        db.session.flush()  # Força o INSERT para obter o ID (equivalente ao seu SELECT do ID)

        # 2. Obter o ID do cliente (já temos em novo_cliente.id)

        # 3. Processar associação com contratos
        numeros_contratos = request.form.getlist('contratos_associados')
        contratos_nao_encontrados = []

        for numero_contrato in numeros_contratos:
            # Buscar contrato pelo número (equivalente ao seu terceiro bloco SQL)
            contrato = Contrato.query.filter_by(numero=numero_contrato).first()
            
            if contrato:
                # 4. Associar cliente ao contrato (equivalente ao quarto INSERT)
                stmt = cliente_contrato.insert().values(
                    cliente_id=novo_cliente.id,
                    contrato_id=contrato.id
                )
                db.session.execute(stmt)
            else:
                contratos_nao_encontrados.append(numero_contrato)

        # Se algum contrato não foi encontrado, cancelar a operação
        if contratos_nao_encontrados:
            raise ValueError(f"Contratos não encontrados: {', '.join(contratos_nao_encontrados)}")

        # Commit da transação (equivalente ao COMMIT)
        db.session.commit()

        # Tentativa de ajuste do autoincrement (mantendo sua lógica original)
        try:
            db.session.execute(
                text("ALTER TABLE clientes AUTO_INCREMENT = :id"),
                {'id': novo_cliente.id + 1}
            )
            db.session.commit()
        except Exception as e:
            print("Não foi possível realizar o autoincrement")

        return redirect(url_for('home_bp.render_clientes'))

    except ValueError as ve:
        db.session.rollback()
        flash(f"Erro de validação: {str(ve)}", "error")
        return redirect(request.referrer or url_for('home_bp.render_clientes'))

    except Exception as e:
        db.session.rollback()
        flash("Ocorreu um erro ao criar o cliente. Por favor, tente novamente.", "error")
        return redirect(request.referrer or url_for('home_bp.render_clientes'))
    
@cliente_bp.route('/update/cliente', methods=['POST'])
def update_cliente():
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            return None

    try:

        db.session.execute(
        text("""
        UPDATE clientes SET
            
            cadastramento = :cadastramento,
            atualizacao = :atualizacao,
            razao_social = :razao_social,
            nome_fantasia = :nome_fantasia,
            tipo = :tipo,
            cnpj = :cnpj,
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
                'razao_social': request.form.get('corporate_name'),
                'nome_fantasia': request.form.get('second_name'),
                'tipo': request.form.get('type'),
                'cnpj': request.form.get('cpf_cnpj'),
                'ie': request.form.get('state_registration'),
                'im': request.form.get('municipal_registration'),
                'email': request.form.get('email_address'),
                'telefone': request.form.get('phone_number'),
                'cep': request.form.get('postal_code'),
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
        return redirect(url_for(('home_bp.render_clientes')))

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

    def format_date(date):
            return date.strftime('%d/%m/%Y') if date else None

    if not termo:
        return jsonify({'success': False, 'error': 'Nenhum termo enviado'})

    # Aqui busca pela sequência, razão social, nome fantasia ou CNPJ
    cliente = Cliente.query.filter(
        Cliente.empresa_id == empresa_id,(
        (Cliente.sequencia.ilike(f"%{termo}%")) |
        (Cliente.razao_social.ilike(f"%{termo}%")) |
        (Cliente.nome_fantasia.ilike(f"%{termo}%")) |
        (Cliente.cnpj.ilike(f"%{termo}%"))
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
                'phone_number': cliente.telefone or None,
                'tipo': cliente.tipo or None,
                'cpf_cnpj': cliente.cnpj or None,
                'im': cliente.im or None,
                'ie': cliente.ie or None,
                'revenda_nome': cliente.revenda_nome or None,
                'vendedor_nome': cliente.vendedor_nome or None,
                'tipo_servico': cliente.tipo_servico or None,
                'localidade': cliente.localidade or None,
                'regiao': cliente.regiao or None,
                'atividade': cliente.atividade or None,
                'cep': cliente.cep or None,
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
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Itens por página
        
        offset = (page - 1) * per_page
        resultado = db.session.execute(
            text("SELECT * FROM clientes WHERE empresa_id = :empresa_id ORDER BY razao_social LIMIT :limit OFFSET :offset"),
            {'empresa_id': empresa_id,'limit': per_page, 'offset': offset}
        )
        
        clientes = [dict(row._mapping) for row in resultado]
        total = db.session.execute(text(f"SELECT COUNT(*) FROM clientes WHERE empresa_id = {empresa_id}")).scalar()
        
        return render_template('listar_clientes.html', clientes=clientes, page=page, per_page=per_page, total=total)
        
    except Exception as e:
        print(f"Erro ao listar clientes: {str(e)}")
        return render_template('listar_clientes.html', error="Não foi possível carregar os clientes")

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
               OR numero_contrato LIKE :term 
               OR nome_fantasia LIKE :term
               OR cnpj LIKE :term
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

@cliente_bp.route('/insert/instalacoes/cliente', methods=['POST'])
def insert_instalacoes_cliente():
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