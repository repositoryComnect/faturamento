// Função para carregar empresas do banco de dados
        async function carregarEmpresas() {
            try {
                const response = await fetch('/getEmpresa');
                
                if (!response.ok) {
                    throw new Error('Erro ao carregar empresas');
                }
                
                const empresas = await response.json();
                const selectEmpresa = document.getElementById('empresa');
                
                // Limpa o select
                selectEmpresa.innerHTML = '<option value="">Selecione uma empresa</option>';
                
                // Adiciona as empresas ao select
                empresas.forEach(empresa => {
                    const option = document.createElement('option');
                    option.value = empresa.id; // Usa o ID como valor
                    option.textContent = empresa.nome_fantasia; // Usa o nome fantasia como texto
                    selectEmpresa.appendChild(option);
                });
                
            } catch (error) {
                console.error('Erro:', error);
                const selectEmpresa = document.getElementById('empresa');
                selectEmpresa.innerHTML = '<option value="">Erro ao carregar empresas</option>';
            }
        }

        // Carrega as empresas quando a página carregar
        document.addEventListener('DOMContentLoaded', carregarEmpresas);