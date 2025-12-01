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


//   CARREGA CLIENTES
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


//   BUSCA PRÓXIMO CÓDIGO DE PLANO

function carregarCodigoPlano(modalEl) {
    const campo = modalEl.querySelector('#codigo');
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
    const campoPagina = document.querySelector('#codigo');
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


//   CARREGA PRODUTOS

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


//   REGRAS DE VALOR / QTD PRODUTO

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


// Script buscar plano para edição
$(document).ready(function () {

  function buscarPlano(termo) {
    if (!termo) {
      Swal.fire({
        icon: 'warning',
        title: 'Campo vazio',
        text: 'Digite o nome ou código do plano.',
        toast: true,
        position: 'top-end',
        timer: 3000,
        showConfirmButton: false
      });
      return;
    }

    const $input = $('#fetch_plano');
    const $spinner = $('#loadingPlano');

    $input.prop('disabled', true);
    $spinner.removeClass('d-none');

    $.ajax({
      url: '/buscar_plano',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ termo: termo }),

      success: function (data) {
        console.log("Dados do plano:", data);

        if (data.success) {
          const plano = data.plano;

          const fieldMap = {
                "codigo": "#atualizar_codigo_plano",
                "nome": "#atualizar_nome_plano",
                "valor": "#atualizar_valor_plano",
                "id_produto_portal": "#atualizar_id_portal_plano",
                // "licenca_valor": "",
                "produto": "#atualizar_produto_plano",
                "qtd_produto": "#atualizar_quantidade_produto_plano",
                "desc_boleto_licenca": "#atualizar_descricao_boleto_plano",
                "aliquota_sp_licenca": "#atualizar_aliquota_plano",
                "cod_servico_sp_licenca": "#atualizar_codigo_servico_plano",
                "desc_nf_licenca": "#atualizar_descricao_nf_plano",
                //"valor_base_produto": plano.valor_base_produto,
                "status": "#atualizar_status_plano", 
                "cadastramento": "#atualizar_cadastramento_plano",
                "atualizacao": "#atualizar_atualizacao_plano"
          };

          for (const key in fieldMap) {
            if (plano[key] !== null && plano[key] !== undefined) {
              $(fieldMap[key]).val(plano[key]);
            }
          }

          Swal.fire({
            icon: 'success',
            title: 'Plano encontrado!',
            text: 'Os dados foram carregados com sucesso.',
            toast: true,
            position: 'top-end',
            timer: 2500,
            showConfirmButton: false
          });

        } else {
          Swal.fire({
            icon: 'warning',
            title: 'Plano não encontrado',
            text: 'Verifique o termo informado.',
            timer: 5000,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
          });
        }
      },

      error: function () {
        Swal.fire({
          icon: 'error',
          title: 'Erro ao buscar plano',
          text: 'Erro de comunicação com o servidor.',
          timer: 4000,
          showConfirmButton: false,
          toast: true,
          position: 'top-end'
        });
      },

      complete: function () {
        $input.prop('disabled', false);
        $spinner.addClass('d-none');
      }
    });
  }

  $('#btnBuscarPlano').on('click', function () {
    buscarPlano($('#fetch_plano').val());
  });

  $('#fetch_plano').on('keypress', function (e) {
    if (e.which === 13) {
      e.preventDefault();
      buscarPlano($(this).val());
    }
  });
});
