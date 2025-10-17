document.addEventListener("DOMContentLoaded", function () {
      const produtoSelect = document.getElementById("produto_ids");
      const contratoSelect = document.getElementById("produto_contrato_id");
      const modal = document.getElementById('vincularProdutoContractModal');
  
      modal.addEventListener('show.bs.modal', function () {
        // Carrega contratos
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
  
        // Carrega produtos
        fetch("/produtos_ativos")
          .then(response => response.json())
          .then(data => {
            produtoSelect.innerHTML = "";
           data.forEach(produto => {
            const option = document.createElement("option");
            option.value = produto.id;
            option.text = `${produto.nome} - R$ ${produto.preco_base.toFixed(2)}`;
            produtoSelect.appendChild(option);
            });
          })
          .catch(error => console.error("Erro ao carregar produtos:", error));
      });
    });