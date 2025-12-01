let timeoutSequencia;
let instalacoesData = [];
let currentInstalacaoPage = 1;
const instalacoesPerPage = 5;

function renderInstalacoesPage() {
    const tbody = $('.instalacao-table tbody');
    tbody.empty();

    if (!instalacoesData.length) {
        tbody.html(`
            <tr>
                <td colspan="5" class="text-center">
                    <i class="bi bi-exclamation-circle me-2"></i>
                    Nenhuma instalação associada encontrada
                </td>
            </tr>
        `);
        $('#instalacao-pageInfo').text('');
        $('#instalacao-prevPage, #instalacao-nextPage').prop('disabled', true);
        return;
    }

    const totalPages = Math.ceil(instalacoesData.length / instalacoesPerPage);
    const start = (currentInstalacaoPage - 1) * instalacoesPerPage;
    const end = start + instalacoesPerPage;

    instalacoesData.slice(start, end).forEach(inst => {
        const statusBadge = inst.status === 'Ativo'
            ? '<span class="badge bg-success">Ativo</span>'
            : '<span class="badge bg-danger">Inativo</span>';

        const valor = inst.valor_plano !== undefined && inst.valor_plano !== null
            ? `R$ ${parseFloat(inst.valor_plano).toFixed(2).replace('.', ',')}`
            : 'R$ 0,00';

        tbody.append(`
            <tr>
                <td>${inst.codigo_instalacao || ''}</td>
                <td>${inst.endereco || ''}</td>
                <td>${inst.bairro || ''}</td>
                <td>${statusBadge}</td>
            </tr>
        `);
    });

    $('#instalacao-pageInfo').text(`Página ${currentInstalacaoPage} de ${totalPages}`);
    $('#instalacao-prevPage').prop('disabled', currentInstalacaoPage === 1);
    $('#instalacao-nextPage').prop('disabled', currentInstalacaoPage === totalPages);
}

$('#instalacao-prevPage').on('click', () => {
    if (currentInstalacaoPage > 1) {
        currentInstalacaoPage--;
        renderInstalacoesPage();
    }
});

$('#instalacao-nextPage').on('click', () => {
    if (currentInstalacaoPage < Math.ceil(instalacoesData.length / instalacoesPerPage)) {
        currentInstalacaoPage++;
        renderInstalacoesPage();
    }
});

function buscarDadosCliente(numeroSequencia) {
    if (!numeroSequencia) return;

    $('#loadingCliente').removeClass('d-none');
    clearTimeout(timeoutSequencia);

    timeoutSequencia = setTimeout(() => {
        $.ajax({
            url: '/clientes/buscar-por-numero/' + numeroSequencia,
            method: 'GET',
            success: function(data) {
                console.log("Dados recebidos:", data);

                if (!data || Object.keys(data).length === 0) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Cliente não encontrado',
                        text: 'Verifique se o número informado está correto.',
                        toast: true,
                        position: 'top-end',
                        timer: 6000,
                        timerProgressBar: true,
                        showConfirmButton: true
                    });
                    $('#loadingCliente').addClass('d-none');
                    return;
                }

                // Mapear campos do cliente
                const fieldMap = {
                    'numero': '#numeroContrato',
                    'sequencia': '#sequencia',
                    'razao_social': '#razao_social',
                    'nome_fantasia': '#nome_fantasia',
                    'cadastramento': '#cadastramento',
                    'atualizacao': '#atualizacao',
                    'tipo': '#tipo',
                    'contato': '#contato',
                    'cnpj_cpf': '#cnpj_cpf',
                    'ie': '#ie',
                    'im': '#im',
                    'email': '#email',
                    'telefone': '#telefone',
                    'cep': '#cep',
                    'endereco': '#endereco',
                    'complemento': '#complemento',
                    'bairro': '#bairro',
                    'cidade': '#cidade',
                    'estado': '#estado',
                    'cep_cobranca': '#cep_cobranca',
                    'endereco_cobranca': '#endereco_cobranca',
                    'bairro_cobranca': '#bairro_cobranca',
                    'cidade_cobranca': '#cidade_cobranca',
                    'telefone_cobranca': '#telefone_cobranca',
                    'uf_cobranca': '#uf_cobranca',
                    'fator_juros': '#fator_juros',
                    'estado_contrato': '#estado_contrato',
                    'data_estado': '#data_estado',
                    'motivo_estado': '#motivo_estado',
                    'plano_nome': '#plano_nome',
                    'observacao': '#observacao',
                    'revenda_nome': '#revenda_nome',
                    'vendedor_nome': '#vendedor_nome',
                    'tipo_servico': '#tipo_servico',
                    'localidade': '#localidade',
                    'regiao': '#regiao',
                    'atividade': '#atividade'
                };

                for (const key in fieldMap) {
                    const selector = fieldMap[key];
                    const value = data[key];
                    if (value !== null && value !== undefined) {
                        $(selector).val(value);
                    }
                }

                // Renderizar instalações
                if (Array.isArray(data.instalacoes)) {
                    instalacoesData = data.instalacoes;
                    currentInstalacaoPage = 1;
                    renderInstalacoesPage();
                } else {
                    instalacoesData = [];
                    renderInstalacoesPage();
                }

                function createLink(url, label) {
                    return `<a href="${url}" class="text-primary" style="text-decoration:none; font-weight:600;">${label}</a>`;
                }


                // Renderizar contratos
                const contratoTbody = $('.contrato-table tbody');
                contratoTbody.empty();

                if (Array.isArray(data.contratos) && data.contratos.length > 0) {
                    data.contratos.forEach(contrato => {
                        const tr = $('<tr>').addClass('text');
                        tr.html(`
                            <td>${createLink(`/contratos/buscar-por-numero/${contrato.numero}`, contrato.numero)}</td>
                            <td>${contrato.razao_social || contrato.nome_fantasia || '-'}</td>
                            <td>${contrato.plano_nome || ''}</td>
                            <td>${contrato.produto_nome || ''}</td>
                            <td>${contrato.fator_juros != null ? contrato.fator_juros.toFixed(2) : '-'}</td>
                        `);
                        contratoTbody.append(tr);
                    });
                } else {
                    contratoTbody.html(`<tr><td colspan="5" 
                        class="text-center">
                        <i class="bi bi-exclamation-circle me-2"></i>
                        Nenhum contrato vinculado</td></tr>`);
                }


                $('#loadingCliente').addClass('d-none');
            },
            error: function(xhr, status, error) {
                console.error("Erro na requisição:", xhr);
                Swal.fire({
                    icon: 'error',
                    title: 'Erro ao buscar o cliente',
                    text: 'Não foi possível localizar o contrato. Verifique o número informado.',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });
                $('#loadingCliente').addClass('d-none');
            },
        });
    }, 500);
}

// Disparar ao alterar input ou clicar no botão
$('#sequencia').on('change', function() {
    buscarDadosCliente(this.value);
});


function buscarProximoCliente() {
    const numeroSequencia = document.getElementById('sequencia').value;
    if (!numeroSequencia) return;

    $('#loadingCliente').removeClass('d-none');

    $.ajax({
        url: `/clientes/proximo/${numeroSequencia}`,
        method: 'GET',
        success: function(data) {

            if (!data || data.error || data.message) {
                Swal.fire({
                    icon: 'info',
                    title: 'Aviso',
                    text: data?.message || 'Nenhum próximo cliente encontrado.',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });
                $('#loadingCliente').addClass('d-none');
                return;
            }

            // Agora utilizamos a mesma função padrão do fluxo normal!
            if (data.sequencia) {
                buscarDadosCliente(data.sequencia);
            } else {
                // fallback caso a API retorne o objeto completo diretamente
                preencherCamposCliente(data);
            }

            $('#loadingCliente').addClass('d-none');
        },
        error: function() {
            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: 'Não foi possível buscar o próximo cliente.',
            });
            $('#loadingCliente').addClass('d-none');
        }
    });
}

