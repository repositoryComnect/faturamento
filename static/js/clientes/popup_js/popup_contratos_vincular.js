// Script que retorna os contratos
document.addEventListener('DOMContentLoaded', function () {
    let contratosCarregados = false;

    function carregarContratos() {
        if (contratosCarregados) return;

        fetch('/api/contratos/numeros')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao carregar contratos');
                }
                return response.json();
            })
            .then(contratos => {
                const selectContratos = document.getElementById('contrato_id');
                selectContratos.innerHTML = '';

                contratos.forEach(contrato => {
                    const option = document.createElement('option');
                    option.value = contrato.numero;
                    option.textContent =
                        `${contrato.numero} - ${contrato.razao_social || contrato.nome_fantasia || ''}`;
                    selectContratos.appendChild(option);
                });

                contratosCarregados = true;
            })
            .catch(error => {
                console.error(error);
                alert('Erro ao carregar contratos.');
            });
    }

    //  Carregar contratos quando o modal abrir
    const modal = document.getElementById('vincularContractModal');
    if (modal) {
        modal.addEventListener('shown.bs.modal', function () {
            carregarContratos();
        });
    }

});


// Script que retorna os clientes
document.addEventListener('DOMContentLoaded', function () {
    let clientesCarregados = false;

    function carregarClientes() {
        if (clientesCarregados) return;

        fetch('/get/list/clientes')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao buscar clientes');
                }
                return response.json();
            })
            .then(clientes => {
                const selectClientes = document.getElementById('selecione_cliente');
                selectClientes.innerHTML = '<option value="">Selecione um cliente</option>';

                clientes.forEach(cliente => {
                    const option = document.createElement('option');
                    option.value = cliente.id; 
                    option.textContent = `${cliente.codigo} - ${cliente.razao_social} - ${cliente.cnpj_cpf}`;
                    selectClientes.appendChild(option);
                });

                clientesCarregados = true;
            })
            .catch(error => {
                console.error('Erro ao buscar clientes:', error);
                const selectClientes = document.getElementById('selecione_cliente');
                selectClientes.innerHTML = '<option value="">Erro ao carregar clientes</option>';
            });
    }

    // Carrega clientes quando o modal abrir
    const modal = document.getElementById('vincularContractModal');
    if (modal) {
        modal.addEventListener('shown.bs.modal', function () {
            carregarClientes();
        });
    }

});
