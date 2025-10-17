// Script: carrega clientes e preenche nome no campo 'numero_serie' -->

    document.addEventListener('DOMContentLoaded', function () {
        const select = document.getElementById('cliente_selecionado');
        const numeroSerieInput = document.getElementById('company') || document.getElementById('razao_social');
;

        fetch('/get/list/clientes')
            .then(response => response.json())
            .then(data => {
                select.innerHTML = '<option value="">Vincule um cliente</option>';
                data.forEach(cliente => {
                    const option = document.createElement('option');
                    option.value = cliente.id;  // será cliente_id no backend
                    option.textContent = cliente.razao_social;
                    option.setAttribute('data-nome', cliente.razao_social);  // usado para preencher número de série
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


// Script: define data atual no campo 'cadastramento' -->
    document.addEventListener('DOMContentLoaded', function () {
        const hoje = new Date();
        const dia = String(hoje.getDate()).padStart(2, '0');
        const mes = String(hoje.getMonth() + 1).padStart(2, '0');
        const ano = hoje.getFullYear();
        const dataFormatada = `${ano}-${mes}-${dia}`;  // formato compatível com MySQL

        const campo = document.getElementById('cadastramento', 'registry');
        if (campo && !campo.value) {
            campo.value = dataFormatada;
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        fetch('/proximo_codigo_instalacao')
            .then(response => response.json())
            .then(data => {
                const campoCodigo = document.getElementById('codigo_instalacao');
                if (campoCodigo && data.proximo_codigo_instalacao) {
                    campoCodigo.value = data.proximo_codigo_instalacao;
                }
            })
            .catch(error => {
                console.error('Erro ao buscar próximo código de instalação:', error);
            });
    });
    

// Search Instalações
function buscarInstalacoes() {
    const search = document.getElementById("search").value.trim();

    if (!search) {
        Swal.fire({
            icon: 'info',
            title: 'Busca vazia',
            text: 'Por favor, insira um termo para pesquisa.',
        });
        return;
    }

    fetch(`/get/instalacoes?search=${encodeURIComponent(search)}`)
        .then(response => response.json())
        .then(data => {
            if (!data.sucesso) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Nenhum resultado encontrado',
                    text: 'Verifique o código ou razão social.',
                });
                return;
            }

            const instalacao = data.instalacoes[0];  // Pegando a primeira instalação
            preencherCamposInstalacao(instalacao);
        })
        .catch(error => {
            console.error("Erro ao buscar instalações:", error);
            Swal.fire({
                icon: 'error',
                title: 'Erro no servidor',
                text: 'Não foi possível buscar a instalação.',
            });
        });
}

function preencherCamposInstalacao(inst) {
    // Preenche os campos principais
    document.getElementById("codigo_instalacao").value = inst.codigo_instalacao || "";
    document.getElementById("razao_social").value = inst.razao_social || "";
    document.getElementById("id_portal").value = inst.id_portal || "";
    document.getElementById("cadastramento").value = inst.cadastramento || "";
    document.getElementById("status").value = inst.status || "";

    // Endereço
    document.getElementById("cep").value = inst.cep || "";
    document.getElementById("endereco").value = inst.endereco || "";
    document.getElementById("bairro").value = inst.bairro || "";
    document.getElementById("cidade").value = inst.cidade || "";
    document.getElementById("uf").value = inst.uf || "";

    // Cliente vinculado
    const selectCliente = document.getElementById('cliente_selecionado');
    if (inst.cliente_id && selectCliente) {
        selectCliente.value = inst.cliente_id;
    }
}