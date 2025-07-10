from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from application.models.models import db, Plano, Contrato
from sqlalchemy import text
from datetime import datetime
import re

planos_bp = Blueprint('planos_bp', __name__)

@planos_bp.route('/get/planos', methods=['GET'])
def get_planos():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Itens por página

    offset = (page - 1) * per_page

    resultado = db.session.execute(
        text("SELECT * FROM planos ORDER BY id LIMIT :limit OFFSET :offset"),
        {"limit": per_page, "offset": offset}
    )
    planos = [dict(row._mapping) for row in resultado]

    total = db.session.execute(text("SELECT COUNT(*) FROM planos")).scalar()

    return render_template('listar_planos.html', planos=planos, page=page, per_page=per_page, total=total)

@planos_bp.route('/insert/planos', methods=['POST'])
def insert_planos():
    try:
        db.session.rollback()
        form_data = request.form.to_dict()

        def parse_float(valor):
            try:
                return float(str(valor).replace(',', '.'))
            except (ValueError, TypeError):
                return 0.0

        desc_nf_licenca = True if form_data.get('desc_nf_licenca') == 'on' else False

        # Valores base
        valor_base = parse_float(form_data.get('valor', 0))
        aliquota_sp = parse_float(form_data.get('aliquota_sp_licenca'))
        aliquota_barueri = parse_float(form_data.get('aliquota_barueri_licenca'))

        # Só calcula o valor com alíquota se pelo menos uma for > 0
        if aliquota_sp > 0 or aliquota_barueri > 0:
            percentual_total = aliquota_sp + aliquota_barueri
            valor_com_imposto = valor_base + (valor_base * percentual_total / 100)
        else:
            valor_com_imposto = valor_base  # permanece o mesmo

        plano_data = {
            'codigo': form_data.get('codigo'),
            'nome': form_data.get('nome'),
            'valor': round(valor_com_imposto, 2),
            'licenca_valor': valor_base,
            'id_portal': form_data.get('id_produto'),
            'desc_boleto_licenca': form_data.get('desc_boleto_licenca'),
            'aliquota_sp_licenca': aliquota_sp,
            'cod_servico_sp_licenca': form_data.get('cod_servico_sp_licenca'),
            'aliquota_barueri_licenca': aliquota_barueri,
            'cod_servico_barueri_licenca': form_data.get('cod_servico_barueri_licenca'),
            'desc_nf_licenca': desc_nf_licenca,

            'desc_boleto_suporte': form_data.get('desc_boleto_suporte'),
            'aliquota_sp_suporte': parse_float(form_data.get('aliquota_sp_suporte')),
            'cod_servico_sp_suporte': form_data.get('cod_servico_sp_suporte'),
            'aliquota_barueri_suporte': parse_float(form_data.get('aliquota_barueri_suporte')),
            'cod_servico_barueri_suporte': form_data.get('cod_servico_barueri_suporte'),
            'desc_nf_suporte': form_data.get('desc_nf_suporte'),

            'desc_boleto_gerenciamento': form_data.get('desc_boleto_gerenciamento'),
            'aliquota_sp_gerenciamento': parse_float(form_data.get('aliquota_sp_gerenciamento')),
            'cod_servico_sp_gerenciamento': form_data.get('cod_servico_sp_gerenciamento'),
            'aliquota_barueri_gerenciamento': parse_float(form_data.get('aliquota_barueri_gerenciamento')),
            'cod_servico_barueri_gerenciamento': form_data.get('cod_servico_barueri_gerenciamento'),
            'desc_nf_gerenciamento': form_data.get('desc_nf_gerenciamento'),

            'desc_boleto_hospedagem': form_data.get('desc_boleto_hospedagem'),
            'aliquota_sp_hospedagem': parse_float(form_data.get('aliquota_sp_hospedagem')),
            'cod_servico_sp_hospedagem': form_data.get('cod_servico_sp_hospedagem'),
            'aliquota_barueri_hospedagem': parse_float(form_data.get('aliquota_barueri_hospedagem')),
            'cod_servico_barueri_hospedagem': form_data.get('cod_servico_barueri_hospedagem'),
            'desc_nf_hospedagem': form_data.get('desc_nf_hospedagem'),

            'desc_boleto_manutencao': form_data.get('desc_boleto_manutencao'),
            'aliquota_sp_manutencao': parse_float(form_data.get('aliquota_sp_manutencao')),
            'cod_servico_sp_manutencao': form_data.get('cod_servico_sp_manutencao'),
            'aliquota_barueri_manutencao': parse_float(form_data.get('aliquota_barueri_manutencao')),
            'cod_servico_barueri_manutencao': form_data.get('cod_servico_barueri_manutencao'),
            'desc_nf_manutencao': form_data.get('desc_nf_manutencao'),

            'desc_boleto_monitoramento': form_data.get('desc_boleto_monitoramento'),
            'aliquota_sp_monitoramento': parse_float(form_data.get('aliquota_sp_monitoramento')),
            'cod_servico_sp_monitoramento': form_data.get('cod_servico_sp_monitoramento'),
            'aliquota_barueri_monitoramento': parse_float(form_data.get('aliquota_barueri_monitoramento')),
            'cod_servico_barueri_monitoramento': form_data.get('cod_servico_barueri_monitoramento'),
            'desc_nf_monitoramento': form_data.get('desc_nf_monitoramento'),

            'data_criacao': datetime.now(),
            'data_atualizacao': datetime.now()
        }

        novo_plano = Plano(**plano_data)
        db.session.add(novo_plano)
        db.session.commit()

        contrato_id = form_data.get('contrato_id')
        if contrato_id:
            contrato = Contrato.query.get(int(contrato_id))
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

        # Acrescentando total, página e itens por página
        total = len(planos)
        page = 1
        per_page = total  # ou defina um valor fixo, ex: 10
        
        return render_template('listar_planos.html', planos=planos, total=total, page=page, per_page=per_page)  # Fixed variable name
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500

@planos_bp.route('/delete/planos', methods=['POST'])
def delete_planos():
    codigo = request.form.get('delete_codigo_plano')
    print(f"🔍 Código recebido para exclusão: {codigo}")
    
    try:
        # 1. Buscar ID do plano
        plano_id_result = db.session.execute(
            text("SELECT id FROM planos WHERE codigo = :codigo"),
            {'codigo': codigo}
        ).first()

        if not plano_id_result:
            flash('Plano não encontrado com esse código.', 'error')
            print("❌ Plano não encontrado.")
            return redirect(url_for('home_bp.render_planos'))

        plano_id = plano_id_result[0]
        print(f"✅ Plano encontrado com ID: {plano_id}")

        # 2. Deletar vínculos na tabela contrato_plano
        deleted_links = db.session.execute(
            text("DELETE FROM contrato_plano WHERE plano_id = :plano_id"),
            {'plano_id': plano_id}
        )
        print(f"🔗 Vínculos removidos: {deleted_links.rowcount}")

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





    