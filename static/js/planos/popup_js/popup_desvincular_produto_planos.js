document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("desvincularProdutoPlanoModal");
    const planoSelect = document.getElementById("desvincular_plano_id_produtos");
    const produtosSelect = document.getElementById("produtos_vinculados");

    if (!modal || !planoSelect || !produtosSelect) {
        console.error("Elementos do modal não encontrados!");
        return;
    }

    // Função para carregar planos
    function carregarPlanos() {
        console.log("Carregando planos...");
        
        planoSelect.innerHTML = "<option value='' disabled selected>Selecione um plano</option>";
        produtosSelect.innerHTML = "";
        
        fetch("/planos_ativos/contratos")
            .then(response => response.json())
            .then(data => {
                if (!data || !data.length) {
                    planoSelect.innerHTML = "<option disabled>Nenhum plano encontrado</option>";
                    return;
                }
                
                data.sort((a, b) => a.nome.localeCompare(b.nome));
                
                data.forEach(plano => {
                    const option = document.createElement("option");
                    option.value = plano.id;
                    let texto = `${plano.codigo} - ${plano.nome}`;
                    
                    if (plano.produto) {
                        texto += ` [Produto: ${plano.produto}]`;
                    }
                    
                    option.textContent = texto;
                    planoSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Erro ao carregar planos:", error);
                planoSelect.innerHTML = "<option disabled>Erro ao carregar planos</option>";
            });
    }

    // Função para carregar produtos do plano
    function carregarProdutosDoPlano(planoId) {
        console.log(`Buscando produtos do plano: ${planoId}`);
        
        produtosSelect.innerHTML = "<option disabled>Carregando...</option>";
        
        fetch(`/get/planos/produto/${planoId}`)
            .then(response => response.json())
            .then(data => {
                produtosSelect.innerHTML = "";
                
                if (!data.success || !data.produtos || data.produtos.length === 0) {
                    const option = document.createElement("option");
                    option.disabled = true;
                    option.textContent = "Nenhum produto vinculado";
                    produtosSelect.appendChild(option);
                    return;
                }
                
                // Adicionar produtos
                data.produtos.forEach(produto => {
                    const option = document.createElement("option");
                    option.value = produto.id;
                    option.textContent = produto.codigo ? 
                        `${produto.codigo} - ${produto.nome}` : produto.nome;
                    option.selected = true;
                    produtosSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Erro ao carregar produtos:", error);
                produtosSelect.innerHTML = "<option disabled>Erro ao carregar produtos</option>";
            });
    }

    // Eventos
    modal.addEventListener("shown.bs.modal", carregarPlanos);
    
    planoSelect.addEventListener("change", function() {
        if (this.value) {
            carregarProdutosDoPlano(this.value);
        } else {
            produtosSelect.innerHTML = "";
        }
    });

});