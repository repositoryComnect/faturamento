document.addEventListener("DOMContentLoaded", async () => {
    // ====== Gráfico de Barras ======
    try {
        const responseBar = await fetch('/contratosChart');
        const dataBar = await responseBar.json();

        const ctxBar = document.getElementById('contratosChart').getContext('2d');
        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: dataBar.map(item => item.month),
                datasets: [{
                    label: 'Cadastros',
                    data: dataBar.map(item => item.count),
                    backgroundColor: '#4CAF50',
                    borderRadius: 6,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // 🔑 permite o gráfico se adaptar ao espaço
                layout: {
                    padding: { top: 20, bottom: 10, left: 15, right: 15 }
                },
                plugins: {
                    title: {
                        display: true,
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.parsed.y} cadastros`
                        }
                    },
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { maxRotation: 45, minRotation: 45 },
                        grid: { display: false },
                        barPercentage: 0.6,      // 🔹 controla largura relativa das barras
                        categoryPercentage: 0.6   // 🔹 evita que fiquem muito finas ou largas
                    },
                    y: {
                        beginAtZero: true
                    }
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

        const ctxPie = document.getElementById('statusChart').getContext('2d');
        new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: dataPie.map(item => item.status),
                datasets: [{
                    data: dataPie.map(item => item.count),
                    backgroundColor: [
                        '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF'
                    ],
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
