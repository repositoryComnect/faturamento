(() => {
    document.addEventListener('DOMContentLoaded', function() {
        let contratosCarregados = false;

        // 🔹 Carregar contratos disponíveis
        function carregarContratosDisponiveis() {
            if (contratosCarregados) return;

            fetch('/api/contratos/numeros')
                .then(response => {
                    if (!response.ok) throw new Error('Erro ao carregar contratos');
                    return response.json();
                })
                .then(contratos => {
                    const select = document.getElementById('cliente_contratos_associados');
                    if (!select) return;

                    select.innerHTML = ''; // Limpa opções duplicadas
                    contratos.forEach(contrato => {
                        const option = document.createElement('option');
                        option.value = contrato.numero;
                        option.textContent = `${contrato.numero} - ${contrato.razao_social || contrato.nome_fantasia || ''}`;
                        select.appendChild(option);
                    });

                    contratosCarregados = true;
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro ao carregar lista de contratos. Por favor, recarregue a página.');
                });
        }

        carregarContratosDisponiveis();

        // 🔹 Máscara CNPJ/CPF
        const cnpjField = document.getElementById('numero_documento');
        if (cnpjField) {
            cnpjField.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 11) { // CNPJ
                    value = value.replace(/^(\d{2})(\d)/, '$1.$2');
                    value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
                    value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
                    value = value.replace(/(\d{4})(\d)/, '$1-$2');
                } else { // CPF
                    value = value.replace(/^(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/\.(\d{3})(\d)/, '.$1.$2');
                    value = value.replace(/\.(\d{3})(\d)/, '.$1-$2');
                }
                e.target.value = value;
            });
        }

        // 🔹 Validação formulário
        const form = document.getElementById('clientForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                const razaoSocial = document.getElementById('razao_social')?.value.trim();
                const cnpj = document.getElementById('numero_documento')?.value.trim();

                if (!razaoSocial || !cnpj) {
                    e.preventDefault();
                    alert('Por favor, preencha a Razão Social e CNPJ/CPF corretamente.');
                }
            });
        }
    });

    // 🔹 Buscar próxima sequência ao abrir o modal
    document.addEventListener('DOMContentLoaded', function () {
        const createClientModal = document.getElementById('cliente_createModal');
        if (!createClientModal) return;

        createClientModal.addEventListener('show.bs.modal', function () {
            fetch('/proxima_sequencia_cliente')
                .then(res => res.json())
                .then(data => {
                    const input = document.getElementById('cliente_sequencia');
                    if (input) input.value = data.proxima_sequencia || '';
                })
                .catch(err => console.error('Erro ao buscar sequência do cliente:', err));
        });
    });

    // 🔹 Data atual - Set Cliente
    document.addEventListener("DOMContentLoaded", () => {
        const hoje = new Date();
        const dataFormatada = hoje.toLocaleDateString('pt-BR');
        const modal = document.getElementById('cliente_createModal');
        if (!modal) return;

        modal.addEventListener('shown.bs.modal', () => {
            ['cliente_cadastramento', 'cliente_atualizacao', 'date_state'].forEach(id => {
                const campo = document.getElementById(id);
                if (campo && !campo.value) campo.value = dataFormatada;
            });
        });
    });


    // 🔹 Buscar contrato (isolado para evitar conflito com timeoutId)
    (() => {
        let timeoutBuscaContrato;

        function formatarData(data) {
            const d = new Date(data);
            return !isNaN(d)
                ? `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}`
                : '';
        }

        // Função principal de busca de contrato
        function buscarContrato(termo) {
            if (!termo) {
            Swal.fire({
                icon: 'warning',
                title: 'Campo vazio',
                text: 'Digite o número ou nome do contrato antes de buscar.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
            return;
            }

            timeoutBuscaContrato = setTimeout(() => {
                $.ajax({
                    url: '/buscar_contrato',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ termo }),
                    success: function(data) {
                        if (data.success) {
                            const contrato = data.contrato;
                            const map = {
                                'numero': '#cliente_numero_contrato',
                                'razao_social': '#cliente_nome_empresa',
                                'nome_fantasia': '#cliente_nome_fantasia',
                                'tipo': '#cliente_tipo',
                                'contato': '#contact',
                                'id_matriz_portal': '#id_matriz_portal',
                                'address_email': '#cliente_email',
                                'telefone': '#cliente_telefone',
                                'contato': '#cliente_contato',
                                'zip_code_cep': '#cliente_cep',
                                'cnpj_cpf': '#cliente_cnpj_cpf',
                                'endereco': '#cliente_endereco',
                                'complemento': '#cliente_complemento',
                                'bairro': '#cliente_bairro',
                                'cidade': '#cliente_cidade',
                                'estado': '#cliente_uf',
                                'fator_juros': '#interest_rate_factor',
                                'dia_vencimento': '#last_day',
                                'estado_contrato': '#current_state',
                                'data_estado': '#state_date',
                                'motivo_estado': '#reason'
                            };

                            for (const key in map) {
                                if (contrato[key] != null) {
                                    const val = key.includes('data') ? formatarData(contrato[key]) : contrato[key];
                                    $(map[key]).val(val);
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
            }, 800);
        }

        $('#cliente_buscar_contrato').on('input', function() {
            buscarContrato($(this).val());
        });
    })();

})();



