let ethPriceChart, walletValueChart;
let ethTimeframe = '1h'; // Default timeframe for ETH chart
let walletTimeframe = '1h'; // Default timeframe for Wallet chart

function initCharts() {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(71, 85, 105, 0.1)';
    
    const ctxPrice = document.getElementById('ethPriceChart').getContext('2d');
    const ctxWallet = document.getElementById('walletValueChart').getContext('2d');

    const gradientEth = ctxPrice.createLinearGradient(0, 0, 0, 300);
    gradientEth.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    gradientEth.addColorStop(1, 'rgba(99, 102, 241, 0.02)');
    
    const gradientWallet = ctxWallet.createLinearGradient(0, 0, 0, 300);
    gradientWallet.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
    gradientWallet.addColorStop(1, 'rgba(16, 185, 129, 0.02)');

    ethPriceChart = new Chart(ctxPrice, {
        type: 'line',
        data: {
            datasets: [{
                label: 'ETH Price (GBP)',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: gradientEth,
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointBackgroundColor: '#6366f1',
                pointHoverBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointHoverBorderColor: '#fff',
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        tooltipFormat: 'dd MMM yyyy HH:mm:ss'
                    },
                    title: { display: false },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 0
                    }
                },
                y: {
                    title: { display: false },
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(71, 85, 105, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '£' + value;
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: { 
                    mode: 'index', 
                    intersect: false,
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(51, 65, 85, 0.3)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '£' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'index',
                intersect: false
            }
        }
    });

    walletValueChart = new Chart(ctxWallet, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Wallet Value (GBP)',
                data: [],
                borderColor: '#10b981',
                backgroundColor: gradientWallet,
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointBackgroundColor: '#10b981',
                pointHoverBackgroundColor: '#10b981',
                pointBorderColor: '#fff',
                pointHoverBorderColor: '#fff',
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        tooltipFormat: 'dd MMM yyyy HH:mm:ss'
                    },
                    title: { display: false },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 0
                    }
                },
                y: {
                    title: { display: false },
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(71, 85, 105, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '£' + value;
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: { 
                    mode: 'index', 
                    intersect: false,
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(51, 65, 85, 0.3)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '£' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

function updateEthPrice() {
    fetch('/latest-price/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('live-eth-price').innerText = 'N/A';
                document.getElementById('live-eth-timestamp').innerText = '-';
                return;
            }
            document.getElementById('live-eth-price').innerText = data.gbp_price.toFixed(2);
            document.getElementById('live-eth-timestamp').innerText = formatTimestamp(data.timestamp);
        })
        .catch(error => {
            console.error('Error fetching ETH price:', error);
            document.getElementById('live-eth-price').innerText = 'Error';
        });
}

function updateTrends() {
    fetch('/eth-trends/')
        .then(response => response.json())
        .then(data => {
            Trends('eth-hour-trend', data['1h']);
            Trends('eth-day-trend', data['24h']);
            Trends('eth-week-trend', data['7d']);
            Trends('eth-all-trend', data['all']);
        })
        .catch(error => {
            console.error('Error fetching ETH trends:', error);
            ['eth-hour-trend', 'eth-day-trend', 'eth-week-trend', 'eth-all-trend'].forEach(id => {
                document.getElementById(id).innerText = 'Error';
                document.getElementById(id).style.color = 'gray';
            });
        });

    fetch('/wallet-trends/')
        .then(response => response.json())
        .then(data => {
            Trends('wallet-hour-trend', data['1h']);
            Trends('wallet-day-trend', data['24h']);
            Trends('wallet-week-trend', data['7d']);
            Trends('wallet-all-trend', data['all']);
        })
        .catch(error => {
            console.error('Error fetching wallet trends:', error);
            ['wallet-hour-trend', 'wallet-day-trend', 'wallet-week-trend', 'wallet-all-trend'].forEach(id => {
                document.getElementById(id).innerText = 'Error';
                document.getElementById(id).style.color = 'gray';
            });
        });
}

function updateCharts() {
    // Update ETH Price Chart
    fetch(`/historical-data/?timeframe=${ethTimeframe}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching ETH historical data:', data.error);
                return;
            }
            ethPriceChart.data.datasets[0].data = data.eth_prices.map(item => ({
                x: new Date(item.timestamp),
                y: parseFloat(item.gbp_price) // Convert string to number
            }));
            // Adjust time unit based on timeframe
            ethPriceChart.options.scales.x.time.unit = ethTimeframe === '1h' ? 'minute' : ethTimeframe === '24h' ? 'hour' : 'day';
            ethPriceChart.update();
        })
        .catch(error => {
            console.error('Error fetching ETH historical data:', error);
        });

    // Update Wallet Value Chart
    fetch(`/historical-data/?timeframe=${walletTimeframe}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching wallet historical data:', data.error);
                return;
            }
            walletValueChart.data.datasets[0].data = data.wallet_values.map(item => ({
                x: new Date(item.timestamp),
                y: parseFloat(item.value) // Convert string to number
            }));
            walletValueChart.options.scales.x.time.unit = walletTimeframe === '1h' ? 'minute' : walletTimeframe === '24h' ? 'hour' : 'day';
            walletValueChart.update();
        })
        .catch(error => {
            console.error('Error fetching wallet historical data:', error);
        });
}

function Trends(id, data) {
    const el = document.getElementById(id);
    if (!data || data.percent === null || data.price === null) {
        el.innerText = 'Not enough data yet';
        el.style.color = 'gray';
        return;
    }

    const percent = data.percent;
    const price = data.price;
    const sign = percent >= 0 ? '+' : '';
    const color = percent >= 0 ? '#10b981' : '#ef4444';
    el.innerText = `${sign}${percent.toFixed(2)}% (${sign}£${Math.abs(price).toFixed(2)})`;
    el.style.color = color;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    });
}

// Handle timeframe selector clicks
document.getElementById('eth-timeframe-selector').addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        ethTimeframe = e.target.dataset.timeframe;
        document.querySelectorAll('#eth-timeframe-selector button').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        updateCharts(); // Update immediately
    }
});

document.getElementById('wallet-timeframe-selector').addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        walletTimeframe = e.target.dataset.timeframe;
        document.querySelectorAll('#wallet-timeframe-selector button').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        updateCharts(); // Update immediately
    }
});

// Initialize charts and perform initial updates
initCharts();
updateEthPrice();
updateTrends();
updateCharts();

// Periodic updates every 15 seconds
setInterval(updateEthPrice, 15000);
setInterval(updateTrends, 15000);
setInterval(updateCharts, 15000);