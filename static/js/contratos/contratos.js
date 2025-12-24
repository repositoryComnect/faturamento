

    let timeoutBuscarContratoId;
    let clientesData = [];
    let currentPage = 1;
    const rowsPerPage = 5;

    let planosData = [];
    let currentPlanoPage = 1;
    const planoRowsPerPage = 5;

        function createLink(url, text) {
            return `<a href="${url}" class="text-decoration-none">${text || ''}</a>`;
        }

        function formatCurrency(value) {
            return `R$ ${value.toFixed(2)}`;
        }

        function updatePaginationButtons(prevBtn, nextBtn, currentPage, totalPages) {
            $(prevBtn).prop('disabled', currentPage === 1);
            $(nextBtn).prop('disabled', currentPage === totalPages);
        }

        function renderClientesPage() {
            const tbody = $('.clientes-table tbody');
            tbody.empty();

            if (!clientesData.length) {
                tbody.html(noDataRow(6, "Nenhum cliente relacionado ao contrato encontrado."));
                $('#pageInfo').text('');
                updatePaginationButtons('#prevPage', '#nextPage', 1, 1);
                return;
            }

            const totalPages = Math.ceil(clientesData.length / rowsPerPage);
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;

            clientesData.slice(start, end).forEach(cliente => {
                tbody.append(`
                    <tr>
                        <td>${createLink(`/clientes/${cliente.sequencia}`, cliente.sequencia)}</td>
                        <td>${cliente.nome_fantasia || ''}</td>
                        <td>${cliente.razao_social || ''}</td>
                        <td>${cliente.cnpj_cpf || ''}</td>
                        <td>${cliente.cidade || ''}</td>
                        <td>
                            <span class="status-badge ${cliente.estado_atual === 'Ativo' ? 'status-ativo' : 'status-inativo'}">
                                ${cliente.estado_atual || 'N/A'}
                            </span>
                        </td>
                    </tr>
                `);
            });

            $('#pageInfo').text(`Página ${currentPage} de ${totalPages}`);
            updatePaginationButtons('#prevPage', '#nextPage', currentPage, totalPages);
        }

        // ----------------- RENDER PLANOS -----------------
        function renderPlanosPage() {
            const tbody = $('.planos-table tbody');
            tbody.empty();

            if (!planosData.length) {
                tbody.html(noDataRow(5, "Nenhum plano associado encontrado"));
                $('#planos-pageInfo').text('');
                updatePaginationButtons('#planos-prevPage', '#planos-nextPage', 1, 1);
                return;
            }

            const totalPages = Math.ceil(planosData.length / planoRowsPerPage);
            const start = (currentPlanoPage - 1) * planoRowsPerPage;
            const end = start + planoRowsPerPage;

            planosData.slice(start, end).forEach(plano => {
                tbody.append(`
                    <tr>
                        <td>${createLink(`/planos/${plano.codigo}`, plano.codigo)}</td>
                        <td>${plano.nome}</td>
                        <td>${formatCurrency(plano.valor)}</td>
                    </tr>
                `);
            });

            $('#planos-pageInfo').text(`Página ${currentPlanoPage} de ${totalPages}`);
            updatePaginationButtons('#planos-prevPage', '#planos-nextPage', currentPlanoPage, totalPages);
        }

        function renderProdutos(produtos) {
            const tbody = $('.produtos-table tbody');
            if (!produtos || !produtos.length) {
                tbody.html(noDataRow(5, "Nenhum produto associado encontrado"));
                return;
            }

            const linhas = produtos.map(produto => `
                <tr>
                    <td>${createLink(`/produtos/${produto.codigo}`, produto.codigo)}</td>
                    <td>${produto.nome || ''}</td>
                    <td>${produto.descricao || 'N/A'}</td>
                    <td>${produto.quantidade || 0}</td>
                    <td>${produto.valor_unitario ? formatCurrency(produto.valor_unitario) : formatCurrency(0)}</td>
                </tr>
            `).join('');
            tbody.html(linhas);
        }

        function noDataRow(colspan, message) {
            return `
                <tr>
                    <td colspan="${colspan}" class="text-center text-muted">
                        <i class="bi bi-exclamation-circle me-2"></i>
                        ${message}
                    </td>
                </tr>
            `;
        }

        function updateContractFields(data) {
            const fieldMap = {
                'numero': '#numeroContrato',
                'razao_social': '#razao_social',
                'nome_fantasia': '#nome_fantasia',
                'atualizacao': '#atualizacao',
                'cadastramento': '#cadastramento',
                'tipo': '#tipo',
                'tipo_pessoa': '#tipo_pessoa',
                'contato': '#contato',
                'id_matriz_portal': '#id_matriz_portal',
                'email': '#email',
                'telefone': '#telefone',
                'cep': '#cep',
                'cnpj_cpf': '#cnpjCPFContrato',
                'revenda': '#revenda',
                'vendedor': '#vendedor',
                'endereco': '#endereco',
                'complemento': '#complemento',
                'bairro': '#bairro',
                'cidade': '#cidade',
                'estado': '#estado',
                'dia_vencimento': '#dia_vencimento',
                'fator_juros': '#fator_juros',
                'estado_contrato': '#estado_contrato',
                'data_estado': '#data_estado',
                'motivo_estado': '#motivo_estado',
                'plano_nome': '#plano_nome',
                'valor_plano': '#valor_plano',
                'valor_contrato': '#valor_contrato',
                'observacao' : '#observacao_contrato'
            };

            Object.keys(fieldMap).forEach(key => {
                const element = $(fieldMap[key]);
                if (!element.length) return;

                const value = data[key] || '';
                if (key === 'estado_contrato') {
                    element.val(value)
                        .removeClass('status-ativo status-inativo')
                        .addClass(value ? 'status-' + value.toLowerCase() : '');
                } else {
                    element.val(value);
                }
            });
        }

        function buscarDadosContrato(numeroContrato) {
            if (!numeroContrato) return;
            $('#loadingContrato').removeClass('d-none');
            clearTimeout(timeoutBuscarContratoId);

            timeoutBuscarContratoId = setTimeout(() => {
                $.ajax({
                    url: '/contratos/buscar-por-numero/' + numeroContrato,
                    method: 'GET',
                    success: function(data) {
                        if (!data || Object.keys(data).length === 0) {
                            Swal.fire({
                                icon: 'warning',
                                title: 'Contrato não encontrado',
                                text: 'Verifique se o número informado está correto.',
                                toast: true,
                                position: 'top-end',
                                timer: 6000,
                                timerProgressBar: true,
                                showConfirmButton: true
                            });
                            return;
                        }

                        updateContractFields(data);

                        clientesData = Array.isArray(data.clientes) ? data.clientes : [];
                        planosData = Array.isArray(data.planos) ? data.planos : [];
                        renderClientesPage();
                        renderPlanosPage();
                        renderProdutos(data.produtos);

                        const totalPlanos = (data.planos || []).reduce((acc, p) => acc + (p.valor || 0), 0);
                        const totalProdutos = (data.produtos || []).reduce((acc, p) => acc + ((p.quantidade || 0) * (p.valor_unitario || 0)), 0);
                        $('#valor_contrato').val((totalPlanos + totalProdutos).toFixed(2));
                    },
                    error: function(xhr) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro ao buscar contrato',
                            text: 'Não foi possível localizar o contrato. Verifique o número informado.',
                            toast: true,
                            position: 'top-end',
                            timer: 3000,
                            showConfirmButton: false
                        });
                    },
                    complete: function() {
                        $('#loadingContrato').addClass('d-none');
                    }
                });
            }, 500);
        }

        $(document).ready(function () {
            $('#prevPage').click(() => { if (currentPage > 1) { currentPage--; renderClientesPage(); } });
            $('#nextPage').click(() => { if (currentPage < Math.ceil(clientesData.length / rowsPerPage)) { currentPage++; renderClientesPage(); } });
            $('#planos-prevPage').click(() => { if (currentPlanoPage > 1) { currentPlanoPage--; renderPlanosPage(); } });
            $('#planos-nextPage').click(() => { if (currentPlanoPage < Math.ceil(planosData.length / planoRowsPerPage)) { currentPlanoPage++; renderPlanosPage(); } });

            const numeroContratoInput = $('#numeroContrato');
            numeroContratoInput.on('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); buscarDadosContrato(e.target.value); } });
            numeroContratoInput.on('change', e => buscarDadosContrato(e.target.value));
        });






// Buscar contrato editar popup
    let timeoutId;
    function buscarContrato(termo) {
        if (!termo) return;
        $('#loadingContrato').removeClass('d-none');
        clearTimeout(timeoutId);

        timeoutId = setTimeout(() => {
            $.ajax({
                url: '/buscar_contrato',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ termo: termo }),
                success: function(data) {
                    console.log("Dados recebidos:", data);
                    if (data.success) {
                        const contrato = data.contrato;
                        const fieldMap = {
                            'numero': '#contract_number',
                            'razao_social': '#company_name',
                            'nome_fantasia': '#trade_name',
                            'tipo': '#type',
                            'contato': '#contact',
                            'id_matriz_portal': '#id_matriz_portal',
                            'address_email': '#address_email',
                            'telefone': '#phone',
                            'cep': '#cep',
                            'cnpj_cpf': '#cnpj_cpf',
                            'endereco': '#address',
                            'complemento': '#complement',
                            'bairro': '#neighborhood',
                            'cidade': '#city',
                            'estado': '#state',
                            'fator_juros': '#interest_rate_factor',
                            'dia_vencimento': '#last_day',
                            'data_estado': '#state_date',
                            'motivo_estado': '#reason',
                            'estado_contrato': '#current_state',
                            'observacao': '#observacao_contrato_editar'
                        };

                        for (const key in fieldMap) {
                            if (contrato[key] !== null && contrato[key] !== undefined) {
                                const val = (key.includes('data')) ? formatarData(contrato[key]) : contrato[key];
                                $(fieldMap[key]).val(val);
                            }
                        }
                    } else {
                        alert('Contrato não encontrado!');
                    }
                    $('#loadingContrato').addClass('d-none');
                },
                error: function(xhr, status, error) {
                    console.error("Erro:", status, error);
                    alert('Erro ao buscar contrato.');
                    $('#loadingContrato').addClass('d-none');
                }
            });
        }, 1000);
    }
    function formatarData(data) {
        const d = new Date(data);
        return !isNaN(d) ? `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}` : '';
    }

    $('#search_contract').on('input', function() {
        buscarContrato($(this).val());
    });


// Buscar contrato
  function searchDadosContrato(numero) {
    numero = numero.trim();

    if (!numero) {
        Swal.fire({
            icon: 'info',
            title: 'Campo vazio',
            text: 'Por favor, informe o número do contrato.',
        });
        return;
    }

    const loading = document.getElementById('loadingContrato');
    if (loading) loading.classList.remove('d-none');

    fetch(`/get/contrato?search=${encodeURIComponent(numero)}`)
        .then(response => {
            if (loading) loading.classList.add('d-none');
            return response.json();
        })
        .then(data => {
            if (!data.sucesso || !data.contrato || !data.contrato.numero) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Contrato não encontrado',
                    text: data.erro || 'Verifique o número ou termo informado.',
                });
                return;
            }

            preencherCamposContrato(data.contrato);
        })
        .catch(error => {
            if (loading) loading.classList.add('d-none');

            console.error("Erro ao buscar contrato:", error);
            Swal.fire({
                icon: 'error',
                title: 'Erro no servidor',
                text: 'Não foi possível buscar o contrato.',
            });
        });
}


function preencherCamposContrato(contrato) {
    // Informações Básicas
    document.getElementById("numeroContrato").value = contrato.numero || "";
    document.getElementById("razao_social").value = contrato.razao_social || "";
    document.getElementById("nome_fantasia").value = contrato.nome_fantasia || "";
    document.getElementById("cadastramento").value = contrato.cadastramento || "";
    document.getElementById("atualizacao").value = contrato.atualizacao || "";
    document.getElementById("tipo").value = contrato.tipo || "";
    document.getElementById("contato").value = contrato.contato || "";
    document.getElementById("id_matriz_portal").value = contrato.id_matriz_portal || "";
    document.getElementById("email").value = contrato.email || "";
    document.getElementById("telefone").value = contrato.telefone || "";
    document.getElementById("cnpj").value = contrato.cnpj || contrato.cnpj_cpf || "";
    document.getElementById("tipo_pessoa").value = contrato.tipo_pessoa || "";
    document.getElementById("revenda").value =
    contrato.revenda_contrato === null || contrato.revenda_contrato === undefined || contrato.revenda_contrato === ""
        ? "Não possui revenda"
        : contrato.revenda_contrato;

    document.getElementById("vendedor").value =
    contrato.vendedor_contrato === null || contrato.vendedor_contrato === undefined || contrato.vendedor_contrato === ""
        ? "Não possui vendedor"
        : contrato.vendedor_contrato;


    // Endereço
    document.getElementById("cep").value = contrato.cep || "";
    document.getElementById("endereco").value = contrato.endereco || "";
    document.getElementById("complemento").value = contrato.complemento || "";
    document.getElementById("bairro").value = contrato.bairro || "";
    document.getElementById("cidade").value = contrato.cidade || "";
    document.getElementById("estado").value = contrato.estado || "";

    // Detalhes do Contrato
    document.getElementById("dia_vencimento").value = contrato.dia_vencimento || "";
    document.getElementById("fator_juros").value = contrato.fator_juros || "";
    document.getElementById("estado_contrato").value = contrato.estado_contrato || "";
    document.getElementById("data_estado").value = contrato.data_estado || "";
    document.getElementById("motivo_estado").value = contrato.motivo_estado || "";
    document.getElementById("valor_contrato").value = contrato.valor_contrato || "";
    document.getElementById("observacao").value = contrato.observacao || "";

    //  Se quiser limpar as tabelas vinculadas também:
    limparTabelasRelacionadas();
}

// Próximo número contrato, ação botão
function proximoContrato(numeroAtual) {
    if (!numeroAtual) return;

    $('#loadingContrato').removeClass('d-none');

    $.ajax({
        url: '/contratos/proximo/' + numeroAtual,
        method: 'GET',
        success: function(data) {
            if (!data || Object.keys(data).length === 0) {
                Swal.fire({
                    icon: 'info',
                    title: 'Não há mais contratos',
                    text: 'Você já está no último contrato cadastrado.',
                    toast: true,
                    position: 'top-end',
                    timer: 4000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
                return;
            }

            // Preenche os campos do contrato — usa a função já existente:
            updateContractFields(data);

            // Atualiza tabelas
            clientesData = Array.isArray(data.clientes) ? data.clientes : [];
            planosData = Array.isArray(data.planos) ? data.planos : [];
            renderClientesPage();
            renderPlanosPage();
            renderProdutos(data.produtos);

            // Soma valores
            const totalPlanos = (data.planos || []).reduce((acc, p) => acc + (p.valor || 0), 0);
            const totalProdutos = (data.produtos || []).reduce((acc, p) => acc + ((p.quantidade || 0) * (p.valor_unitario || 0)), 0);
            $('#valor_contrato').val((totalPlanos + totalProdutos).toFixed(2));
        },
        error: function() {
            Swal.fire({
                icon: 'error',
                title: 'Erro ao buscar próximo contrato',
                text: 'Ocorreu um problema na busca.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        },
        complete: function() {
            $('#loadingContrato').addClass('d-none');
        }
    });
}
