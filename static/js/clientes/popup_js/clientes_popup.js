    document.addEventListener('DOMContentLoaded', function() {
        let contratosCarregados = false;

        // Função para carregar os contratos disponíveis
        function carregarContratosDisponiveis() {
            if (contratosCarregados) return;

            fetch('/api/contratos/numeros')
                .then(response => {
                    if (!response.ok) throw new Error('Erro ao carregar contratos');
                    return response.json();
                })
                .then(contratos => {
                    const select = document.getElementById('contratos_associados');
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

        // Executa uma vez ao carregar a página
        carregarContratosDisponiveis();
        const cnpjField = document.getElementById('numero_documento');
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

        // Validação do formulário antes de enviar
        document.getElementById('clientForm').addEventListener('submit', function(e) {
            const razaoSocial = document.getElementById('razao_social').value.trim();
            const cnpj = document.getElementById('numero_documento').value.trim();

            if (!razaoSocial || !cnpj) {
                e.preventDefault();
                alert('Por favor, preencha a Razão Social e CNPJ/CPF corretamente.');
                return false;
            }

            return true;
        });
    });


// Bloco responsável pelo PopUp Delete 
    document.addEventListener('DOMContentLoaded', function() {
        const deleteModal = document.getElementById('deleteClientModal');
        const validateBtn = document.getElementById('validateBtn');
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        const unlinkOptions = document.getElementById('unlinkOptions');
        const validationResults = document.getElementById('validationResults');
        const contractsCountText = document.getElementById('contractsCountText');
        const clientNumberInput = document.getElementById('delete_numero_cliente');
        const clientInfo = document.getElementById('clientInfo');
        const clientNameDisplay = document.getElementById('clientNameDisplay');
        const clientNumberDisplay = document.getElementById('clientNumberDisplay');
        
        let currentClient = null;
    
        // Botão de verificação
        validateBtn.addEventListener('click', async function() {
            const numeroCliente = clientNumberInput.value.trim();
            
            if (!numeroCliente) {
                showValidationResult('Por favor, informe o número do cliente', 'danger');
                return;
            }
            
            try {
                showValidationResult('Verificando cliente...', 'info');
                validateBtn.disabled = true;
                
                const response = await fetch('/delete/cliente', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'numero': numeroCliente,
                        'action': 'check'
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showValidationResult(data.message, 'danger');
                    validateBtn.disabled = false;
                    return;
                }
                
                if (data.success) {
                    currentClient = data.cliente;
                    clientNameDisplay.textContent = currentClient.razao_social;
                    clientNumberDisplay.textContent = currentClient.numero_contrato;  // Garantindo que o número do contrato seja exibido
                    clientInfo.classList.remove('d-none');
                    
                    if (data.hasContracts) {
                        showValidationResult('Cliente encontrado com contratos vinculados', 'warning');
                        contractsCountText.textContent = `Possui ${data.count} contrato(s) vinculado(s).`;
                        unlinkOptions.classList.remove('d-none');
                        confirmDeleteBtn.classList.remove('d-none');
                        confirmDeleteBtn.textContent = 'Desvincular e Excluir';
                        validateBtn.classList.add('d-none');
                    } else {
                        showValidationResult('Cliente pode ser excluído sem problemas', 'success');
                        confirmDeleteBtn.classList.remove('d-none');
                        confirmDeleteBtn.textContent = 'Confirmar Exclusão';
                        validateBtn.classList.add('d-none');
                    }
                }
                
            } catch (error) {
                showValidationResult('Erro ao comunicar com o servidor', 'danger');
                console.error(error);
                validateBtn.disabled = false;
            }
        });
    
        // Botão de confirmação
        confirmDeleteBtn.addEventListener('click', async function() {
            if (!currentClient) return;
            
            const action = confirmDeleteBtn.dataset.nextAction || 
                (document.querySelector('input[name="unlinkOption"]:checked')?.value === 'justUnlink' ? 'unlink' : 'delete');
    
            try {
                showValidationResult('Processando solicitação...', 'info');
                confirmDeleteBtn.disabled = true;
                
                const response = await fetch('/delete/cliente', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'numero': currentClient.sequencia,  // Usando a SEQUENCIA do cliente
                        'action': action
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showValidationResult(data.message, 'danger');
                    confirmDeleteBtn.disabled = false;
                    return;
                }
                
                if (data.success) {
                    if (action === 'unlink') {
                        showValidationResult('Contratos desvinculados com sucesso!', 'success');
        
                        contractsCountText.textContent = 'Nenhum contrato vinculado';
                        unlinkOptions.classList.add('d-none');
                        
                        confirmDeleteBtn.textContent = 'Confirmar Exclusão';
                        confirmDeleteBtn.classList.remove('btn-warning');
                        confirmDeleteBtn.classList.add('btn-danger');
    
                        // 👉 Aqui é o principal:
                        confirmDeleteBtn.dataset.nextAction = 'delete';  // Prepara o próximo clique para excluir
                        
                        confirmDeleteBtn.disabled = false;
                    } else {
                        // Excluiu de fato: fecha modal e recarrega
                        const modal = bootstrap.Modal.getInstance(deleteModal);
                        modal.hide();
                        setTimeout(() => window.location.reload(), 1000);
                    }
                }
                
            } catch (error) {
                showValidationResult('Erro ao processar a solicitação', 'danger');
                console.error(error);
                confirmDeleteBtn.disabled = false;
            }
        });
    
        // Reset ao fechar o modal
        deleteModal.addEventListener('hidden.bs.modal', function() {
            clientNumberInput.value = '';
            validationResults.innerHTML = '';
            clientInfo.classList.add('d-none');
            unlinkOptions.classList.add('d-none');
            confirmDeleteBtn.classList.add('d-none');
            validateBtn.classList.remove('d-none');
            validateBtn.disabled = false;
        });
    
        // Função para mostrar os resultados da validação
        function showValidationResult(message, type) {
            const types = {
                success: 'alert-success',
                danger: 'alert-danger',
                warning: 'alert-warning',
                info: 'alert-info'
            };
            
            validationResults.innerHTML = `
                <div class="alert ${types[type]}" role="alert">
                    ${message}
                </div>
            `;
        }
    });


//<!-- Bloco responsável por buscar o próximo número da sequência -->

    document.addEventListener('DOMContentLoaded', function () {
        const createClientModal = document.getElementById('createClientModal');
    
        createClientModal.addEventListener('show.bs.modal', function () {
            fetch('/proxima_sequencia_cliente')
                .then(response => response.json())
                .then(data => {
                    const inputSequencia = document.getElementById('sequencia_cliente');
                    inputSequencia.value = data.proxima_sequencia || '';
                })
                .catch(error => {
                    console.error('Erro ao buscar sequência do cliente:', error);
                });
        });
    });

    
//<!-- Bloco para resgatar a data atual PopUp Set Cliente-->

    document.addEventListener("DOMContentLoaded", function () {
        const hoje = new Date();
        const dia = String(hoje.getDate()).padStart(2, '0');
        const mes = String(hoje.getMonth() + 1).padStart(2, '0'); // Janeiro = 0
        const ano = hoje.getFullYear();
        const dataFormatada = `${dia}/${mes}/${ano}`;

        const camposData = ['registration', 'update', 'date_state'];
        camposData.forEach(id => {
            const campo = document.getElementById(id);
            if (campo && !campo.value) {
                campo.value = dataFormatada;
            }
        });
    });


//<!-- Bloco para resgatar a data atual PopUp Edit Cliente-->

    document.addEventListener("DOMContentLoaded", function () {
        const hoje = new Date();
        const dia = String(hoje.getDate()).padStart(2, '0');
        const mes = String(hoje.getMonth() + 1).padStart(2, '0'); // Janeiro = 0
        const ano = hoje.getFullYear();
        const dataFormatada = `${dia}/${mes}/${ano}`;

        const camposData = ['registry', 'registry_update'];
        camposData.forEach(id => {
            const campo = document.getElementById(id);
            if (campo && !campo.value) {
                campo.value = dataFormatada;
            }
        });
    });


// 🔹 Buscar cliente manualmente (clique ou Enter)
document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ DOM totalmente carregado — script ativo.");

    let timeoutSeguenceEditId;

    // Função de formatação de data
    function formatarData(data) {
        const date = new Date(data);
        if (isNaN(date)) return '';
        return date.toISOString().split('T')[0]; // yyyy-mm-dd
    }

    // Função principal de busca
    function buscarCliente(termo) {
        console.log("🔎 Função buscarCliente chamada com termo:", termo);

        if (!termo) {
            Swal.fire({
                icon: 'warning',
                title: 'Campo vazio',
                text: 'Digite o nome, razão social ou CNPJ antes de buscar.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
            return;
        }

        $('#loadingCliente').removeClass('d-none');
        clearTimeout(timeoutSeguenceEditId);

        timeoutSeguenceEditId = setTimeout(() => {
            console.log("📡 Enviando requisição AJAX para /buscar_cliente ...");

            $.ajax({
                url: '/buscar_cliente',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ termo }),

                success: function (data) {
                    console.log("✅ Dados recebidos do servidor:", data);

                    if (data.success) {
                        const cliente = data.cliente;
                        const fieldMap = {
                            'sequel': '#sequel',
                            'corporate_name': '#razao_social_editar_popup',
                            'second_name': '#second_name',
                            'cadastramento': '#registration',
                            'atualizacao': '#update',
                            'tipo': '#type',
                            'cnpj_cpf': '#cnpj_cpf_editar_popup',
                            'ie': '#state_registration',
                            'im': '#municipal_registration',
                            'email_address': '#email_address',
                            'phone_number': '#phone_number',
                            'cep': '#postal_code',
                            'street': '#street',
                            'comp': '#comp',
                            'neighbor': '#neighbor',
                            'cit': '#cit',
                            'state_uf': '#state_uf',
                            'fator_juros': '#interest_rate_factor',
                            'plano_nome': '#plan_name',
                            'dia_vencimento': '#due_day',
                            'observacao': '#observations',
                            'data_estado': '#state_date',
                            'contato': '#contact'
                        };

                        for (const key in fieldMap) {
                            const fieldSelector = fieldMap[key];
                            const fieldValue = cliente[key];
                            if (fieldValue !== null && fieldValue !== undefined) {
                                if (['atualizacao', 'cadastramento', 'data_estado'].includes(key)) {
                                    $(fieldSelector).val(formatarData(fieldValue));
                                } else {
                                    $(fieldSelector).val(fieldValue);
                                }
                            }
                        }

                        Swal.fire({
                            icon: 'success',
                            title: 'Cliente encontrado!',
                            text: 'Os dados foram carregados com sucesso.',
                            toast: true,
                            timer: 2500,
                            position: 'top-end',
                            showConfirmButton: false
                        });

                    } else {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Cliente não encontrado',
                            text: 'Verifique o nome, razão social ou CNPJ informado.',
                            timer: 5000,
                            toast: true,
                            position: 'top-end',
                            showConfirmButton: false
                        });
                    }

                    $('#loadingCliente').addClass('d-none');
                },

                error: function (xhr, status, error) {
                    console.error("❌ Erro na requisição:", status, error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro ao buscar cliente',
                        text: 'Ocorreu um problema na comunicação com o servidor.',
                        timer: 4000,
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false
                    });
                    $('#loadingCliente').addClass('d-none');
                }
            });
        }, 500);
    }

    // 🔹 Clique do botão
    $('#btnBuscarCliente').on('click', function () {
        console.log("🖱️ Botão de busca clicado!");
        buscarCliente($('#search_edit_client').val());
    });

    // 🔹 Pressionar Enter no campo
    $('#search_edit_client').on('keypress', function (e) {
        if (e.which === 13) {
            console.log("⌨️ Enter pressionado!");
            e.preventDefault();
            buscarCliente($(this).val());
        }
    });
});





//<!-- Bloco que me tras as revendas cadastradas -->

    document.addEventListener('DOMContentLoaded', function () {
        fetch('/revendas_ativas/cliente')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('revenda_selecionada_client');
                select.innerHTML = '<option value="">Selecione uma revenda</option>';

                data.forEach(nome => {
                    const option = document.createElement('option');
                    option.value = nome;       // Usando o nome como valor
                    option.textContent = nome; // Mostrando o nome
                    select.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Erro ao buscar revendas:', error);
                const select = document.getElementById('revenda_selecionada_client');
                select.innerHTML = '<option value="">Erro ao carregar revendas</option>';
            });
    });



//<!-- Bloco que me tras os vendedores cadastrados -->

    document.addEventListener('DOMContentLoaded', function () {
        fetch('/api/vendedores')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('vendedor_selecionado_client');
                select.innerHTML = '<option value="">Selecione um vendedor</option>';

                data.forEach(vendedor => {
                    // Criação de um novo <option> para cada vendedor
                    const option = document.createElement('option');
                    option.value = vendedor.id;  // Usando 'id' para associar o vendedor
                    option.textContent = vendedor.nome;  // Exibindo o 'nome' do vendedor
                    select.appendChild(option);  // Adiciona a opção ao select
                });
            })
            .catch(error => {
                console.error('Erro ao buscar vendedores:', error);
                const select = document.getElementById('vendedor_selecionado_client');
                select.innerHTML = '<option value="">Erro ao carregar vendedores</option>';
            });
    });


// Bloco buscar contrato set cliente -->
document.addEventListener('DOMContentLoaded', function () {
    console.log("Script buscarContrato ativo");

    let timeoutId;

    function formatarData(data) {
        const d = new Date(data);
        if (isNaN(d)) return '';
        return `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}`;
    }

    function buscarContrato(termo) {
        console.log("Buscando contrato com termo:", termo);

        if (!termo) {
            Swal.fire({
                icon: 'warning',
                title: 'Campo vazio',
                text: 'Digite o número do contrato ou nome antes de buscar.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
            return;
        }

        $('#loadingContrato').removeClass('d-none');
        clearTimeout(timeoutId);

        timeoutId = setTimeout(() => {
            $.ajax({
                url: '/buscar_contrato',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ termo: termo }),
                success: function (data) {
                    console.log("Dados recebidos:", data);

                    if (data.success) {
                        const contrato = data.contrato;

                        const fieldMap = {
                            'numero': '#contract_number',
                            'razao_social': '#company_name',
                            'nome_fantasia': '#trade_name',
                            'tipo': '#tipo_cliente',
                            'contato': '#contact',
                            'id_matriz_portal': '#id_matriz_portal',
                            'address_email': '#address_email',
                            'telefone': '#phone',
                            'responsavel': '#responsible',
                            'zip_code_cep': '#zip_code_cep',
                            'cnpj_cpf': '#cnpj_cpf_cliente',
                            'endereco': '#address',
                            'complemento': '#complement',
                            'bairro': '#neighborhood',
                            'cidade': '#city',
                            'estado': '#state',
                            'fator_juros': '#interest_rate_factor',
                            'dia_vencimento': '#last_day',
                            'estado_contrato': '#current_state',
                            'data_estado': '#state_date',
                            'motivo_estado': '#reason'
                        };

                        for (const key in fieldMap) {
                            const fieldSelector = fieldMap[key];
                            if (contrato[key] !== null && contrato[key] !== undefined) {
                                const val = key.includes('data') ? formatarData(contrato[key]) : contrato[key];
                                $(fieldSelector).val(val);
                            }
                        }

                        Swal.fire({
                            icon: 'success',
                            title: 'Contrato encontrado!',
                            text: 'Os dados foram carregados com sucesso.',
                            toast: true,
                            position: 'top-end',
                            timer: 2500,
                            showConfirmButton: false
                        });

                    } else {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Contrato não encontrado',
                            text: 'Verifique o número ou nome informado.',
                            toast: true,
                            position: 'top-end',
                            timer: 4000,
                            showConfirmButton: false
                        });
                    }

                    $('#loadingContrato').addClass('d-none');
                },
                error: function (xhr, status, error) {
                    console.error("❌ Erro ao buscar contrato:", status, error);

                    Swal.fire({
                        icon: 'error',
                        title: 'Erro ao buscar contrato',
                        text: 'Ocorreu um problema na comunicação com o servidor.',
                        toast: true,
                        position: 'top-end',
                        timer: 4000,
                        showConfirmButton: false
                    });

                    $('#loadingContrato').addClass('d-none');
                }
            });
        }, 600);
    }

    // Clique no botão de busca
    $('#btnBuscarContrato').on('click', function () {
        console.log("Clique no botão de busca de contrato");
        buscarContrato($('#search_contract').val());
    });

    // Pressionar Enter no campo
    $('#search_contract').on('keypress', function (e) {
        if (e.which === 13) {
            console.log("Enter pressionado no campo de busca de contrato");
            e.preventDefault();
            buscarContrato($(this).val());
        }
    });
});
