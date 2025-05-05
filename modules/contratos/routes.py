from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from application.models.models import Contrato, db, Cliente, Produto, Plano
from datetime import datetime
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
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    resultado = [{'id': p.id, 'nome': p.nome} for p in produtos]
    return jsonify(resultado)

@contratos_bp.route('/planos_ativos', methods=['GET'])
def planos_ativos():
    planos = Plano.query.order_by(Plano.nome).all()
    resultado = [{'id': p.id, 'nome': p.nome, 'valor': str(p.valor)} for p in planos]
    return jsonify(resultado)

'''@contratos_bp.route('/api/contrato/<int:contrato_id>', methods=['GET'])
def contrato_detalhes_api(contrato_id):
    # Buscando o contrato com o plano associado
    contrato = db.session.query(Contrato, Plano).join(Plano, Contrato.plano_id == Plano.id).filter(Contrato.id == contrato_id).first()

    if contrato:
        contrato_data = {
            'plano_nome': contrato[1].nome,
            'valor_plano': str(contrato[1].valor),
            'valor_contrato': str(contrato[0].fator_juros)  # Exemplo de valor, ajuste conforme necessário
        }
        return jsonify(contrato_data)
    else:
        return jsonify({'error': 'Contrato não encontrado'}), 404'''

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
                    'sequencia': contrato_id  # se quiser exibir algo como sequência
                }
            })

        elif action == 'unlink':
            db.session.execute(text("DELETE FROM cliente_contrato WHERE contrato_id = :id"), {'id': contrato_id})
            db.session.commit()
            return jsonify({'success': True, 'message': f'Contrato {numero} desvinculado com sucesso'})

        elif action == 'delete':
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

    if not termo:
        return jsonify({'success': False, 'error': 'Nenhum termo enviado'})
    
    def format_date(date):
            return date.strftime('%d/%m/%Y') if date else None

    # Aqui buscamos pelo número do contrato, razão social, nome fantasia ou ID do contrato
    contrato = Contrato.query.filter(
        (Contrato.numero.ilike(f"%{termo}%")) |
        (Contrato.razao_social.ilike(f"%{termo}%")) |
        (Contrato.nome_fantasia.ilike(f"%{termo}%")) |
        (Contrato.id_matriz_portal.ilike(f"%{termo}%"))
    ).first()

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
                'zip_code': contrato.cep or None,
                'cnpj_cpf': contrato.cnpj or None,
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
        return jsonify({'success': False, 'error': 'Contrato não encontrado'})

@contratos_bp.route('/contratos/alterar', methods=['POST'])
def alterar_contrato():
    try:
        numero = request.form.get('contract_number')
        razao_social = request.form.get('company_name')
        nome_fantasia = request.form.get('trade_name')
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
        contrato_revenda = request.form.get('id_matriz_portal')
        faturamento_contrato = request.form.get('contract_value')
        faturamento_contrato = int(faturamento_contrato) if faturamento_contrato.strip() else None
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
                'motivo_estado': motivo_estado
            }
        )
        db.session.commit()

        return redirect(url_for(('home_bp.render_contratos')))

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
        page = request.args.get('page', 1, type=int)
        per_page = 10  
        
        offset = (page - 1) * per_page
        resultado = db.session.execute(
            text("SELECT * FROM contratos ORDER BY numero LIMIT :limit OFFSET :offset"),
            {'limit': per_page, 'offset': offset}
        )
        
        contratos = [dict(row._mapping) for row in resultado]
        total = db.session.execute(text("SELECT COUNT(*) FROM contratos")).scalar()
        
        return render_template('listar_contratos.html', 
                            contratos=contratos,
                            page=page,
                            per_page=per_page,
                            total=total)
        
    except Exception as e:
        print(f"Erro ao listar clientes: {str(e)}")
        return render_template('listar_contratos.html', 
                            error="Não foi possível carregar os clientes")

@contratos_bp.route('/contratos/buscar-por-numero/<numero>', methods=['GET'])
def buscar_contrato_por_numero(numero):
    try:
        contrato = Contrato.query.filter_by(numero=numero).first()
        
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
            'cnpj': contrato.cnpj or None,
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
            'localidade': c.localidade or None,
            'atividade': c.atividade or None,
            'regiao': c.regiao or None,
            'estado_atual': c.estado_atual or None,
            'numero_contrato_cadastrado': c.numero_contrato
        } for c in contrato.clientes] if contrato.clientes else []

        # Planos associados (N:N)
        data['planos'] = [{
            'id': p.id,
            'codigo': p.codigo,
            'nome': p.nome,
            'valor': float(p.valor),
            'status': 'Ativo'  # Pode ser ajustado conforme sua regra
        } for p in contrato.planos] if contrato.planos else []

        return jsonify(data)
    
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({'error': 'Erro ao processar a requisição'}), 500

@contratos_bp.route('/set_contrato', methods=['POST'])
def set_contrato():
    try:
        db.session.rollback()
        form_data = request.form.to_dict()
        
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
        
        contrato_data = {
            'numero': form_data.get('numero_contrato'),
            'cadastramento': parse_date(form_data.get('cadastramento')),
            'atualizacao': parse_date(form_data.get('atualizacao')),
            'tipo': form_data.get('tipo_contrato'),
            'id_matriz_portal': form_data.get('portal_id'),
            'responsavel': form_data.get('responsavel'),
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
            'estado_produto': form_data.get('produto'),
            'estado_contrato': form_data.get('estado_contrato'),
            'data_estado': parse_date(form_data.get('data_estado')),
            'motivo_estado': form_data.get('motivo_estado'),
            
        }
        
        if Contrato.query.filter_by(numero=contrato_data['numero']).first():
            return jsonify({
                'success': False,
                'message': 'Já existe um contrato com este número'
            }), 400
        
        novo_contrato = Contrato(**contrato_data)
        db.session.add(novo_contrato)
        db.session.commit()
        
        try:
            db.session.execute(
                "ALTER TABLE contratos AUTO_INCREMENT = : id",
                {'id': novo_contrato.id + 1}
            )
            db.session.commit()
        except Exception as e:
            print(f"Alerta: Não foi possível realizar o autoincremento: {str(e)}")
        
        return redirect(url_for(('home_bp.render_contratos')))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar contrato: {str(e)}',
            'error_details': str(e)
        }), 500
    
@contratos_bp.route('/get/id/contatos', methods=['GET'])
def get_id_contratos():
    search_term = request.args.get('search', '').strip()
    
    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    try:
        query = text("""
            SELECT * FROM contratos
            WHERE razao_social LIKE :term 
               OR numero LIKE :term 
               OR nome_fantasia LIKE :term
               OR cnpj LIKE :term
        """)

        result = db.session.execute(query, {'term': f'%{search_term}%'})
        contratos = [dict(row._asdict()) for row in result]
        
        return render_template('listar_contratos.html', contratos=contratos)
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500