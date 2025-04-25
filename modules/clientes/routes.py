from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from application.models.models import db, Cliente
from sqlalchemy import text
from datetime import datetime


cliente_bp = Blueprint('cliente_bp', __name__)

@cliente_bp.route('/clientes/buscar-por-numero/<sequencia>', methods=['GET'])
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
            'estado' : sequencia.estado or None,
            'fator_juros': sequencia.fator_juros or None,
            'plano_nome': sequencia.plano_nome or None,
            'observacao': sequencia.observacao or None,
            'data_estado': format_date(sequencia.data_estado) or None,
            'dia_vencimento': sequencia.dia_vencimento or None
        }
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500





@cliente_bp.route('/delete/cliente', methods=['POST'])
def delete_cliente():
    numero = request.form.get('numero')
    try:
        db.session.execute(
            text("DELETE FROM clientes WHERE numero_contrato = :numero"),
            {'numero': numero}
        )
        db.session.commit()

    except Exception as e:
        print(f"Alerta: Não foi possível realizar a exclusão do cliente: {str(e)}")
    
    return redirect(url_for('home_bp.render_clientes'))





@cliente_bp.route('/set/cliente', methods=['POST'])
def set_cliente():
    try:
        # Verificar e resetar transações pendentes
        db.session.rollback()
        
        # Pegar todos os dados do formulário
        form_data = request.form.to_dict()
        
        # Função melhorada para converter datas
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                # Tenta vários formatos de data
                for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                return None
            except Exception:
                return None
        
        # Criar dicionário com os dados formatados
        cliente_data = {
            'numero_contrato': form_data.get('numero_contrato'),
            'sequencia': form_data.get('sequencia'),
            'cadastramento': parse_date(form_data.get('cadastramento')),
            'atualizacao': parse_date(form_data.get('atualizacao')),
            'razao_social': form_data.get('razao_social'),
            'nome_fantasia': form_data.get('nome_fantasia'),
            'tipo': form_data.get('tipo'),
            'cnpj': form_data.get('numero_documento'),
            'ie': form_data.get('ie'),
            'im': form_data.get('im'),
            'contato_principal': form_data.get('contato_principal'),
            'email': form_data.get('email'),
            'telefone': form_data.get('telefone'),
            'revenda_nome': form_data.get('revenda'),
            'vendedor_nome': form_data.get('vendedor'),
            'tipo_servico': form_data.get('tipo_servico'),
            'localidade': form_data.get('localidade'),
            'regiao': form_data.get('regiao'),
            'atividade': form_data.get('atividade'),
            'cep': form_data.get('cep'),
            'endereco': form_data.get('endereco'),
            'complemento': form_data.get('complemento'),
            'bairro': form_data.get('bairro'),
            'cidade': form_data.get('cidade'),
            'estado': form_data.get('uf'),
            'fator_juros': form_data.get('fator_juros'),
            'estado_atual': form_data.get('estado_atual'),
            'data_estado': parse_date(form_data.get('data_estado')),
            'dia_vencimento': form_data.get('dia_vencimento'),
            'plano_nome': form_data.get('plano'),
            'motivo_estado': form_data.get('motivo_estado'),
            'observacao': form_data.get('observacao')
        }
        
        novo_cliente = Cliente(**cliente_data)
        db.session.add(novo_cliente)
        db.session.commit()
        
        try:
            db.session.execute(
                "ALTER TABLE contratos AUTO_INCREMENT = : id",
                {'id': novo_cliente.id + 1}
            )
            db.session.commit()
        except Exception as e:
            print(f"Alerta: Não foi possível realizar o autoincremento: {str(e)}")
        
        return redirect(url_for(('home_bp.render_clientes')))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar cliente: {str(e)}',
            'error_details': str(e)
        }), 500
    




@cliente_bp.route('/update/cliente', methods=['POST'])
def update_cliente():
    try:
        numero_contrato = request.form.get('numero_contrato')
        sequencia = request.form.get('sequencia')
        cadastramento= request.form.get('cadastramento')
        atualizacao= request.form.get('atualizacao')
        razao_social= request.form.get('razao_social')
        nome_fantasia= request.form.get('nome_fantasia')
        tipo= request.form.get('tipo')
        cnpj= request.form.get('numero_documento')
        ie= request.form.get('ie')
        im= request.form.get('im')
        contato_principal= request.form.get('contato_principal')
        email= request.form.get('email')
        telefone= request.form.get('telefone')
        revenda_nome= request.form.get('revenda')
        vendedor_nome= request.form.get('vendedor')
        tipo_servico= request.form.get('tipo_servico')
        localidade= request.form.get('localidade')
        regiao= request.form.get('regiao')
        atividade= request.form.get('atividade')
        cep= request.form.get('cep')
        endereco= request.form.get('endereco')
        complemento= request.form.get('complemento')
        bairro= request.form.get('bairro')
        cidade= request.form.get('cidade')
        estado= request.form.get('uf')
        fator_juros= request.form.get('fator_juros')
        estado_atual= request.form.get('estado_atual')
        data_estado= request.form.get('data_estado')
        dia_vencimento= request.form.get('dia_vencimento')
        plano_nome= request.form.get('plano')
        motivo_estado= request.form.get('motivo_estado')
        observacao= request.form.get('observacao')

        db.session.execute(
            text("""
                UPDATE clientes SET
                    sequencia = :sequencia,
                    cadastramento = :cadastramento,
                    atualizacao = :atualizacao,
                    razao_social = :razao_social,
                    nome_fantasia = :nome_fantasia,
                    tipo = :tipo,
                    cnpj = :cnpj,
                    ie = :ie,
                    im = :im,
                    contato_principal = :contato_principal,
                    email = :email,
                    telefone = :telefone,
                    revenda_nome = :revenda_nome,
                    vendedor_nome = :vendedor_nome,
                    tipo_servico = :tipo_servico,
                    localidade = :localidade,
                    regiao = :regiao,
                    atividade = :atividade,
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
                    motivo_estado = :motivo_estado,
                    observacao = :observacao,
                    atualizacao = CURRENT_TIMESTAMP
                WHERE numero_contrato = :numero_contrato
            """),
            {
                'numero_contrato': numero_contrato,
                'sequencia': sequencia,
                'cadastramento': cadastramento,
                'atualizacao': atualizacao,
                'razao_social': razao_social,
                'nome_fantasia': nome_fantasia,
                'tipo': tipo,
                'cnpj': cnpj,
                'ie': ie,
                'im': im,
                'contato_principal': contato_principal,
                'email': email,
                'telefone': telefone,
                'revenda_nome': revenda_nome,
                'vendedor_nome': vendedor_nome,
                'tipo_servico': tipo_servico,
                'localidade': localidade,
                'regiao': regiao,
                'atividade': atividade,
                'cep': cep,
                'endereco': endereco,
                'complemento': complemento,
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado,
                'fator_juros': fator_juros,
                'estado_atual': estado_atual,
                'data_estado': data_estado,
                'dia_vencimento': dia_vencimento,
                'plano_nome': plano_nome,
                'motivo_estado': motivo_estado,
                'observacao': observacao
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
    





@cliente_bp.route('/listar/clientes')
def listar_clientes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Itens por página
        
        offset = (page - 1) * per_page
        resultado = db.session.execute(
            text("SELECT * FROM clientes ORDER BY razao_social LIMIT :limit OFFSET :offset"),
            {'limit': per_page, 'offset': offset}
        )
        
        clientes = [dict(row._mapping) for row in resultado]
        total = db.session.execute(text("SELECT COUNT(*) FROM clientes")).scalar()
        
        return render_template('listar_clientes.html', clientes=clientes, page=page, per_page=per_page, total=total)
        
    except Exception as e:
        print(f"Erro ao listar clientes: {str(e)}")
        return render_template('listar_clientes.html', error="Não foi possível carregar os clientes")





@cliente_bp.route('/get/id/cliente', methods=['GET'])
def get_id_cliente():
    search_term = request.args.get('search', '').strip()
    
    if not search_term:
        return jsonify({'erro': 'Termo de pesquisa não fornecido'}), 400

    try:
        # Consulta SQL usando text() para segurança
        query = text("""
            SELECT * FROM clientes
            WHERE razao_social LIKE :term 
               OR numero_contrato LIKE :term 
               OR nome_fantasia LIKE :term
               OR cnpj LIKE :term
            """)
        
        # Executa a consulta com parâmetros
        result = db.session.execute(query, {'term': f'%{search_term}%'})
        
        # Converte os resultados para dicionário
        clientes = [dict(row._asdict()) for row in result]
        
        return render_template('listar_clientes.html', clientes=clientes)
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500