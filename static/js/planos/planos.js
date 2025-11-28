function proximoCodigoPlano() {
    let codigoAtual = document.getElementById('codigo_plano').value;
    if (!codigoAtual) return;

    $('#loadingCodigoPlano').removeClass('d-none');

    fetch(`/planos/proximo/${codigoAtual}`)
        .then(response => response.json())
        .then(data => {
            $('#loadingCodigoPlano').addClass('d-none');

            // Caso seja o último plano
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

            // ==========
            // CAMPOS
            // ==========
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

            // ====================
            // LISTA DE CONTRATOS
            // ====================
            const tabela = document.querySelector(".contrato-table tbody");
            tabela.innerHTML = ""; 

            if (!data.contratos || data.contratos.length === 0) {
                tabela.innerHTML = `
                   <tr>
                      <td colspan="5" class="text-center">
                         Nenhum contrato associado
                      </td>
                   </tr>`;
                return;
            }

            data.contratos.forEach(contrato => {
                const tr = document.createElement("tr");

                tr.innerHTML = `
                    <td>${contrato.numero ?? '-'}</td>
                    <td>${contrato.razao_social ?? contrato.nome_fantasia ?? '-'}</td>
                    <td>${contrato.cnpj_cpf ?? '-'}</td>
                    <td>
                        <span class="badge rounded-pill px-3 py-2 ${getStatusBadgeClass(contrato.status)}">
                            ${contrato.status ?? 'N/A'}
                        </span>
                    </td>
                `;
                tabela.appendChild(tr);
            });
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


// Buscar planos por código 

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

            if (data.error) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Plano não encontrado',
                    text: data.error
                });
                return;
            }

            // PREENCHER CAMPOS DO PLANO
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

            // ====================
            // PREENCHER CONTRATOS
            // ====================
            const tabela = document.querySelector(".contrato-table tbody");
            tabela.innerHTML = ""; 

            if (!data.contratos || data.contratos.length === 0) {
                tabela.innerHTML = `
                   <tr>
                      <td colspan="5" class="text-center">
                         Nenhum contrato associado
                      </td>
                   </tr>`;
                return;
            }

            data.contratos.forEach(contrato => {
                const tr = document.createElement("tr");

                tr.innerHTML = `
                    <td>${contrato.numero ?? '-'}</td>
                    <td>${contrato.razao_social ?? contrato.nome_fantasia ?? '-'}</td>
                    <td>${contrato.cnpj_cpf ?? '-'}</td>
                    <td>
                        <span class="badge rounded-pill px-3 py-2 ${getStatusBadgeClass(contrato.status)}">
                            ${contrato.status ?? 'N/A'}
                        </span>
                    </td>


                    
                `;
                
                tabela.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("Erro ao buscar plano:", err);
            $('#loadingCodigoPlano').addClass('d-none');
        });
}


function getStatusBadgeClass(status) {
    if (!status) return "bg-secondary";

    status = status.toLowerCase();

    if (status.includes("ativo")) return "bg-success";          // VERDE
    if (status.includes("suspenso")) return "bg-warning text-dark"; // AMARELO
    if (status.includes("arquivado")) return "bg-orange text-white"; // LARANJA
    if (status.includes("cancelado")) return "bg-danger";       // VERMELHO

    return "bg-secondary"; // fallback
}

