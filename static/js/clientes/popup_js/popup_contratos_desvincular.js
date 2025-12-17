document.addEventListener("DOMContentLoaded", function () {
    const clienteSelect = document.getElementById("desvincular_contrato_id");
    const contratoSelect = document.getElementById("contratos_vinculados");
    const modal = document.getElementById("desvincularContractModal");
    const form = modal.querySelector("form");

    modal.addEventListener("show.bs.modal", function () {
        fetch("/get/list/clientes")
            .then(response => response.json())
            .then(clientes => {
                clienteSelect.innerHTML =
                    "<option disabled selected value=''>Selecione um cliente</option>";

                clientes.forEach(cliente => {
                    const option = document.createElement("option");
                    option.value = cliente.id;
                    option.text = `${cliente.codigo} - ${cliente.razao_social}`;
                    clienteSelect.appendChild(option);
                });
            });
    });

    clienteSelect.addEventListener("change", function () {
        const clienteId = this.value;

        if (!clienteId) return;

        fetch(`/get/contratos_por_clientes/${clienteId}`)
            .then(response => response.json())
            .then(contratos => {
                contratoSelect.innerHTML = "";

                if (contratos.length === 0) {
                    const option = document.createElement("option");
                    option.disabled = true;
                    option.text = "Nenhum contrato vinculado.";
                    contratoSelect.appendChild(option);
                } else {
                    contratos.forEach(contrato => {
                        const option = document.createElement("option");
                        option.value = contrato.id;
                        option.text = `${contrato.numero} - ${contrato.razao_social}`;
                        contratoSelect.appendChild(option);
                    });
                }
            });
    });

    form.addEventListener("submit", function (e) {
        if (contratoSelect.selectedOptions.length === 0) {
            e.preventDefault();
            alert("Selecione ao menos um contrato para desvincular.");
        } else {
            form.action = "/desvincular-contratos";
        }
    });
});
