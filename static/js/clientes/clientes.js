

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
                    <td>${inst.id || ''}</td>
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
                        return;
                    }

                    const fieldMap = {
                        'numero': '#numeroContrato',
                        'sequencia': '#sequencia',
                        'razao_social': '#razao_social',
                        'nome_fantasia': '#nome_fantasia',
                        'cadastramento': '#cadastramento',
                        'atualizacao': '#atualizacao',
                        'tipo': '#tipo',
                        'contato': '#contato',
                        'cnpj': '#cnpj',
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
                        'tipo_cobranca': '#tipo_cobranca',
                        'data_estado': '#data_estado',
                        'motivo_estado': '#motivo_estado',
                        'plano_nome': '#plano_nome',
                        'valor_plano': '#valor_plano',
                        'valor_contrato': '#valor_contrato',
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

                    // Atualiza instalações vinculadas ao cliente
                    if (Array.isArray(data.instalacoes)) {
                        instalacoesData = data.instalacoes;
                        currentInstalacaoPage = 1;
                        renderInstalacoesPage();
                    } else {
                        instalacoesData = [];
                        renderInstalacoesPage();
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
                },
            });
        }, 500);
    }









    