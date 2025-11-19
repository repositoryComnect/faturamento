 document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById('vincularPlanoContractModal');

    if (!modal) {
        console.error("Modal NÃO encontrado!");
        return;
    }

    modal.addEventListener('shown.bs.modal', function () {

        console.log("Modal abriu: carregando contratos...");

        // CARREGAR CONTRATOS
        fetch("/contratos_ativos")
            .then(response => response.json())
            .then(data => {

                console.log("Contratos recebidos:", data);

                const contratoSelect = document.getElementById("contrato_id_vincular_plano");

                if (!contratoSelect) {
                    console.error("Select de contratos (contrato_id_vincular_plano) NÃO encontrado!");
                    return;
                }

                contratoSelect.innerHTML = "<option value='' disabled selected>Selecione um contrato</option>";

                data.forEach(contrato => {
                    const option = document.createElement("option");
                    option.value = contrato.id;
                    option.textContent = `${contrato.numero} - ${contrato.razao_social}`;
                    contratoSelect.appendChild(option);
                });
            })
            .catch(error => console.error("Erro ao carregar contratos:", error));


        // CARREGAR PLANOS
        fetch("/planos_ativos")
            .then(response => response.json())
            .then(data => {

                console.log("Planos recebidos:", data);

                const planoSelect = document.getElementById("plano_ids");

                if (!planoSelect) {
                    console.error("Select de planos (plano_ids) NÃO encontrado!");
                    return;
                }

                planoSelect.innerHTML = "<option value='' disabled selected>Selecione um plano</option>";

                data.forEach(plano => {
                    const option = document.createElement("option");
                    option.value = plano.id;
                    option.textContent = `${plano.codigo} - ${plano.nome} - R$ ${plano.valor}`;
                    planoSelect.appendChild(option);
                });
            })
            .catch(error => console.error("Erro ao carregar planos:", error));
    });
});

