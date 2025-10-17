 document.addEventListener("DOMContentLoaded", function () {
      const clienteSelect = document.getElementById("plano_ids");
      const contratoSelect = document.getElementById("contrato_id");
      const modal = document.getElementById('vincularPlanoContractModal');
    
      modal.addEventListener('show.bs.modal', function () {
    
        // 1. Carrega contratos
        fetch("/contratos_ativos")
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
    
          fetch("/planos_ativos")
            .then(response => response.json())
            .then(data => {
                const planoSelect = document.getElementById("plano_ids"); 
                planoSelect.innerHTML = "";
                data.forEach(plano => {
                const option = document.createElement("option");
                option.value = plano.id;
                option.text = `${plano.nome} - R$ ${plano.valor}`; 
                planoSelect.appendChild(option);
            });
          })
          .catch(error => console.error("Erro ao carregar clientes:", error));
      });
    });