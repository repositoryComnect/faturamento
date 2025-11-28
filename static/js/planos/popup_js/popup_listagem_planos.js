document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('listarPlanosModal');
    const tbody = document.querySelector('#planosModalTable tbody');
    const pagination = document.getElementById('planosModalPagination');

    // Mapeamento dos inputs do formulário
    const TARGETS = {
        idField: document.getElementById('plano_id'),
        codigoField: document.getElementById('codigo_plano'),
        nomeField: document.getElementById('nome_plano'),
        valorField: document.getElementById('valor_plano'),
        qtdField: document.getElementById('qtd_produto_plano'),
        produtoField: document.getElementById('produto_id_plano'),
        contratoField: document.getElementById('contrato_id_plano'),
        cadastradoField: document.getElementById('cadastramento_plano'),
        atualizacaoField: document.getElementById('atualizacao_plano'),
        statusField: document.getElementById('status_plano'),
    };

    const perPage = 10;
    let planos = [];
    let currentPage = 1;

    function renderTable() {
        tbody.innerHTML = '';
        if (!Array.isArray(planos) || planos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Nenhum plano encontrado</td></tr>`;
            return;
        }

        const start = (currentPage - 1) * perPage;
        const end = start + perPage;
        const pagePlans = planos.slice(start, end);

        for (const plano of pagePlans) {
            const tr = document.createElement('tr');

            tr.innerHTML = `
                <td class="text-center">${escapeHtml(plano.codigo ?? '')}</td>
                <td>${escapeHtml(plano.nome ?? '')}</td>
                <td class="text-center">${(typeof plano.valor === 'number') ? plano.valor.toFixed(2) : escapeHtml(plano.valor ?? '')}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-secondary selecionar-plano"
                        data-codigo="${escapeHtml(plano.codigo)}"
                        data-id="${plano.id}">
                        Selecionar
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        }

        renderPagination();

        tbody.querySelectorAll(".selecionar-plano").forEach(btn => {
            btn.removeEventListener('click', onSelecionarClick);
            btn.addEventListener('click', onSelecionarClick);
        });
    }

    function onSelecionarClick(e) {
        const btn = e.currentTarget;
        const codigo = btn.dataset.codigo;
        const id = btn.dataset.id;

        if (!codigo) {
            console.warn("Botão de selecionar plano sem código.");
            return;
        }

        // Preenche ID e código imediatamente
        if (TARGETS.codigoField) TARGETS.codigoField.value = codigo;
        if (TARGETS.idField && id) TARGETS.idField.value = id;

        // CHAMA A FUNÇÃO OFICIAL PARA OBTER DADOS COMPLETOS DO BACKEND
        if (typeof buscarPlanoPorCodigo === "function") {
            try {
                buscarPlanoPorCodigo(codigo);
            } catch (err) {
                console.error("Erro ao executar buscarPlanoPorCodigo:", err);
            }
        } else {
            console.warn("Função buscarPlanoPorCodigo não encontrada.");
        }

        // Fecha o modal
        fecharModalBootstrap();
    }


    function fecharModalBootstrap() {
        try {
            if (bootstrap && typeof bootstrap.Modal.getOrCreateInstance === 'function') {
                bootstrap.Modal.getOrCreateInstance(modal).hide();
                return;
            }
            if (bootstrap && typeof bootstrap.Modal.getInstance === 'function') {
                const inst = bootstrap.Modal.getInstance(modal);
                if (inst) inst.hide();
                else new bootstrap.Modal(modal).hide();
                return;
            }
            const btnClose = modal.querySelector('[data-bs-dismiss="modal"]');
            if (btnClose) btnClose.click();
        } catch (err) {
            console.warn("Não foi possível fechar modal via API do Bootstrap:", err);
        }
    }



    function renderPagination() {
        pagination.innerHTML = '';
        const totalPages = Math.max(1, Math.ceil(planos.length / perPage));

        const makeLi = (page, text = null, disabled = false, active = false) => {
            const li = document.createElement('li');
            li.className = 'page-item' + (disabled ? ' disabled' : '') + (active ? ' active' : '');
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.innerText = text || page;
            a.addEventListener('click', (ev) => {
                ev.preventDefault();
                if (!disabled && currentPage !== page) {
                    currentPage = page;
                    renderTable();
                }
            });
            li.appendChild(a);
            return li;
        };

        pagination.appendChild(makeLi(currentPage - 1, 'Anterior', currentPage === 1));
        for (let i = 1; i <= totalPages; i++) {
            pagination.appendChild(makeLi(i, null, false, i === currentPage));
        }
        pagination.appendChild(makeLi(currentPage + 1, 'Próximo', currentPage === totalPages));
    }



    modal && modal.addEventListener('show.bs.modal', function () {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center">Carregando planos...</td></tr>`;
        fetch("/listagem/planos/popup")
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                planos = Array.isArray(data) ? data : [];
                currentPage = 1;
                renderTable();
            })
            .catch(error => {
                tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Erro ao carregar planos</td></tr>`;
                console.error("Erro ao carregar planos:", error);
            });
    });


    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;');
    }
});
