document.addEventListener('DOMContentLoaded', function () {
    const produtoModal = document.getElementById('createProdutoModal');
    produtoModal.addEventListener('show.bs.modal', function () {
        fetch('/proximo_codigo_produto')
            .then(response => response.json())
            .then(data => {
                if (data.proximo_codigo_produto) {
                    document.getElementById('codigo_produto').value = data.proximo_codigo_produto;
                } else {
                    console.warn("Código não retornado pela API.");
                }
            })
            .catch(error => {
                console.error("Erro ao buscar código do produto:", error);
            });
    });
});