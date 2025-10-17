document.addEventListener("DOMContentLoaded", function () {
      const modal = document.getElementById('desvincularInstalacaoModal');
      const clienteSelect = document.getElementById("desvincular_cliente_id");
      const instalacaoSelect = document.getElementById("instalacoes_vinculadas");
  
      modal.addEventListener('show.bs.modal', function () {
        // Carrega clientes com instalações
        fetch("/get/clientes_com_instalacoes")
          .then(response => response.json())
          .then(clientes => {
            clienteSelect.innerHTML = "<option disabled selected value=''>Selecione um cliente</option>";
            clientes.forEach(cliente => {
              const option = document.createElement("option");
              option.value = cliente.id;
              option.text = `${cliente.sequencia} - ${cliente.razao_social}`;
              clienteSelect.appendChild(option);
            });
          });
  
        instalacaoSelect.innerHTML = "<option disabled>Selecione um cliente para ver as instalações</option>";
      });
  
      // Quando um cliente é selecionado, carregar as instalações dele
      clienteSelect.addEventListener("change", function () {
        const clienteId = this.value;
        fetch(`/get/instalacoes_por_cliente/${clienteId}`)
          .then(response => response.json())
          .then(data => {
            instalacaoSelect.innerHTML = "";
  
            if (data.length === 0) {
              const option = document.createElement("option");
              option.disabled = true;
              option.text = "Nenhuma instalação vinculada.";
              instalacaoSelect.appendChild(option);
            } else {
              data.forEach(inst => {
                const option = document.createElement("option");
                option.value = inst.id;
                option.text = `${inst.codigo_instalacao} - ${inst.endereco}`;
                instalacaoSelect.appendChild(option);
              });
            }
          });
      });
    });