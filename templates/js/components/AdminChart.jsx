const AdminChart = ({ title, chartType, endpoint, endpoints, days = 30, className = '' }) => {
    const [chartData, setChartData] = React.useState({});
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const chartRef = React.useRef(null);
    const chartInstance = React.useRef(null);

    // Veri çekme işlemi
    React.useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                if (chartType === 'combined' && Array.isArray(endpoints)) {
                    const results = await Promise.all(endpoints.map(async (config) => {
                        const url = `${config.url}?days=${days}`;
                        const response = await fetch(url);

                        if (!response.ok) {
                            throw new Error(`${config.url} için veri alınamadı.`);
                        }

                        return {
                            config,
                            data: await response.json()
                        };
                    }));

                    // Birleştirilmiş veri formatını hazırla
                    const datasets = [];
                    let labels = [];

                    results.forEach(result => {
                        const { data, config } = result;

                        // Tüm tarihleri topla
                        if (data && Array.isArray(data)) {
                            data.forEach(item => {
                                if (item.date && !labels.includes(item.date)) {
                                    labels.push(item.date);
                                }
                            });
                        }

                        datasets.push({
                            ...config,
                            data,
                        });
                    });

                    // Tarihleri sırala
                    labels.sort();

                    setChartData({ datasets, labels });
                } else {
                    // Tek endpoint için veri çekme
                    const response = await fetch(`${endpoint}?days=${days}`);

                    if (!response.ok) {
                        throw new Error('Veriler alınamadı.');
                    }

                    const data = await response.json();
                    setChartData(data);
                }
            } catch (err) {
                console.error('Veri çekme hatası:', err);
                setError(err.message || 'Veriler yüklenirken bir hata oluştu.');
            } finally {
                setLoading(false);
            }
        };

        fetchData();

        return () => {
            // Temizlik işlemi
            if (chartInstance.current) {
                chartInstance.current.destroy();
                chartInstance.current = null;
            }
        };
    }, [endpoint, endpoints, chartType, days]);

    // Grafik oluşturma/güncelleme
    React.useEffect(() => {
        if (loading || error || !chartRef.current || !chartData) return;

        // Önceki grafik instance'ını temizle
        if (chartInstance.current) {
            chartInstance.current.destroy();
            chartInstance.current = null;
        }

        // Stats için grafik oluşturmaya gerek yok
        if (chartType === 'stats') return;

        const ctx = chartRef.current.getContext('2d');

        // Grafik verilerini hazırla
        let chartConfig = {
            type: 'line',  // Varsayılan tip
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                }
            }
        };

        if (chartType === 'combined' && chartData.datasets) {
            // Birden çok veri seti için düzenleme
            const datasets = chartData.datasets.map(dataset => {
                // Dataset veri noktalarını oluşturma
                const dataPoints = [];

                // Tüm etiketler için veri noktası oluştur (tarihe göre)
                chartData.labels.forEach(label => {
                    const dataItem = dataset.data.find(item => item.date === label);
                    dataPoints.push(dataItem ? dataItem.count : 0);
                });

                return {
                    label: dataset.label,
                    data: dataPoints,
                    backgroundColor: dataset.backgroundColor,
                    borderColor: dataset.borderColor,
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.4,
                    // Fill özelliğini kontrol et
                    fill: dataset.fill === true
                };
            });

            chartConfig.data = {
                labels: chartData.labels.map(date => formatDate(date)),
                datasets
            };

            // Her veri seti için belirlenen tür varsa kullan
            if (chartData.datasets && chartData.datasets[0] && chartData.datasets[0].config && chartData.datasets[0].config.type) {
                chartConfig.type = chartData.datasets[0].config.type;
            }
        } else {
            // Tek veri seti için
            const labels = chartData.map ? chartData.map(item => formatDate(item.date)) : [];
            const data = chartData.map ? chartData.map(item => item.count) : [];

            chartConfig.data = {
                labels,
                datasets: [{
                    label: title,
                    data,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.4,
                    fill: true
                }]
            };
        }

        // Chart oluştur
        chartInstance.current = new Chart(ctx, chartConfig);
    }, [chartData, loading, error, chartType, title]);

    // Stat kartlarını render etme
    const renderStatsCards = () => {
        if (!chartData) return null;

        // İstatistik özellikleri için
        const statItems = [
            { key: 'new_users', label: 'Yeni Kullanıcı', icon: '👤', color: 'blue' },
            { key: 'total_submissions', label: 'Toplam Gönderim', icon: '📝', color: 'purple' },
            { key: 'correct_submissions', label: 'Doğru Cevap', icon: '✅', color: 'green' },
            { key: 'active_users', label: 'Aktif Kullanıcı', icon: '🔥', color: 'orange' },
            { key: 'accuracy_rate', label: 'Doğruluk Oranı', icon: '📊', color: 'yellow', suffix: '%' }
        ];

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {statItems.map((item, index) => (
                    <div key={index} className={`bg-${item.color}-50 p-4 rounded-lg border-l-4 border-${item.color}-500 flex items-center`}>
                        <div className="text-2xl mr-3">{item.icon}</div>
                        <div>
                            <div className="text-xl font-bold text-gray-800">
                                {chartData[item.key]}{item.suffix || ''}
                            </div>
                            <div className="text-sm text-gray-600">{item.label}</div>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    // Tarih formatı için yardımcı fonksiyon
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('tr-TR', {day: 'numeric', month: 'short'});
    };

    return (
        <div className={`bg-white p-6 rounded-xl shadow-sm ${className}`}>
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
                {chartType !== 'stats' && (
                    <div className="text-sm text-gray-500">Son {days} gün</div>
                )}
            </div>

            {loading && (
                <div className="flex justify-center items-center h-60">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <span className="ml-2">Veriler yükleniyor...</span>
                </div>
            )}

            {error && (
                <div className="h-60 flex flex-col justify-center items-center">
                    <div className="text-red-500 text-xl mb-2">⚠️</div>
                    <div className="text-red-500">{error}</div>
                </div>
            )}

            {!loading && !error && chartType === 'stats' && renderStatsCards()}

            {!loading && !error && chartType !== 'stats' && (
                <div className="h-80 mt-4">
                    <canvas ref={chartRef}></canvas>
                </div>
            )}
        </div>
    );
};