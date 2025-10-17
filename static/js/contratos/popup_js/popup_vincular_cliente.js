document.addEventListener("DOMContentLoaded", function () {
        const clienteSelect = document.getElementById("cliente_ids");
        const contratoSelect = document.getElementById("selecione_contrato");
        const modal = document.getElementById('vincularContractModal');
    
        modal.addEventListener('show.bs.modal', function () {
            fetch("/list/contratos_ativos")
                .then(response => response.json())
                .then(data => {
                    contratoSelect.innerHTML = "<option value='' disabled selected>Selecione um contrato</option>";
                    data.forEach(contrato => {
                        const option = document.createElement("option");
                        option.value = contrato.id;
                        option.text = `${contrato.numero} - ${contrato.razao_social}`;
                        contratoSelect.appendChild(option);
                    });
                })
                .catch(error => console.error("Erro ao carregar contratos:", error));
    
            fetch("/get/list/clientes")
                .then(response => response.json())
                .then(data => {
                    clienteSelect.innerHTML = "";
                    data.forEach(cliente => {
                        const option = document.createElement("option");
                        option.value = cliente.id;
                        option.text = cliente.razao_social;
                        clienteSelect.appendChild(option);
                    });
                })
                .catch(error => console.error("Erro ao carregar clientes:", error));
        });
    });