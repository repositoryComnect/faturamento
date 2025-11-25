document.addEventListener("DOMContentLoaded", async () => {
    try {
        const responseBar = await fetch('/contratosChart');
        const dataBar = await responseBar.json();

        const ctxBar = document.getElementById('contratosChart').getContext('2d');

        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: dataBar.map(item => item.month),
                datasets: [
                    {
                        label: 'Cadastrados',
                        data: dataBar.map(item => item.ativo),
                        backgroundColor: '#4CAF50'
                    },
                    {
                        label: 'Suspensos',
                        data: dataBar.map(item => item.suspenso),
                        backgroundColor: '#FFC107'
                    },
                    {
                        label: 'Cancelados',
                        data: dataBar.map(item => item.cancelado),
                        backgroundColor: '#F44336'
                    },
                    {
                        label: 'Arquivado',
                        data: dataBar.map(item => item.arquivado),
                        backgroundColor: '#F47B20'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.dataset.label}: ${context.parsed.y}`
                        }
                    },
                    legend: { position: 'top' }
                },
                scales: {
                    x: { stacked: false },
                    y: { beginAtZero: true, stacked: false }
                }
            }
        });
    } catch (error) {
        console.error('Erro ao carregar dados do gráfico de barras:', error);
        document.getElementById('contratosChart').outerHTML =
            '<div class="alert alert-danger">Erro ao carregar dados do gráfico de barras</div>';
    }


    // ====== Gráfico de Pizza ======
    try {
        const responsePie = await fetch('/statusChart');
        const dataPie = await responsePie.json();

        const STATUS_COLORS = {
            'Ativos': '#2196F3',
            'Suspensos': '#FFC107',
            'Cancelado': '#F44336',
            'Arquivado': '#F47B20'
        };

        const ctxPie = document.getElementById('statusChart').getContext('2d');
        new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: dataPie.map(item => item.status),
                datasets: [{
                    data: dataPie.map(item => item.count),
                    backgroundColor: dataPie.map(item => STATUS_COLORS[item.status] || '#999'),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const total = context.chart._metasets[0].total;
                                const value = context.parsed;
                                const percent = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value} (${percent}%)`;
                            }
                        }
                    },
                    legend: { position: 'bottom' }
                }
            }
        });
    } catch (error) {
        console.error('Erro ao carregar dados do gráfico de pizza:', error);
        document.getElementById('statusChart').outerHTML =
            '<div class="alert alert-danger">Erro ao carregar dados do gráfico de status</div>';
    }

});
