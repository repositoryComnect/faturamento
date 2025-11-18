document.addEventListener("DOMContentLoaded", function () {
      const contratoSelect = document.getElementById("desvincular_contrato_id");
      const clienteSelect = document.getElementById("clientes_vinculados");
      const modal = document.getElementById('desvincularContractModal');
    
      modal.addEventListener('show.bs.modal', function () {
        // Carrega contratos
        fetch("/list/contratos_ativos")
          .then(response => response.json())
          .then(data => {
            contratoSelect.innerHTML = "<option disabled selected value=''>Selecione um contrato</option>";
            data.forEach(contrato => {
              const option = document.createElement("option");
              option.value = contrato.id;
              option.text = `${contrato.numero} - ${contrato.razao_social}`;
              contratoSelect.appendChild(option);
            });
          });
      });
    
      contratoSelect.addEventListener("change", function () {
        const contratoId = this.value;
    
        if (!contratoId) return;
    
        fetch(`/get/clientes_por_contrato/${contratoId}`)
          .then(response => response.json())
          .then(data => {
            clienteSelect.innerHTML = "";
            if (data.length === 0) {
              const option = document.createElement("option");
              option.disabled = true;
              option.text = "Nenhum cliente vinculado.";
              clienteSelect.appendChild(option);
            } else {
              data.forEach(cliente => {
                const option = document.createElement("option");
                option.value = cliente.id;
                option.text = `${cliente.codigo} - ${cliente.razao_social}`;
                clienteSelect.appendChild(option);
              });
            }
          });
      });
    });