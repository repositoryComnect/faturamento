// Script: carrega clientes e preenche nome no campo 'numero_serie' 

    document.addEventListener('DOMContentLoaded', function () {
        const select = document.getElementById('cliente_selecionado');
        const numeroSerieInput = document.getElementById('company') || document.getElementById('razao_social');
;

        fetch('/get/list/clientes')
            .then(response => response.json())
            .then(data => {
                select.innerHTML = '<option value="">Vincule um cliente</option>';
                data.forEach(cliente => {
                    const option = document.createElement('option');
                    option.value = cliente.id;  // será cliente_id no backend
                    option.textContent = cliente.razao_social;
                    option.setAttribute('data-nome', cliente.razao_social);  // usado para preencher número de série
                    select.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Erro ao buscar clientes:', error);
                select.innerHTML = '<option value="">Erro ao carregar clientes</option>';
            });

        select.addEventListener('change', function () {
            const nome = select.options[select.selectedIndex].getAttribute('data-nome');
            numeroSerieInput.value = nome || '';
        });
    });


// Script: define data atual no campo 'cadastramento' 
    document.addEventListener('DOMContentLoaded', function () {
        const hoje = new Date();
        const dia = String(hoje.getDate()).padStart(2, '0');
        const mes = String(hoje.getMonth() + 1).padStart(2, '0');
        const ano = hoje.getFullYear();
        const dataFormatada = `${ano}-${mes}-${dia}`;  // formato compatível com MySQL

        const campo = document.getElementById('cadastramento', 'registry');
        if (campo && !campo.value) {
            campo.value = dataFormatada;
        }
    });

    

// Search Instalações
function buscarInstalacoes() {
    const search = document.getElementById("search").value.trim();

    if (!search) {
        Swal.fire({
            icon: 'info',
            title: 'Busca vazia',
            text: 'Por favor, insira um termo para pesquisa.',
        });
        return;
    }

    fetch(`/get/instalacoes?search=${encodeURIComponent(search)}`)
        .then(response => response.json())
        .then(data => {
            if (!data.sucesso) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Nenhum resultado encontrado',
                    text: 'Verifique o código ou razão social.',
                });
                return;
            }

            const instalacao = data.instalacoes[0];  // Pegando a primeira instalação
            preencherCamposInstalacao(instalacao);
        })
        .catch(error => {
            console.error("Erro ao buscar instalações:", error);
            Swal.fire({
                icon: 'error',
                title: 'Erro no servidor',
                text: 'Não foi possível buscar a instalação.',
            });
        });
}

function preencherCamposInstalacao(inst) {
    // Preenche os campos principais
    document.getElementById("codigo_instalacao").value = inst.codigo_instalacao || "";
    document.getElementById("razao_social").value = inst.razao_social || "";
    document.getElementById("id_portal").value = inst.id_portal || "";
    document.getElementById("cadastramento").value = inst.cadastramento || "";
    document.getElementById("status").value = inst.status || "";

    // Endereço
    document.getElementById("cep").value = inst.cep || "";
    document.getElementById("endereco").value = inst.endereco || "";
    document.getElementById("bairro").value = inst.bairro || "";
    document.getElementById("cidade").value = inst.cidade || "";
    document.getElementById("uf").value = inst.uf || "";

    // Cliente vinculado
    const selectCliente = document.getElementById('cliente_selecionado');
    if (inst.cliente_id && selectCliente) {
        selectCliente.value = inst.cliente_id;
    }
}


// Módulo para trazer a data atual para poder realizar o cadastro 

    document.addEventListener('DOMContentLoaded', function () {
        const createModal = document.getElementById('createInstalacoesModal');

        if (createModal) {
            createModal.addEventListener('shown.bs.modal', function () {
                const hoje = new Date();
                const dia = String(hoje.getDate()).padStart(2, '0');
                const mes = String(hoje.getMonth() + 1).padStart(2, '0');
                const ano = hoje.getFullYear();
                const dataFormatada = `${dia}/${mes}/${ano}`;

                const camposData = ['atualizacao_instalacao'];
                camposData.forEach(id => {
                    const campo = document.getElementById(id);
                    if (campo && !campo.value) {
                        campo.value = dataFormatada;
                    }
                });
            });
        }
    });


let timeoutSequenciaInstalacao;

function buscarDadosInstalacao(codigoInstalacao) {
    if (!codigoInstalacao) return;

    $('#loadingCliente').removeClass('d-none');
    clearTimeout(timeoutSequenciaInstalacao);

    timeoutSequenciaInstalacao = setTimeout(() => {
        $.ajax({
            url: '/instalacao/buscar-por-numero/' + codigoInstalacao,
            method: 'GET',
            success: function (data) {

                console.log("Dados da instalação recebidos:", data);

                if (!data || Object.keys(data).length === 0 || data.error) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Instalação não encontrada',
                        text: 'Verifique se o código informado está correto.',
                        toast: true,
                        position: 'top-end',
                        timer: 6000,
                        timerProgressBar: true,
                        showConfirmButton: true
                    });

                    $('#clientesTableBody').html(`
                        <tr>
                            <td colspan="6" class="text-center">
                                Nenhum cliente relacionado a instalação foi encontrado.
                            </td>
                        </tr>
                    `);

                    $('#loadingCliente').addClass('d-none');
                    return;
                }

                /* ===============================
                   CAMPOS DA INSTALAÇÃO
                =============================== */
                const fieldMap = {
                    'codigo_instalacao': '#codigo_instalacao',
                    'razao_social': '#razao_social',
                    'cadastramento': '#cadastramento',
                    'id_portal': '#id_portal',
                    'endereco': '#endereco',
                    'bairro': '#bairro',
                    'cidade': '#cidade',
                    'cep': '#cep',
                    'uf': '#uf',
                    'status': '#status',
                    'observacao': '#observacao'
                };

                for (const key in fieldMap) {
                    if (data[key] !== null && data[key] !== undefined) {
                        $(fieldMap[key]).val(data[key]);
                    }
                }

                /* ===============================
                   TABELA DE CLIENTES
                =============================== */
                const tbody = $('#clientesTableBody');
                tbody.empty();

                if (data.cliente && data.cliente.length > 0) {

                    data.cliente.forEach(cliente => {

                        const statusClass =
                            cliente.status && cliente.status.toUpperCase() === 'ATIVO'
                                ? 'status-ativo'
                                : 'status-inativo';

                        tbody.append(`
                            <tr>
                                <td>
                                    <a href="/clientes/${cliente.sequencia}">
                                        ${cliente.sequencia}
                                    </a>
                                </td>
                                <td>${cliente.nome_fantasia ?? ''}</td>
                                <td>${cliente.razao_social ?? ''}</td>
                                <td>${cliente.cnpj_cpf ?? ''}</td>
                                <td>${cliente.cidade ?? ''}</td>
                                <td class="text-center">
                                    <span class="status-badge ${statusClass}">
                                        ${cliente.status ?? 'N/A'}
                                    </span>
                                </td>
                            </tr>
                        `);
                    });

                } else {
                    tbody.append(`
                        <tr>
                            <td colspan="6" class="text-center">
                                Nenhum cliente relacionado a instalação foi encontrado.
                            </td>
                        </tr>
                    `);
                }

                $('#loadingCliente').addClass('d-none');
            },

            error: function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro ao buscar a instalação',
                    text: 'Não foi possível localizar a instalação.',
                    toast: true,
                    position: 'top-end',
                    timer: 3000,
                    showConfirmButton: false
                });

                $('#loadingCliente').addClass('d-none');
            }
        });
    }, 500);
}

$('#codigo_instalacao').on('change', function () {
    buscarDadosInstalacao(this.value);
});

