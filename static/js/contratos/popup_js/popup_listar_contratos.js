document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('listarContratosModal');
    const tbody = document.querySelector('#contratosModalTable tbody');
    const pagination = document.getElementById('contratosModalPagination');
    const inputContrato = document.getElementById('numeroContrato');

    const perPage = 10; // contratos por página
    let contratos = [];
    let currentPage = 1;
    let totalPages = 1;

    function renderTable() {
        tbody.innerHTML = '';
        if (!contratos.length) {
            tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">Nenhum contrato ativo encontrado</td></tr>`;
            return;
        }

        const start = (currentPage - 1) * perPage;
        const end = start + perPage;
        const pageContracts = contratos.slice(start, end);

        pageContracts.forEach(contrato => {
            const tr = document.createElement('tr');

            const tdNumero = document.createElement('td');
            tdNumero.innerText = contrato.numero;
            tr.appendChild(tdNumero);

            const tdRazao = document.createElement('td');
            tdRazao.innerText = contrato.razao_social;
            tr.appendChild(tdRazao);

            const tdAcao = document.createElement('td');
            const btn = document.createElement('button');
            btn.classList.add('btn', 'btn-sm', 'btn-secondary');
            btn.innerText = 'Selecionar';
            btn.addEventListener('click', () => {
                inputContrato.value = contrato.numero;
                buscarDadosContrato(contrato.numero);
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
            });
            tdAcao.appendChild(btn);
            tr.appendChild(tdAcao);

            tbody.appendChild(tr);
        });

        renderPagination();
    }

    function renderPagination() {
        pagination.innerHTML = '';
        totalPages = Math.ceil(contratos.length / perPage);

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

        // Previous
        pagination.appendChild(createPageItem(currentPage - 1, 'Anterior', currentPage === 1));

        // Pages
        for (let i = 1; i <= totalPages; i++) {
            pagination.appendChild(createPageItem(i, null, false, i === currentPage));
        }

        // Next
        pagination.appendChild(createPageItem(currentPage + 1, 'Próximo', currentPage === totalPages));
    }

    modal.addEventListener('show.bs.modal', function () {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center">Carregando contratos...</td></tr>`;
        fetch("/list/contratos_ativos")
            .then(response => response.json())
            .then(data => {
                contratos = data;
                currentPage = 1;
                renderTable();
            })
            .catch(error => {
                tbody.innerHTML = `<tr><td colspan="3" class="text-center text-danger">Erro ao carregar contratos</td></tr>`;
                console.error("Erro ao carregar contratos:", error);
            });
    });
});
