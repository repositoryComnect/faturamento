def montar_dict_plano(plano):
    """
    Constrói um dicionário serializável a partir do objeto Plano,
    mapeando para os nomes de coluna reais do seu banco.
    Colunas disponíveis (conforme você listou):
    id, codigo, nome, valor, id_portal, licenca_valor,
    data_criacao, data_atualizacao, desc_boleto_licenca,
    aliquota_sp_licenca, cod_servico_sp_licenca, produto,
    qtd_produto, desc_nf_licenca, valor_base_produto, empresa_id
    """
    return {
        'id': plano.id,
        'codigo': plano.codigo,
        'nome': plano.nome or None,
        'valor': float(plano.valor) if plano.valor is not None else 0.0,
        # id do produto no portal — sua coluna é id_portal
        'id_produto_portal': plano.id_portal or None,
        # campo 'produto' na sua tabela (usado como produto_id no frontend)
        'produto_id': plano.produto or None,
        'qtd_produto': plano.qtd_produto or None,
        # campos de licença/boletos usam sufixo _licenca no seu schema
        'desc_boleto': plano.desc_boleto_licenca or None,
        'aliquota_sp': plano.aliquota_sp_licenca or None,
        'cod_servico_sp': plano.cod_servico_sp_licenca or None,
        'desc_nf': plano.desc_nf_licenca or None,
        # data de criação no seu schema é data_criacao
        'cadastramento': plano.data_criacao.strftime('%Y-%m-%d') if getattr(plano, 'data_criacao', None) else None,
        # não existe coluna contrato_id no seu schema — devolve None para frontend
        'contrato_id': None,
        # opcional: expor valor_base_produto caso precise no frontend
        'valor_base_produto': float(plano.valor_base_produto) if getattr(plano, 'valor_base_produto', None) is not None else None,
        # empresa_id (útil para debug)
        'empresa_id': plano.empresa_id if hasattr(plano, 'empresa_id') else None,
    }
