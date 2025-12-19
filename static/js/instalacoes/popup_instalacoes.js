// Script que me traz o próximo código disponível de instalação
document.addEventListener('DOMContentLoaded', function () {
        fetch('/proximo_codigo_instalacao')
            .then(response => response.json())
            .then(data => {
                const campoCodigo = document.getElementById('cod_instalacao');
                if (campoCodigo && data.proximo_codigo_instalacao) {
                    campoCodigo.value = data.proximo_codigo_instalacao;
                }
            })
            .catch(error => {
                console.error('Erro ao buscar próximo código de instalação:', error);
            });
    });


// Script que me retorna a data atual
document.getElementById('createInstalacaoModal')
    .addEventListener('shown.bs.modal', function () {

        const hoje = new Date();
        const dia = String(hoje.getDate()).padStart(2, '0');
        const mes = String(hoje.getMonth() + 1).padStart(2, '0');
        const ano = hoje.getFullYear();

        const dataFormatada = `${dia}/${mes}/${ano}`;

        const campo = document.getElementById('cadastramento_instalacao');
        if (campo && !campo.value) {
            campo.value = dataFormatada;
        }
});


// Script: carrega clientes
document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('cliente_selecionado');
    const numeroSerieInput = document.getElementById('company') || document.getElementById('razao_social');
    fetch('/get/list/clientes')
        .then(response => response.json())
        .then(data => {
            select.innerHTML = '<option value="">Vincule um cliente</option>';
            data.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;  
                option.textContent = cliente.razao_social;
                option.setAttribute('data-nome', cliente.razao_social);  
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar clientes:', error);
            select.innerHTML = '<option value="">Erro ao carregar clientes</option>';
        });

    select.addEventListener('change', function () {
        const nome = select.options[select.selectedIndex].getAttribute('data-nome');
        numeroSerieInput.value = nome || '';
    });
});



// Script: carrega clientes
document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('cliente_selecionado_instalacao');
    const numeroSerieInput = document.getElementById('company') || document.getElementById('razao_social');
    fetch('/get/list/clientes')
        .then(response => response.json())
        .then(data => {
            select.innerHTML = '<option value="">Vincule um cliente</option>';
            data.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;  
                option.textContent = cliente.razao_social;
                option.setAttribute('data-nome', cliente.razao_social);  
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar clientes:', error);
            select.innerHTML = '<option value="">Erro ao carregar clientes</option>';
        });

    select.addEventListener('change', function () {
        const nome = select.options[select.selectedIndex].getAttribute('data-nome');
        numeroSerieInput.value = nome || '';
    });
});



// Script: carrega clientes
document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('cliente_selecionado_instalacao_vinculo');
    const numeroSerieInput = document.getElementById('company') || document.getElementById('razao_social');
    fetch('/get/list/clientes')
        .then(response => response.json())
        .then(data => {
            select.innerHTML = '<option value="">Vincule um cliente</option>';
            data.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;  
                option.textContent = `${cliente.codigo} - ${cliente.razao_social}`;
                option.setAttribute('data-nome', cliente.razao_social);  
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar clientes:', error);
            select.innerHTML = '<option value="">Erro ao carregar clientes</option>';
        });

    select.addEventListener('change', function () {
        const nome = select.options[select.selectedIndex].getAttribute('data-nome');
        numeroSerieInput.value = nome || '';
    });
});


// Script que traz a lista de instalações para vínculo
document.addEventListener('DOMContentLoaded', function () {
    fetch('/get/instalacoes/vinculo')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('instalacao_id');
            select.innerHTML = '';

            if (data.sucesso) {
                data.instalacoes.forEach(inst => {
                    const option = document.createElement('option');
                    option.value = inst.id; 
                    option.textContent = `${inst.codigo_instalacao} - ${inst.razao_social}`;
                    select.appendChild(option);
                });
            }
        })
        .catch(err => console.error('Erro ao carregar instalações:', err));
});



// Script que traz os dados do popup de desvinculo 
document.addEventListener("DOMContentLoaded", function () {
    const clienteSelect = document.getElementById("desvincular_cliente_id");
    const instalacaoSelect = document.getElementById("instalacoes_vinculadas");
    const modal = document.getElementById("desvincularInstalacaoModal");

    modal.addEventListener("show.bs.modal", function () {
        fetch("/get/list/clientes")
            .then(response => response.json())
            .then(data => {
                clienteSelect.innerHTML =
                    "<option disabled selected value=''>Selecione um cliente</option>";

                data.forEach(cliente => {
                    const option = document.createElement("option");
                    option.value = cliente.id;
                    option.text = `${cliente.codigo} - ${cliente.razao_social}`;
                    clienteSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Erro ao carregar clientes:", error);
                clienteSelect.innerHTML =
                    "<option disabled>Erro ao carregar clientes</option>";
            });
    });

    clienteSelect.addEventListener("change", function () {
        const clienteId = this.value;

        instalacaoSelect.innerHTML = "";

        if (!clienteId) return;

        fetch(`/get/instalacoes/por-cliente/${clienteId}`)
            .then(response => response.json())
            .then(data => {
                instalacaoSelect.innerHTML = "";

                if (!data.sucesso || data.instalacoes.length === 0) {
                    const option = document.createElement("option");
                    option.disabled = true;
                    option.text = "Nenhuma instalação vinculada.";
                    instalacaoSelect.appendChild(option);
                } else {
                    data.instalacoes.forEach(instalacao => {
                        const option = document.createElement("option");
                        option.value = instalacao.id;
                        option.text =
                            `${instalacao.codigo_instalacao} - ${instalacao.razao_social}`;
                        instalacaoSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error("Erro ao carregar instalações vinculadas:", error);
                const option = document.createElement("option");
                option.disabled = true;
                option.text = "Erro ao carregar instalações.";
                instalacaoSelect.appendChild(option);
            });
    });
});
