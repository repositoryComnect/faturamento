document.addEventListener('DOMContentLoaded', () => {
    carregarOperadores();
});

function carregarOperadores() {
    fetch('/operadores/api/operadores')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('operadoresTableBody');
            const erroGlobal = document.getElementById('erroGlobal');

            tbody.innerHTML = '';
            erroGlobal.classList.add('d-none');

            if (!data.success || data.operadores.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center text-muted py-4">
                            Nenhum operador encontrado
                        </td>
                    </tr>`;
                return;
            }

            data.operadores.forEach(op => {
                tbody.insertAdjacentHTML('beforeend', `
                    <tr>
                        <td>${op.id}</td>
                        <td>${op.nome || '-'}</td>
                        <td>${op.sobrenome || '-'}</td>
                        <td>${op.email || '-'}</td>
                        <td>${op.username}</td>

                        <td>
                            <span class="badge ${op.is_active ? 'bg-success' : 'bg-danger'}">
                                ${op.is_active ? 'Ativo' : 'Inativo'}
                            </span>
                        </td>

                        <td>
                            <span class="badge ${op.is_admin ? 'bg-primary' : 'bg-secondary'}">
                                ${op.is_admin ? 'Admin' : 'Operador'}
                            </span>
                        </td>

                        <td>${op.created_at || '-'}</td>

                        <td>
                            <button class="btn btn-sm btn-warning"
                                data-bs-toggle="modal"
                                data-bs-target="#updateOperadoresModal"
                                data-op-id="${op.id}">
                                <i class="bi bi-pencil"></i>
                            </button>


                            <button class="btn btn-sm btn-danger"
                                    onclick="excluirOperador(${op.id})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `);
            });
        })
        .catch(err => {
            console.error(err);
            document.getElementById('operadoresTableBody').innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-danger py-4">
                        Erro ao carregar operadores
                    </td>
                </tr>`;
        });
}

function editarOperador(id) {
    alert('Editar operador ID: ' + id);
}

function excluirOperador(id) {
    if (!confirm('Deseja excluir este operador?')) return;

    fetch(`/operadores/operadores/delete/${id}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                carregarOperadores();
            } else {
                alert(data.error || 'Erro ao excluir');
            }
        })
        .catch(() => alert('Erro de comunicação com o servidor'));
}


// Insert operadores
document.getElementById('operadorForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch(this.action, {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(() => alert('Erro ao salvar operador'));
});

// Tras o próximo ID disponível
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('createOperadorModal');
    const campoId = document.getElementById('id_operador');

    if (!modal || !campoId) return;

    modal.addEventListener('show.bs.modal', function () {
        fetch('/operadores/operadores/proximo_id')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    campoId.value = data.proximo_id;
                } else {
                    console.error('Erro ao buscar próximo ID');
                }
            })
            .catch(error => {
                console.error('Erro na requisição:', error);
            });
    });
});
