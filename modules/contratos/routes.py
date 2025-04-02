from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from application.models.models import Contrato, db
from datetime import datetime

contratos_bp = Blueprint('contratos_bp', __name__)


@contratos_bp.route('/contratos/<int:contrato_id>', methods=['GET'])
def get_contrato(contrato_id):
    try:
        contrato = Contrato.query.get(contrato_id)
        if not contrato:
            return jsonify({"error": "Contrato não encontrado"}), 404
        
        print(contrato)
        
        # Converter para dicionário
        contrato_data = {
            'id': contrato.id,
            'numero': contrato.numero,
            # Adicione todos os outros campos aqui
        }
        return jsonify(contrato_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Renderiza a página de contratos com as informações
@contratos_bp.route('/contratos')
def list_contratos():
    try:
        contrato = Contrato.query.first()
        if contrato:
            return redirect(url_for('contratos_bp.view_contrato', contrato_id=contrato.id))
        else:
            flash('Nenhum contrato encontrado no banco de dados', 'info')
            return render_template('contratos.html', contrato=None)
    except Exception as e:
        flash(f'Erro ao acessar contratos: {str(e)}', 'error')
        return render_template('contratos.html', contrato=None)


# Realiza a consulta com o número do contrato.
@contratos_bp.route('/contratos/buscar-por-numero/<numero>', methods=['GET'])
def buscar_contrato_por_numero(numero):
    try:
        numero = str(numero).strip()
        contrato = Contrato.query.filter_by(numero=numero).first()
        
        if not contrato:
            return jsonify({'error': f'Contrato {numero} não encontrado'}), 404
        
        # Função auxiliar para formatar datas
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
            'endereco': contrato.endereco or None,
            'complemento': contrato.complemento or None,
            'bairro': contrato.bairro or None,
            'cidade': contrato.cidade or None,
            'estado': contrato.estado or None,
            'cobranca_cep': contrato.cobranca_cep or None,
            'cobranca_endereco': contrato.cobranca_endereco or None,
            'cobranca_bairro': contrato.cobranca_bairro or None,
            'cobranca_cidade': contrato.cobranca_cidade or None,
            'cobranca_estado': contrato.cobranca_estado or None,
            'dia_vencimento': contrato.dia_vencimento or None,
            'fator_juros': contrato.fator_juros or None,
            'contrato_revenda': contrato.contrato_revenda or None,
            'faturamento_contrato': contrato.faturamento_contrato or None,
            'estado_contrato': contrato.estado_contrato or None,
            'data_estado': format_date(contrato.data_estado),
            'motivo_estado': contrato.motivo_estado or None
        }
        print(data)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@contratos_bp.route('/set_contrato', methods=['POST'])
def set_contrato():
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
        
        # Funções para conversão segura de tipos
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
        
        # Criar dicionário com os dados formatados
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
            'cobranca_cep': form_data.get('cobranca_cep'),
            'cobranca_endereco': form_data.get('cobranca_endereco'),
            'cobranca_complemento': form_data.get('cobranca_complemento'),
            'cobranca_bairro': form_data.get('cobranca_bairro'),
            'cobranca_cidade': form_data.get('cobranca_cidade'),
            'cobranca_estado': form_data.get('cobranca_uf'),
            'dia_vencimento': parse_int(form_data.get('dia_vencimento')),
            'fator_juros': parse_float(form_data.get('fator_juros')),
            'contrato_revenda': parse_bool(form_data.get('contrato_revenda')),
            'faturamento_contrato': parse_bool(form_data.get('faturamento_contrato')),
            'estado_contrato': form_data.get('estado_contrato'),
            'data_estado': parse_date(form_data.get('data_estado')),
            'motivo_estado': form_data.get('motivo_estado'),
            'cliente_id': parse_int(form_data.get('cliente_id'))
        }
        
        # Verificar se o número do contrato já existe
        if Contrato.query.filter_by(numero=contrato_data['numero']).first():
            return jsonify({
                'success': False,
                'message': 'Já existe um contrato com este número'
            }), 400
        
        # Criar novo contrato (deixe o ID ser auto-incrementado)
        novo_contrato = Contrato(**contrato_data)
        
        # Adicionar e commitar no banco
        db.session.add(novo_contrato)
        db.session.commit()
        
        # Atualizar o auto-increment se necessário (apenas para MySQL)
        try:
            db.session.execute(
                "ALTER TABLE contratos AUTO_INCREMENT = : id",
                {'id': novo_contrato.id + 1}
            )
            db.session.commit()
        except Exception as e:
            print(f"Alerta: Não foi possível realizar o autoincremento: {str(e)}")
        
        return render_template('contratos.html')
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar contrato: {str(e)}',
            'error_details': str(e)
        }), 500