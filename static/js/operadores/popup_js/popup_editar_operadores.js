document.addEventListener('DOMContentLoaded', function () {

    const modal = document.getElementById('updateOperadoresModal');

    modal.addEventListener('show.bs.modal', function (event) {

        const button = event.relatedTarget;
        if (!button) return;

        const operadorId = button.getAttribute('data-op-id');
        if (!operadorId) return;


        const inputFetch = modal.querySelector('#fetch_operador_editar');
        const inputId = modal.querySelector('#id_operador');

        inputFetch.value = operadorId;
        inputId.value = operadorId;

        const loading = modal.querySelector('#loadingInstalacao');
        loading.classList.remove('d-none');

        fetch(`/operadores/procurar/operador?id=${operadorId}`)
            .then(response => response.json())
            .then(data => {

                if (!data.success) {
                    alert(data.message);
                    return;
                }

                const operador = data.data;

                modal.querySelector('#nome_operador').value = operador.nome ?? '';
                modal.querySelector('#sobrenome_operador').value = operador.sobrenome ?? '';
                modal.querySelector('#email_operador').value = operador.email ?? '';
                modal.querySelector('#username_operador').value = operador.username ?? '';
                modal.querySelector('#perfil_operador').value = operador.perfil;

            })
            .catch(err => {
                console.error(err);
                alert('Erro ao buscar operador');
            })
            .finally(() => {
                loading.classList.add('d-none');
            });
    });

});