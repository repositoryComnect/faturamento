function proximoCodigoPlano() {
    let codigoAtual = document.getElementById('codigo_plano').value;
    if (!codigoAtual) return;

    $('#loadingCodigoPlano').removeClass('d-none');

    fetch(`/planos/proximo/${codigoAtual}`)
        .then(response => response.json())
        .then(data => {
            $('#loadingCodigoPlano').addClass('d-none');

            // Caso seja o último plano
            if (!data || Object.keys(data).length === 0) {
                Swal.fire({
                    icon: 'info',
                    title: 'Último plano',
                    text: 'Você já está no último plano cadastrado.',
                    toast: true,
                    position: 'top-end',
                    timer: 4000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
                return;
            }

            // Preenche os campos da tela
            document.getElementById('codigo_plano').value = data.codigo ?? "";
            document.getElementById('nome_plano').value = data.nome ?? "";
            document.getElementById('valor_plano').value = data.valor ?? "";
            document.getElementById('id_produto_plano').value = data.id_produto_portal ?? "";
            document.getElementById('contrato_id_plano').value = data.contrato_id ?? "";
            document.getElementById('produto_id_plano').value = data.produto ?? "";
            document.getElementById('qtd_produto_plano').value = data.qtd_produto ?? "";
            document.getElementById('desc_boleto_licenca_plano').value = data.desc_boleto ?? "";
            document.getElementById('aliquota_sp_licenca_plano').value = data.aliquota_sp ?? "";
            document.getElementById('cod_servico_sp_licenca_plano').value = data.cod_servico_sp ?? "";
            document.getElementById('desc_nf_licenca_plano').value = data.desc_nf ?? "";
            document.getElementById('cadastramento_plano').value = data.cadastramento ?? "";
            document.getElementById('atualizacao_plano').value = data.atualizacao ?? "";
        })
        .catch(err => {
            $('#loadingCodigoPlano').addClass('d-none');
            console.error("Erro ao buscar próximo plano:", err);

            Swal.fire({
                icon: 'error',
                title: 'Erro ao buscar próximo plano',
                text: 'Ocorreu um problema na busca.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
        });
}


// Buscar planos por código 

function buscarPlanoPorCodigo(codigo) {
    if (!codigo) return;

    $('#loadingCodigoPlano').removeClass('d-none');

    fetch(`/planos/buscar-por-codigo/${codigo}`)
        .then(response => response.json())
        .then(data => {
            $('#loadingCodigoPlano').addClass('d-none');

            if (data.error) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Plano não encontrado',
                    text: data.error
                });
                return;
            }

            // Preenche os campos
            document.getElementById('codigo_plano').value = data.codigo ?? "";
            document.getElementById('nome_plano').value = data.nome ?? "";
            document.getElementById('valor_plano').value = data.valor ?? "";
            document.getElementById('id_produto_plano').value = data.id_produto_portal ?? "";
            document.getElementById('contrato_id_plano').value = data.contrato_id ?? "";
            document.getElementById('produto_id_plano').value = data.produto_id ?? "";
            document.getElementById('qtd_produto_plano').value = data.qtd_produto ?? "";
            document.getElementById('desc_boleto_licenca_plano').value = data.desc_boleto ?? "";
            document.getElementById('aliquota_sp_licenca_plano').value = data.aliquota_sp ?? "";
            document.getElementById('cod_servico_sp_licenca_plano').value = data.cod_servico_sp ?? "";
            document.getElementById('desc_nf_licenca_plano').value = data.desc_nf ?? "";
            document.getElementById('cadastramento_plano').value = data.cadastramento ?? "";
        })
        .catch(err => {
            console.error("Erro ao buscar plano:", err);
            $('#loadingCodigoPlano').addClass('d-none');

            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: 'Ocorreu um erro ao buscar o plano.'
            });
        });
}
