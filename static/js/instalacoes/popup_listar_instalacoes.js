document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('listarInstalacoesModal');
    const tbody = document.querySelector('#instalacoesModalTable tbody');
    const pagination = document.getElementById('instalacoesModalPagination');
    const inputInstalacao = document.getElementById('codigo_instalacao');

    const perPage = 10; // instalações por página
    let instalacoes = [];
    let currentPage = 1;
    let totalPages = 1;

    function renderTable() {
        tbody.innerHTML = '';

        if (!instalacoes.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-muted">
                        Nenhuma instalação ativa encontrada
                    </td>
                </tr>`;
            return;
        }

        const start = (currentPage - 1) * perPage;
        const end = start + perPage;
        const pageItems = instalacoes.slice(start, end);

        pageItems.forEach(inst => {
            const tr = document.createElement('tr');
            tr.classList.add('text-center');

            const tdCodigo = document.createElement('td');
            tdCodigo.innerText = inst.codigo_instalacao;
            tr.appendChild(tdCodigo);

            const tdRazao = document.createElement('td');
            tdRazao.innerText = inst.razao_social || '-';
            tr.appendChild(tdRazao);

            const tdAcao = document.createElement('td');
            const btn = document.createElement('button');
            btn.classList.add('btn', 'btn-sm', 'btn-secondary');
            btn.innerText = 'Selecionar';

            btn.addEventListener('click', () => {
                inputInstalacao.value = inst.codigo_instalacao;
                buscarDadosInstalacao(inst.codigo_instalacao);

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
        totalPages = Math.ceil(instalacoes.length / perPage);

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

        // Anterior
        pagination.appendChild(
            createPageItem(currentPage - 1, 'Anterior', currentPage === 1)
        );

        // Páginas
        for (let i = 1; i <= totalPages; i++) {
            pagination.appendChild(
                createPageItem(i, null, false, i === currentPage)
            );
        }

        // Próximo
        pagination.appendChild(
            createPageItem(currentPage + 1, 'Próximo', currentPage === totalPages)
        );
    }

    modal.addEventListener('show.bs.modal', function () {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center">
                    Carregando instalações...
                </td>
            </tr>`;

        fetch("/get/instalacoes/vinculo")
            .then(response => response.json())
            .then(data => {
                if (!data.sucesso) {
                    throw new Error(data.erro || 'Erro ao carregar instalações');
                }

                instalacoes = data.instalacoes || [];
                currentPage = 1;
                renderTable();
            })
            .catch(error => {
                console.error("Erro ao carregar instalações:", error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center text-danger">
                            Erro ao carregar instalações
                        </td>
                    </tr>`;
            });
    });
});
