from datetime import datetime
from application.models.models import Contrato, db, Cliente, Produto, Plano, ContratoProduto, Revenda, cliente_contrato
from modules.utils.utils import formatar_telefone, safe_float, safe_date, parse_date, formatar_cep, formatar_cpf_cnpj


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


def montar_dict_contrato(contrato):
    data = {
        'id': contrato.id,
        'numero': contrato.numero,
        'razao_social': contrato.razao_social or None,
        'nome_fantasia': contrato.nome_fantasia or None,
        'atualizacao': safe_date(contrato.atualizacao),
        'cadastramento': safe_date(contrato.cadastramento),
        'tipo': contrato.tipo or None,
        'tipo_pessoa': contrato.tipo_pessoa or None,
        'contato': contrato.contato or None,
        'id_matriz_portal': contrato.id_matriz_portal or None,
        'email': contrato.email or None,
        'telefone': formatar_telefone(contrato.telefone or None),
        'cep': formatar_cep(contrato.cep or None),
        'cnpj_cpf': formatar_cpf_cnpj(contrato.cnpj_cpf or None),
        'revenda': contrato.revenda if contrato.revenda not in (None, "", "null") else "Não possui revenda",
        'vendedor': contrato.vendedor if contrato.vendedor not in (None, "", "null") else "Não possui vendedor",
        'endereco': contrato.endereco or None,
        'complemento': contrato.complemento or None,
        'bairro': contrato.bairro or None,
        'cidade': contrato.cidade or None,
        'estado': contrato.estado or None,
        'dia_vencimento': contrato.dia_vencimento or None,
        'fator_juros': safe_float(contrato.fator_juros),
        'contrato_revenda': contrato.contrato_revenda or None,
        'faturamento_contrato': contrato.faturamento_contrato or None,
        'estado_contrato': contrato.estado_contrato or None,
        'data_estado': safe_date(contrato.data_estado),
        'motivo_estado': contrato.motivo_estado or None,
        'observacao' : contrato.observacao or None
    }

    # Cliente principal
    clientes = []
    if contrato.cliente:
        clientes.append({
            'id': contrato.cliente.id,
            'sequencia': contrato.cliente.sequencia,
            'razao_social': contrato.cliente.razao_social,
            'nome_fantasia': contrato.cliente.nome_fantasia,
            'cnpj_cpf': formatar_cpf_cnpj(contrato.cliente.cnpj_cpf),
            'tipo_serviço': contrato.cliente.tipo_servico,
            'cidade': contrato.cliente.cidade,
            'estado_atual': contrato.cliente.estado_atual,
        })
    data['clientes'] = clientes

    # Planos
    data['planos'] = []
    if hasattr(contrato, 'planos') and contrato.planos:
        for p in contrato.planos:
            data['planos'].append({
                'id': p.id,
                'codigo': p.codigo,
                'nome': p.nome,
                'valor': safe_float(p.valor, 0.00)
            })

    # Produtos
    data['produtos'] = []
    associacoes = ContratoProduto.query.filter_by(contrato_id=contrato.id).all()
    for assoc in associacoes:
        produto = Produto.query.get(assoc.produto_id)
        if produto:
            data['produtos'].append({
                'codigo': produto.codigo,
                'id': produto.id,
                'nome': produto.nome or None,
                'descricao': produto.descricao or 'N/A',
                'quantidade': assoc.quantidade or 0,
                'valor_unitario': safe_float(produto.preco_base, 0.00)
            })

    return data
