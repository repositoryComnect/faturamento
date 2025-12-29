function proximoCodigoPlano() {
    let codigoAtual = document.getElementById('codigo_plano').value;
    if (!codigoAtual) return;

    $('#loadingCodigoPlano').removeClass('d-none');

    fetch(`/planos/proximo/${codigoAtual}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro HTTP');
            }
            return response.json();
        })
        .then(data => {
            $('#loadingCodigoPlano').addClass('d-none');

            console.log('Plano retornado:', data);
            console.log('Contratos:', data.contratos);

            if (!data || Object.keys(data).length === 0) {
                Swal.fire({
                    icon: 'info',
                    title: 'Último plano',
                    text: 'Você já está no último plano cadastrado.',
                    toast: true,
                    position: 'top-end',
                    timer: 4000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
                return;
            }

            document.getElementById('codigo_plano').value = data.codigo ?? "";
            document.getElementById('nome_plano').value = data.nome ?? "";
            document.getElementById('valor_plano').value = data.valor ?? "";
            document.getElementById('id_produto_plano').value = data.id_produto_portal ?? "";
            document.getElementById('produto_id_plano').value = data.produto ?? "";
            document.getElementById('qtd_produto_plano').value = data.qtd_produto ?? "";
            document.getElementById('desc_boleto_licenca_plano').value = data.desc_boleto_licenca ?? "";
            document.getElementById('aliquota_sp_licenca_plano').value = data.aliquota_sp_licenca ?? "";
            document.getElementById('cod_servico_sp_licenca_plano').value = data.cod_servico_sp_licenca ?? "";
            document.getElementById('desc_nf_licenca_plano').value = data.desc_nf_licenca ?? "";
            document.getElementById('cadastramento_plano').value = data.cadastramento ?? "";
            document.getElementById('atualizacao_plano').value = data.atualizacao ?? "";
            document.getElementById('status_plano').value = data.status ?? "";

            const tabelaProdutos = document.getElementById('produtosPlanoTbody');
            tabelaProdutos.innerHTML = "";

            if (!Array.isArray(data.produtos) || data.produtos.length === 0) {
                tabelaProdutos.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center">
                            <i class="bi bi-exclamation-circle me-2"></i>
                            Nenhum produto vinculado
                        </td>
                    </tr>`;
            } else {
                data.produtos.forEach(produto => {
                    const tr = document.createElement("tr");
                    tr.classList.add("text-center");

                    tr.innerHTML = `
                        <td>${produto.codigo ?? '-'}</td>
                        <td>${produto.nome ?? '-'}</td>
                        <td>${produto.descricao ?? '-'}</td>
                        <td>${produto.quantidade ?? '-'}</td>
                        <td>
                            R$ ${Number(produto.preco_base ?? 0)
                                .toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </td>
                        <td>${produto.status ?? '-'}</td>
                    `;
                    tabelaProdutos.appendChild(tr);
                });
            }

            const tabelaContratos = document.querySelector('.contrato-table tbody');

            if (!tabelaContratos) {
                console.error('Tabela de contratos não encontrada');
                return;
            }

            tabelaContratos.innerHTML = "";

            if (!Array.isArray(data.contratos) || data.contratos.length === 0) {
                tabelaContratos.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center">
                            <i class="bi bi-exclamation-circle me-2"></i>
                            Nenhum contrato associado encontrado
                        </td>
                    </tr>`;
            } else {
                data.contratos.forEach(contrato => {
                    const tr = document.createElement("tr");

                    tr.innerHTML = `
                        <td class="text-center">${contrato.numero ?? '-'}</td>
                        <td>${contrato.razao_social ?? contrato.nome_fantasia ?? '-'}</td>
                        <td class="text-center">${contrato.cnpj_cpf ?? '-'}</td>
                        <td class="text-center">
                            <span class="badge ${contrato.status === 'Ativo' ? 'bg-success' : 'bg-secondary'}">
                                ${contrato.status ?? 'N/A'}
                            </span>
                        </td>
                    `;

                    tabelaContratos.appendChild(tr);
                });
            }
        })
        .catch(err => {
            $('#loadingCodigoPlano').addClass('d-none');
            console.error("Erro ao buscar próximo plano:", err);

            Swal.fire({
                icon: 'error',
                title: 'Erro ao buscar próximo plano',
                text: 'Ocorreu um problema na busca.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        });
}






function buscarPlanoPorCodigo(codigo) {
    if (!codigo) return;

    $('#loadingCodigoPlano').removeClass('d-none');

    fetch(`/planos/buscar-por-codigo/${codigo}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            $('#loadingCodigoPlano').addClass('d-none');

            console.log('RETORNO PLANO:', data);
            console.log('PRODUTOS:', data.produtos);

            if (data.error) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Plano não encontrado',
                    text: data.error
                });
                return;
            }

            document.getElementById('codigo_plano').value = data.codigo ?? "";
            document.getElementById('nome_plano').value = data.nome ?? "";
            document.getElementById('valor_plano').value = data.valor ?? "";
            document.getElementById('qtd_produto_plano').value = data.qtd_produto ?? "";
            document.getElementById('status_plano').value = data.status ?? "";

            preencherContratosPlano(data.contratos);

            preencherProdutosPlano(data.produtos);
        })
        .catch(err => {
            console.error("Erro ao buscar plano:", err);
            $('#loadingCodigoPlano').addClass('d-none');
        });
}


function preencherProdutosPlano(produtos) {
    const tbody = document.getElementById('produtosPlanoTbody');

    if (!tbody) {
        console.error(' tbody produtosPlanoTbody não encontrado');
        return;
    }

    tbody.innerHTML = "";

    if (!Array.isArray(produtos) || produtos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <i class="bi bi-exclamation-circle me-2"></i>
                    Nenhum produto associado encontrado
                </td>
            </tr>
        `;
        return;
    }

    produtos.forEach(produto => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td class="text-center">${produto.codigo ?? '-'}</td>
            <td>${produto.nome ?? '-'}</td>
            <td>${produto.descricao ?? '-'}</td>
            <td class="text-center">${produto.quantidade ?? 0}</td>
            <td class="text-end">${formatarMoeda(produto.preco_base)}</td>
            <td>${produto.status ?? '-'}</td>
        `;

        tbody.appendChild(tr);
    });
}


function preencherContratosPlano(contratos) {
    const tabela = document.querySelector(".contrato-table tbody");
    tabela.innerHTML = "";

    if (!contratos || contratos.length === 0) {
        tabela.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">
                    Nenhum contrato associado
                </td>
            </tr>
        `;
        return;
    }

    contratos.forEach(c => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${c.numero}</td>
            <td>${c.razao_social ?? c.nome_fantasia}</td>
            <td>${c.cnpj_cpf}</td>
            <td>
                <span class="badge bg-success">
                    ${c.status}
                </span>
            </td>
        `;

        tabela.appendChild(tr);
    });
}


function formatarMoeda(valor) {
    return Number(valor ?? 0).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

