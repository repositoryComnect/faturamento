document.addEventListener("DOMContentLoaded", function () {
      const contratoSelect = document.getElementById("desvincular_contrato_id_planos");
      const planoSelect = document.getElementById("planos_vinculados");
      const modal = document.getElementById('desvincularPlanoContractModal');
  
      // Carrega contratos ao abrir o modal
      modal.addEventListener('show.bs.modal', function () {
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
          })
          .catch(error => {
            console.error("Erro ao carregar contratos:", error);
          });
      });
  
      // Carrega planos vinculados ao selecionar contrato
      contratoSelect.addEventListener("change", function () {
        const contratoId = this.value;
  
        if (!contratoId) return;
  
        fetch(`/get/planos_por_contrato/${contratoId}`)
          .then(response => response.json())
          .then(data => {
            planoSelect.innerHTML = "";
            if (data.length === 0) {
              const option = document.createElement("option");
              option.disabled = true;
              option.text = "Nenhum plano vinculado.";
              planoSelect.appendChild(option);
            } else {
              data.forEach(plano => {
                const option = document.createElement("option");
                option.value = plano.id;
                option.text = `${plano.nome} - R$ ${plano.valor}`;
                planoSelect.appendChild(option);
              });
            }
          })
          .catch(error => {
            console.error("Erro ao carregar planos vinculados:", error);
          });
      });
    });