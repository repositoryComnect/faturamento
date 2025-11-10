document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('listarClientesModal');
    const tbody = document.querySelector('#clientesModalTable tbody');
    const pagination = document.getElementById('clientesModalPagination');
    const inputSequencia = document.getElementById('sequencia'); // campo de sequência do cliente

    const perPage = 10; // clientes por página
    let clientes = [];
    let currentPage = 1;
    let totalPages = 1;

    // Renderiza a tabela de clientes
    function renderTable() {
        tbody.innerHTML = '';
        if (!clientes.length) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Nenhum cliente encontrado</td></tr>`;
            return;
        }

        const start = (currentPage - 1) * perPage;
        const end = start + perPage;
        const pageClients = clientes.slice(start, end);

        pageClients.forEach(cliente => {
            const tr = document.createElement('tr');

            // Coluna: Código (sequência)
            const tdSeq = document.createElement('td');
            tdSeq.innerText = cliente.codigo || '';
            tr.appendChild(tdSeq);

            // Coluna: Razão Social
            const tdRazao = document.createElement('td');
            tdRazao.innerText = cliente.razao_social || '';
            tr.appendChild(tdRazao);

            // Coluna: CNPJ/CPF
            const tdCnpj = document.createElement('td');
            tdCnpj.innerText = cliente.cnpj_cpf || '';
            tr.appendChild(tdCnpj);

            // Coluna: Ação
            const tdAcao = document.createElement('td');
            const btn = document.createElement('button');
            btn.classList.add('btn', 'btn-sm', 'btn-secondary');
            btn.innerText = 'Selecionar';
            btn.addEventListener('click', () => {
                // Preenche o campo e busca os dados do cliente pela SEQUÊNCIA
                inputSequencia.value = cliente.codigo;
                buscarDadosCliente(cliente.codigo);
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
            });
            tdAcao.appendChild(btn);
            tr.appendChild(tdAcao);

            tbody.appendChild(tr);
        });

        renderPagination();
    }

    // Renderiza a paginação
    function renderPagination() {
        pagination.innerHTML = '';
        totalPages = Math.ceil(clientes.length / perPage);

        const createPageItem = (page, text = null, disabled = false, active = false) => {
            const li = document.createElement('li');
            li.classList.add('page-item');
            if (disabled) li.classList.add('disabled');
            if (active) li.classList.add('active');

            const a = document.createElement('a');
            a.classList.add('page-link');
            a.href = '#';
            a.innerText = text || page;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                if (!disabled && currentPage !== page) {
                    currentPage = page;
                    renderTable();
                }
            });

            li.appendChild(a);
            return li;
        };

        pagination.appendChild(createPageItem(currentPage - 1, 'Anterior', currentPage === 1));

        for (let i = 1; i <= totalPages; i++) {
            pagination.appendChild(createPageItem(i, null, false, i === currentPage));
        }

        pagination.appendChild(createPageItem(currentPage + 1, 'Próximo', currentPage === totalPages));
    }

    // Quando o modal for aberto
    modal.addEventListener('show.bs.modal', function () {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center">Carregando clientes...</td></tr>`;

        fetch("/get/list/clientes")
            .then(response => {
                if (!response.ok) throw new Error("Erro ao buscar clientes");
                return response.json();
            })
            .then(data => {
                clientes = data;
                currentPage = 1;
                renderTable();
            })
            .catch(error => {
                console.error("Erro ao carregar clientes:", error);
                tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Erro ao carregar clientes</td></tr>`;
            });
    });
});
