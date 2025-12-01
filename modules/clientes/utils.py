from datetime import datetime
from modules.utils.utils import formatar_cpf_cnpj, formatar_cep, formatar_telefone


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
        
def format_date(date):
    return date.strftime('%d/%m/%Y') if date else None

def montar_dict_cliente(cliente):
    return {
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
