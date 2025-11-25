function toggleCollapse(id) {
    const collapse = document.getElementById(id);
    const icon = collapse.previousElementSibling.querySelector('i');

    collapse.classList.toggle('show');

    if (collapse.classList.contains('show')) {
        icon.classList.remove('bi-chevron-up');
        icon.classList.add('bi-chevron-down');
    } else {
        icon.classList.remove('bi-chevron-down');
        icon.classList.add('bi-chevron-up');
    }
}

function confirmarExclusao(planoId) {
    if (confirm('Tem certeza que deseja excluir este plano?')) {
        window.location.href = '/planos/excluir/' + planoId;
    }
}


/* ============================
   CARREGA CONTRATOS
============================ */
document.addEventListener("DOMContentLoaded", function () {
    fetch("/contratos_ativos")
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById("contrato_id");
            select.innerHTML = '<option value="">Selecione um contrato</option>';
            const planoContratoId = "{{ plano.contrato_id or '' }}";

            data.forEach(contrato => {
                const option = document.createElement("option");
                option.value = contrato.id;
                option.text = `${contrato.numero} - ${contrato.razao_social}`;

                if (planoContratoId && planoContratoId == contrato.id.toString()) {
                    option.selected = true;
                }

                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar contratos:", error);
            const select = document.getElementById("contrato_id");
            select.innerHTML = '<option value="">Erro ao carregar contratos</option>';
        });
});


/* ============================
   CARREGA CLIENTES
============================ */
document.addEventListener("DOMContentLoaded", function () {
    fetch("/clientes_ativos_planos")
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById("cliente_id");
            select.innerHTML = '<option value="">Selecione um cliente</option>';

            const clienteSelecionadoId = "{{ plano.cliente_id or '' }}";

            data.forEach(cliente => {
                const option = document.createElement("option");
                option.value = cliente.id;
                option.textContent = `${cliente.sequencia} - ${cliente.razao_social}`;

                if (clienteSelecionadoId && clienteSelecionadoId == cliente.id.toString()) {
                    option.selected = true;
                }

                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar clientes:", error);
            const select = document.getElementById("cliente_id");
            select.innerHTML = '<option value="">Erro ao carregar clientes</option>';
        });
});


/* ============================
   BUSCA PRÓXIMO CÓDIGO DE PLANO
============================ */
function carregarCodigoPlano(modalEl) {
    const campo = modalEl.querySelector('#codigo_contrato_plano');
    if (!campo) return;

    fetch('/proximo_codigo_plano')
        .then(response => response.json())
        .then(data => {
            if (data.proximo_codigo) {
                campo.value = data.proximo_codigo;
            } else {
                console.warn("Código de plano não retornado pela API.");
            }
        })
        .catch(error => {
            console.error("Erro ao buscar código de plano:", error);
        });
}

// Se o campo existir na página normal
document.addEventListener("DOMContentLoaded", function () {
    const campoPagina = document.querySelector('#codigo_contrato_plano');
    if (campoPagina) {
        carregarCodigoPlano(document);
    }
});

// Quando o modal abrir (ID CORRIGIDO)
document.addEventListener('shown.bs.modal', function (event) {
    if (event.target.id === "criarPlanoModal") {
        carregarCodigoPlano(event.target);
    }
});


/* ============================
   CARREGA PRODUTOS
============================ */
document.addEventListener("DOMContentLoaded", function () {
    fetch("/planos/get_produtos", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById("produto_id");
            select.innerHTML = '<option value="">Selecione um produto</option>';

            const planoProdutoId = "{{ plano.produto_id if plano is defined else '' }}";

            data.forEach(produto => {
                const option = document.createElement("option");
                option.value = produto.id;
                option.text = `${produto.codigo} - ${produto.nome} - ${produto.preco_base} R$`;

                if (planoProdutoId && planoProdutoId == produto.id.toString()) {
                    option.selected = true;
                }

                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar produtos:", error);
            const select = document.getElementById("produto_id");
            select.innerHTML = '<option value="">Erro ao carregar produtos</option>';
        });
});


/* ============================
   REGRAS DE VALOR / QTD PRODUTO
============================ */
document.addEventListener("DOMContentLoaded", () => {
    const valorInput = document.getElementById("valor");
    const qtdProdutoInput = document.getElementById("qtd_produto");
    const produtoSelect = document.getElementById("produto_id");

    function atualizarEstadoQuantidade() {
        const valorInformado = valorInput.value.trim() !== "";
        const produtoVinculado = produtoSelect.value !== "";

        if (valorInformado) {
            qtdProdutoInput.disabled = true;
            return;
        }

        if (produtoVinculado) {
            qtdProdutoInput.disabled = false;
            return;
        }

        qtdProdutoInput.disabled = false;
    }

    valorInput.addEventListener("input", atualizarEstadoQuantidade);
    produtoSelect.addEventListener("change", atualizarEstadoQuantidade);

    // Ajuste ao abrir modal
    document.addEventListener('shown.bs.modal', atualizarEstadoQuantidade);
});
