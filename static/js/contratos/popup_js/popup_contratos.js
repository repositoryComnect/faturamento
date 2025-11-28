//<!-- Módulo que busca o próximo número de Contrato disponível -->

   document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('createContractModal');

    modal.addEventListener('show.bs.modal', function () {
        // Caminho relativo
        const url = '/proximo_numero_contrato';

        fetch(url)
            .then(response => response.json())
            .then(data => {
                document.getElementById('numero_contrato').value = data.proximo_numero;
            })
            .catch(error => console.error('Erro ao buscar número de contrato:', error));
    });
});



//<!-- Módulo que busca dinâmicamente os produtos disponíveis -->

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('createContractModal');
    
        modal.addEventListener('show.bs.modal', function () {
            // Carrega o próximo número do contrato
            fetch('{{ url_for("contratos_bp.proximo_numero_contrato") }}')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('numero_contrato').value = data.proximo_numero;
                });
    
            // Carrega os produtos ativos
            fetch('{{ url_for("contratos_bp.produtos_ativos") }}')
                .then(response => response.json())
                .then(produtos => {
                    const select = document.getElementById('produto');
                    select.innerHTML = '<option value=""></option>';
                    produtos.forEach(prod => {
                        const option = document.createElement('option');
                        option.value = prod.id;
                        option.textContent = prod.nome;
                        select.appendChild(option);
                    });
                })
                .catch(error => console.error('Erro ao carregar produtos:', error));
        });
    });


//<!-- Módulo que encontra o plano e o valor do plano para o cadastro de contrato -->

    document.addEventListener('DOMContentLoaded', function() {
        const planoSelect = document.getElementById('plano');
        const valorInput = document.getElementById('plan_value');

        fetch('/planos_ativos')
            .then(response => response.json())
            .then(planos => {
                planoSelect.innerHTML = '<option value="">Selecione um plano</option>';
                planos.forEach(plano => {
                    const option = document.createElement('option');
                    option.value = plano.id;
                    option.textContent = `${plano.nome} - R$ ${parseFloat(plano.valor).toFixed(2)}`;
                    option.dataset.valor = plano.valor;  // <- Aqui guardamos o valor
                    planoSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Erro ao carregar os planos:', error);
            });

        planoSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const valor = selectedOption.dataset.valor;
            valorInput.value = valor ? parseFloat(valor).toFixed(2) : '';
        });
    });


//<!-- Módulo para trazer a data atual para poder realizar o cadastro -->

    document.addEventListener('DOMContentLoaded', function () {
        const createModal = document.getElementById('createContractModal');

        if (createModal) {
            createModal.addEventListener('shown.bs.modal', function () {
                const hoje = new Date();
                const dia = String(hoje.getDate()).padStart(2, '0');
                const mes = String(hoje.getMonth() + 1).padStart(2, '0');
                const ano = hoje.getFullYear();
                const dataFormatada = `${dia}/${mes}/${ano}`;

                const camposData = ['cadastramento', 'atualizacao'];
                camposData.forEach(id => {
                    const campo = document.getElementById(id);
                    if (campo && !campo.value) {
                        campo.value = dataFormatada;
                    }
                });
            });
        }
    });


//<!-- Módulo onde eu pego a data atual do Modal de Cadastro-->

    document.addEventListener('DOMContentLoaded', function () {
        const modalElement = document.getElementById('createContractModal');

        // Se Bootstrap não estiver disponível, evita erro
        if (!modalElement || typeof bootstrap === 'undefined') return;

        // Usa Bootstrap 5 Modal API para garantir que está funcionando corretamente
        modalElement.addEventListener('shown.bs.modal', function () {
            const hoje = new Date();
            const dia = String(hoje.getDate()).padStart(2, '0');
            const mes = String(hoje.getMonth() + 1).padStart(2, '0');
            const ano = hoje.getFullYear();
            const dataFormatada = `${dia}/${mes}/${ano}`;

            ['current_datetime', 'update_datetime', 'date_status'].forEach(id => {
                const campo = document.getElementById(id);
                if (campo && !campo.value) {
                    campo.value = dataFormatada;
                }
            });
        });
    });


//<!-- Módulo onde eu pego a data atual do Modal de Editar-->

    document.addEventListener('DOMContentLoaded', function () {
        const modalElement = document.getElementById('updateContractModal');

        // Se Bootstrap não estiver disponível, evita erro
        if (!modalElement || typeof bootstrap === 'undefined') return;

        // Usa Bootstrap 5 Modal API para garantir que está funcionando corretamente
        modalElement.addEventListener('shown.bs.modal', function () {
            const hoje = new Date();
            const dia = String(hoje.getDate()).padStart(2, '0');
            const mes = String(hoje.getMonth() + 1).padStart(2, '0');
            const ano = hoje.getFullYear();
            const dataFormatada = `${dia}/${mes}/${ano}`;

            ['current_datetime_edit', 'update_datetime_edit', 'state_date_edit'].forEach(id => {
                const campo = document.getElementById(id);
                if (campo && !campo.value) {
                    campo.value = dataFormatada;
                }
            });
        });
    });


//<!-- Módulo que encontra o plano e o valor do plano para o edição de contrato -->

    document.addEventListener('DOMContentLoaded', function() {
        const planoSelect = document.getElementById('plan_name_edit');
        const valorInput = document.getElementById('plan_value_edit');

        fetch('/planos_ativos')
            .then(response => response.json())
            .then(planos => {
                planoSelect.innerHTML = '<option value="">Selecione um plano</option>';
                planos.forEach(plano => {
                    const option = document.createElement('option');
                    option.value = plano.id;
                    option.textContent = `${plano.nome} - R$ ${parseFloat(plano.valor).toFixed(2)}`;
                    option.dataset.valor = plano.valor;  // <- Aqui guardamos o valor
                    planoSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Erro ao carregar os planos:', error);
            });

        planoSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const valor = selectedOption.dataset.valor;
            valorInput.value = valor ? parseFloat(valor).toFixed(2) : '';
        });
    });


//<!-- Bloco que me tras os vendedores cadastrados -->

    document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/vendedores')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('vendedor_selecionado');
            select.innerHTML = '<option value="">Selecione um distribuidor</option>';

            data.forEach(vendedor => {
                
                const codigo = vendedor.codigo ?? "Sem código";
                const nome = vendedor.nome;

                const option = document.createElement('option');
                option.value = codigo;
                option.textContent = `${codigo} - ${nome}`; // CONCATENA ID + NOME

                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar vendedores:', error);
            const select = document.getElementById('vendedor_selecionado');
            select.innerHTML = '<option value="">Erro ao carregar vendedores</option>';
        });
});


//<!-- Bloco que me tras as revendas cadastradas -->

  document.addEventListener('DOMContentLoaded', function () {
    fetch('/revendas_ativas')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('revenda_selecionada');

            select.innerHTML = '<option value="">Selecione uma revenda</option>';

            data.forEach(revenda => {

                const codigo = revenda.codigo ?? "SEM CÓDIGO";
                const nome = revenda.nome;

                const option = document.createElement('option');

                option.value = codigo;  
                option.textContent = `${codigo} - ${nome}`;

                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar revendas:', error);
            const select = document.getElementById('revenda_selecionada');
            select.innerHTML = '<option value="">Erro ao carregar revendas</option>';
        });
});






$(document).ready(function () {

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

    const $input = $('#fetch_contract');
    const $spinner = $('#loadingContrato');

    // Desabilita o campo e mostra o spinner
    $input.prop('disabled', true);
    $spinner.removeClass('d-none');

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
            'id_matriz_portal': '#id_edit_portal',
            'address_email': '#email_edit_contract',
            'telefone': '#phone',
            'responsavel': '#responsible',
            'zip_code_cep': '#zip_code_edit',
            'cnpj_cpf': '#cnpj_cpf',
            'endereco': '#address',
            'complemento': '#complement',
            'bairro': '#neighborhood',
            'cidade': '#city',
            'estado': '#state',
            'fator_juros': '#interest_rate_factor',
            'dia_vencimento': '#last_day',
            'estado_contrato': '#current_state',
            'data_estado': '#state_date',
            'motivo_estado': '#reason', 
            'observacao': '#observacao_contrato_editar'
          };

          for (const key in fieldMap) {
            if (contrato[key] !== null && contrato[key] !== undefined) {
              const val = key.includes('data') ? formatarData(contrato[key]) : contrato[key];
              $(fieldMap[key]).val(val);
            }
          }

          // Popup de sucesso
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
          // Popup de aviso (não encontrado)
          Swal.fire({
            icon: 'warning',
            title: 'Contrato não encontrado',
            text: 'Verifique o número ou nome informado e tente novamente.',
            timer: 5000,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
          });
        }
      },

      error: function(xhr, status, error) {
        console.error("Erro:", status, error);
        Swal.fire({
          icon: 'error',
          title: 'Erro ao buscar contrato',
          text: 'Ocorreu um problema na comunicação com o servidor.',
          timer: 4000,
          showConfirmButton: false,
          toast: true,
          position: 'top-end'
        });
      },

      complete: function() {
        // Reabilita o campo e oculta o spinner
        $input.prop('disabled', false);
        $spinner.addClass('d-none');
      }
    });
  }

  // Função para formatar data (yyyy-mm-dd)
  function formatarData(data) {
    const d = new Date(data);
    return !isNaN(d)
      ? `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
      : '';
  }

  // Clique no botão de busca
  $('#btnBuscarContrato').on('click', function() {
    console.log(" Botão de busca clicado");
    buscarContrato($('#fetch_contract').val());
  });

  // Pressionar Enter no campo
  $('#fetch_contract').on('keypress', function(e) {
    if (e.which === 13) { // tecla Enter
      e.preventDefault();
      buscarContrato($(this).val());
    }
  });
});

//<!-- Bloco que traz os clientes cadastrados -->

   document.addEventListener('DOMContentLoaded', function () {
    fetch('/get/list/clientes')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('cliente_selecionado');
            select.innerHTML = '<option value="">Vincule um cliente</option>';

            data.forEach(cliente => {

                const codigo = cliente.codigo ?? "SEM-CODIGO";
                const nome = cliente.razao_social;
                const documento = cliente.cnpj_cpf ?? "";

                const option = document.createElement('option');
                option.value = cliente.id; // backend recebe ID

                // TEXTO EXIBIDO CONCATENADO
                option.textContent = `${codigo} - ${nome} (${documento})`;

                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar clientes:', error);
            const select = document.getElementById('cliente_selecionado');
            select.innerHTML = '<option value="">Erro ao carregar clientes</option>';
        });
});
    
//<!-- Bloco do popup de Delete contratos -->

    document.addEventListener('DOMContentLoaded', function () {
        const deleteModal = document.getElementById('deleteContractModal');
        const validateBtn = document.getElementById('validateBtn');
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        const unlinkOptions = document.getElementById('unlinkOptions');
        const validationResults = document.getElementById('validationResults');
        const clientsCountText = document.getElementById('clientsCountText');
        const contractNumberInput = document.getElementById('delete_numero_contrato');
        const contractInfo = document.getElementById('contractInfo');
        const contractNumberDisplay = document.getElementById('contractNumberDisplay');
        const contractSequenceDisplay = document.getElementById('contractSequenceDisplay');
    
        let currentContract = null;
    
        // Verificação
        validateBtn.addEventListener('click', async function () {
            const numeroContrato = contractNumberInput.value.trim();
    
            if (!numeroContrato) {
                showValidationResult('Por favor, informe o número do contrato', 'danger');
                return;
            }
    
            try {
                showValidationResult('Verificando contrato...', 'info');
                validateBtn.disabled = true;
    
                const response = await fetch('/contratos/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'numero': numeroContrato,
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
                    currentContract = data.contrato;
                    contractNumberDisplay.textContent = currentContract.numero;
                    contractSequenceDisplay.textContent = `${currentContract.cliente_sequencia  || '-' } - ${currentContract.cliente_fantasia || '-' } - ${currentContract.cliente_cnpj || '-' }`;

                    contractInfo.classList.remove('d-none');
    
                    if (data.hasClients) {
                        showValidationResult('Contrato encontrado com clientes vinculados', 'warning');
                        unlinkOptions.classList.remove('d-none');
                        confirmDeleteBtn.classList.remove('d-none');
                        confirmDeleteBtn.textContent = 'Excluir';
                        validateBtn.classList.add('d-none');
                    } else {
                        showValidationResult('Contrato pode ser excluído sem problemas', 'success');
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
    
        // Exclusão ou desvinculação
        confirmDeleteBtn.addEventListener('click', async function () {
            if (!currentContract) return;
    
            const action = confirmDeleteBtn.dataset.nextAction ||
                (document.querySelector('input[name="unlinkOption"]:checked')?.value === 'justUnlink' ? 'unlink' : 'delete');
    
            confirmDeleteBtn.disabled = true;
    
            try {
                await fetch('/contratos/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'numero': currentContract.numero,
                        'action': action
                    })
                });
    
                // Fecha o modal e recarrega a página após 1 segundo
                const modal = bootstrap.Modal.getInstance(deleteModal);
                modal.hide();
                setTimeout(() => window.location.reload(), 1000);
    
            } catch (error) {
                console.error('Erro ao enviar requisição de exclusão:', error);
                confirmDeleteBtn.disabled = false;
            }
        });
    
        // Reset do modal
        deleteModal.addEventListener('hidden.bs.modal', function () {
            contractNumberInput.value = '';
            validationResults.innerHTML = '';
            contractInfo.classList.add('d-none');
            unlinkOptions.classList.add('d-none');
            confirmDeleteBtn.classList.add('d-none');
            validateBtn.classList.remove('d-none');
            validateBtn.disabled = false;
            confirmDeleteBtn.dataset.nextAction = '';
        });
    
        // Função para exibir mensagens
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
