

def montar_dict_plano(plano, contratos=[]):
    return {
        'id': plano.id,
        'codigo': plano.codigo,
        'nome': plano.nome or "",
        'valor': float(plano.valor) if plano.valor else 0.0,

        'id_produto_portal': plano.id_portal or "",
        'produto': plano.produto or "",
        'produto_id': plano.produto or "",
        'qtd_produto': plano.qtd_produto or 0,


        'licenca_valor': plano.licenca_valor or "",
        'valor_base_produto': plano.valor_base_produto or "",
        'desc_boleto_licenca': plano.desc_boleto_licenca or "",
        'desc_nf_licenca': plano.desc_nf_licenca or "",

        'aliquota_sp_licenca': plano.aliquota_sp_licenca or "",
        'cod_servico_sp_licenca': plano.cod_servico_sp_licenca or "",

        'cadastramento': plano.data_criacao.strftime("%d/%m/%Y") if plano.data_criacao else "",
        'atualizacao': plano.data_atualizacao.strftime("%d/%m/%Y") if plano.data_atualizacao else "",

        'status': plano.status or "",
        'empresa_id': plano.empresa_id or "",

        'observacao': getattr(plano, 'observacao', "") or "",
        'ativo': getattr(plano, 'ativo', True),
        
    }


def parse_float(valor):
    try:
        return float(str(valor).replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0