document.addEventListener("DOMContentLoaded", function () {
      const contratoSelect = document.getElementById("desvincular_contrato_id_produtos");
      const produtoSelect = document.getElementById("produtos_vinculados");
      const modal = document.getElementById('desvincularProdutoContractModal');
  
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
          .catch(error => console.error("Erro ao carregar contratos:", error));
      });
  
      contratoSelect.addEventListener("change", function () {
        const contratoId = this.value;
  
        if (!contratoId) return;
  
        fetch(`/get/produtos_por_contrato/${contratoId}`)
          .then(response => response.json())
          .then(data => {
            produtoSelect.innerHTML = "";
            if (data.length === 0) {
              const option = document.createElement("option");
              option.disabled = true;
              option.text = "Nenhum produto vinculado.";
              produtoSelect.appendChild(option);
            } else {
              data.forEach(produto => {
                const option = document.createElement("option");
                option.value = produto.id;
                option.text = `${produto.nome} - R$ ${produto.valor}`;
                produtoSelect.appendChild(option);
              });
            }
          })
          .catch(error => console.error("Erro ao carregar produtos vinculados:", error));
      });
    });