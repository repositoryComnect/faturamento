document.addEventListener("DOMContentLoaded", function () {
      const produtoSelect = document.getElementById("vincular_produto_id");
      const planoSelect = document.getElementById("plano_vincular_produto");
      const modal = document.getElementById('vincularProdutoPlanoModal');
  
      modal.addEventListener('show.bs.modal', function () {
        fetch("/planos_ativos")
            .then(response => response.json())
            .then(data => {

                console.log("Planos recebidos:", data);

                const planoSelect = document.getElementById("plano_vincular_produto");

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