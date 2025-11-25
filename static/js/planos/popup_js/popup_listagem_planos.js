document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('listarPlanosModal');
    const tbody = document.querySelector('#planosModalTable tbody');
    const pagination = document.getElementById('planosModalPagination');

    // IDs alvo que você está usando no formulário principal — ajuste se seus ids forem outros
    const TARGETS = {
        idField: document.getElementById('plano_id'),            // opcional
        codigoField: document.getElementById('codigo_plano'),   // seu campo de código
        nomeField: document.getElementById('nome_plano'),
        valorField: document.getElementById('valor_plano'),
        qtdField: document.getElementById('qtd_produto_plano'),
        produtoField: document.getElementById('produto_id_plano'),
        contratoField: document.getElementById('contrato_id_plano'),
        cadastradoField: document.getElementById('cadastramento_plano')
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
                    <button type="button" class="btn btn-sm btn-secondary selecionar-plano" data-codigo="${escapeHtml(plano.codigo)}" data-id="${plano.id}">
                        Selecionar
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        }

        renderPagination();

        // Delegação para os botões "Selecionar"
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

        // Preencher imediatamente campos visuais mínimos (se existirem)
        if (TARGETS.codigoField) TARGETS.codigoField.value = codigo;
        if (TARGETS.idField && id) TARGETS.idField.value = id;

        // Chamar a função que já faz a busca completa e preenche os campos.
        // Certifique-se de que buscarPlanoPorCodigo está definida globalmente (em outro .js carregado antes).
        if (typeof buscarPlanoPorCodigo === "function") {
            try {
                buscarPlanoPorCodigo(codigo);
            } catch (err) {
                console.error("Erro ao executar buscarPlanoPorCodigo:", err);
            }
        } else {
            console.warn("Função buscarPlanoPorCodigo não encontrada. Preenchendo campos com dados do modal como fallback.");

            // Preenchimento fallback com os dados já presentes no objeto planos
            const plano = planos.find(p => String(p.id) === String(id) || p.codigo === codigo);
            if (plano) {
                if (TARGETS.nomeField) TARGETS.nomeField.value = plano.nome ?? '';
                if (TARGETS.valorField) TARGETS.valorField.value = (plano.valor != null) ? plano.valor : '';
                if (TARGETS.qtdField) TARGETS.qtdField.value = plano.qtd_produto ?? '';
                if (TARGETS.produtoField) TARGETS.produtoField.value = plano.produto ?? '';
                if (TARGETS.contratoField) TARGETS.contratoField.value = plano.contrato_id ?? '';
                if (TARGETS.cadastradoField) TARGETS.cadastradoField.value = plano.cadastramento ?? '';
            }
        }

        // Fechar modal de forma compatível com várias versões do bootstrap
        try {
            // método recomendado se disponível
            if (bootstrap && typeof bootstrap.Modal.getOrCreateInstance === 'function') {
                bootstrap.Modal.getOrCreateInstance(modal).hide();
            } else if (bootstrap && typeof bootstrap.Modal.getInstance === 'function') {
                const inst = bootstrap.Modal.getInstance(modal);
                if (inst) inst.hide();
                else new bootstrap.Modal(modal).hide();
            } else {
                // fallback: tentar disparar clique no botão fechar
                const btnClose = modal.querySelector('[data-bs-dismiss="modal"]');
                if (btnClose) btnClose.click();
            }
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

    // utilitário mínimo para evitar injeção de HTML nos dados da tabela
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
