document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("desvincularContractPlanoModal");
    const planoSelect = document.getElementById("plano_desvincular_contrato");
    const contratosSelect = document.getElementById("contratos_vinculados_planos");

    if (!modal) {
        console.error("Modal desvincularContractPlanoModal NÃO encontrado!");
        return;
    }

    if (!planoSelect) {
        console.error("Select desvincular_plano_id NÃO encontrado!");
        return;
    }

    if (!contratosSelect) {
        console.error("Select contratos_vinculados_planos NÃO encontrado!");
        return;
    }

    modal.addEventListener("shown.bs.modal", function () {

        console.log("Modal aberto: carregando planos ativos...");

        planoSelect.innerHTML =
            "<option value='' disabled selected>Selecione um plano</option>";
        contratosSelect.innerHTML = "";

        fetch("/planos_ativos/contratos")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erro ao buscar planos ativos");
                }
                return response.json();
            })
            .then(data => {

                console.log("Planos recebidos:", data);

                if (!data.length) {
                    const option = document.createElement("option");
                    option.disabled = true;
                    option.textContent = "Nenhum plano ativo encontrado";
                    planoSelect.appendChild(option);
                    return;
                }

                data.forEach(plano => {
                    const option = document.createElement("option");
                    option.value = plano.id;
                    option.textContent = `${plano.codigo} - ${plano.nome}`;
                    planoSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Erro ao carregar planos:", error);
            });
    });

    planoSelect.addEventListener("change", function () {

        const planoId = this.value;

        if (!planoId) {
            contratosSelect.innerHTML = "";
            return;
        }

        console.log("Plano selecionado:", planoId);
        console.log("Buscando contratos vinculados...");

        contratosSelect.innerHTML = "";

        fetch(`/get/contratos_por_plano/${planoId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erro ao buscar contratos do plano");
                }
                return response.json();
            })
            .then(data => {

                console.log("Contratos vinculados recebidos:", data);

                if (!data.length) {
                    const option = document.createElement("option");
                    option.disabled = true;
                    option.textContent = "Nenhum contrato vinculado a este plano";
                    contratosSelect.appendChild(option);
                    return;
                }

                data.forEach(contrato => {
                    const option = document.createElement("option");
                    option.value = contrato.id;
                    option.textContent =
                        `${contrato.numero} - ${contrato.razao_social || ""}`;
                    contratosSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Erro ao carregar contratos vinculados:", error);
            });
    });

});
