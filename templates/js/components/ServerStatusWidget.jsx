const ServerStatusWidget = ({ title }) => {
    const [serverData, setServerData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    const [lastUpdated, setLastUpdated] = React.useState(null);
    const chartRefs = React.useRef({
        cpu: React.createRef(),
        ram: React.createRef(),
        processRam: React.createRef()
    });
    const charts = React.useRef({});

    // Sunucu durumunu çeken fonksiyon
    const fetchServerStatus = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/server-status');
            if (!response.ok) {
                throw new Error('Sunucu durumu alınamadı');
            }
            const data = await response.json();
            setServerData(data);
            setLastUpdated(new Date());
            updateCharts(data);
        } catch (err) {
            setError(err.message);
            console.error('Sunucu durumu güncellenirken hata:', err);
        } finally {
            setLoading(false);
        }
    };

    const createGaugeChart = (ctx, label, value, maxValue) => {
        const percentage = (value / maxValue) * 100;
        const color = getGaugeColor(percentage);

        if (charts.current[label]) {
            charts.current[label].data.datasets[0].data = [percentage, 100 - percentage];
            charts.current[label].data.datasets[0].backgroundColor[0] = color;
            charts.current[label].update('none');
            return charts.current[label];
        }

        charts.current[label] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percentage, 100 - percentage],
                    backgroundColor: [color, 'rgba(241, 245, 249, 0.9)'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '80%',
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                },
                animation: false
            }
        });

        return charts.current[label];
    };

    const getGaugeColor = (value) => {
        if (value < 60) return 'rgba(59, 130, 246, 0.9)'; // mavi
        if (value < 80) return 'rgba(99, 102, 241, 0.9)'; // indigo
        return 'rgba(79, 70, 229, 0.9)'; // mor
    };

    const updateCharts = (data) => {
        if (!data) return;

        // CPU Gauge
        if (chartRefs.current.cpu.current) {
            createGaugeChart(
                chartRefs.current.cpu.current,
                'cpu',
                data.cpu_usage,
                100
            );
        }

        // RAM Gauge
        if (chartRefs.current.ram.current) {
            createGaugeChart(
                chartRefs.current.ram.current,
                'ram',
                data.ram_used,
                data.ram_total
            );
        }

        // Process RAM Gauge
        if (chartRefs.current.processRam.current) {
            createGaugeChart(
                chartRefs.current.processRam.current,
                'processRam',
                data.process_ram_used,
                data.process_ram_allocated
            );
        }
    };

    // Tarih formatını düzenleyen fonksiyon
    const formatTime = (date) => {
        if (!date) return '';
        return date.toLocaleTimeString('tr-TR');
    };

    React.useEffect(() => {
        // İlk yüklemede veri çek
        fetchServerStatus();

        // 5 saniyede bir yenileme için interval
        const intervalId = setInterval(() => {
            fetchServerStatus();
        }, 5000);

        // Bileşen kaldırıldığında interval'i temizle
        return () => {
            clearInterval(intervalId);
            // Chart nesnelerini temizle
            Object.values(charts.current).forEach(chart => {
                if (chart) chart.destroy();
            });
        };
    }, []);

    return (
        <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-medium text-gray-800 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path>
                    </svg>
                    {title || "Sunucu Durumu"}
                </h3>
                {lastUpdated && (
                    <div className="text-sm text-blue-600 py-1 px-3 bg-blue-50 rounded-full flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        {formatTime(lastUpdated)}
                    </div>
                )}
            </div>

            {loading && !serverData && (
                <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600"></div>
                </div>
            )}

            {error && (
                <div className="text-center text-red-500 p-4 rounded-lg bg-red-50">
                    <svg className="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    {error}
                </div>
            )}

            {serverData && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-slate-50 p-5 rounded-xl">
                        <div className="text-sm font-medium text-gray-700 mb-4 flex items-center">
                            <svg className="w-4 h-4 mr-1 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                            </svg>
                            Sistem Bilgisi
                        </div>
                        <div className="space-y-3">
                            <div className="flex justify-between bg-white p-3 rounded-lg shadow-sm">
                                <span className="text-gray-500">Python:</span>
                                <span className="font-medium text-gray-900">{serverData.python_version}</span>
                            </div>
                            <div className="flex justify-between bg-white p-3 rounded-lg shadow-sm">
                                <span className="text-gray-500">Flask:</span>
                                <span className="font-medium text-gray-900">{serverData.flask_version}</span>
                            </div>
                            <div className="flex justify-between bg-white p-3 rounded-lg shadow-sm">
                                <span className="text-gray-500">MySQL:</span>
                                <span className="font-medium text-gray-900">{serverData.mysql_version}</span>
                            </div>
                        </div>
                    </div>

                    {/* CPU Usage Gauge */}
                    <div className="bg-slate-50 p-5 rounded-xl">
                        <div className="text-sm font-medium text-gray-700 mb-3 text-center">
                            CPU Kullanımı
                        </div>
                        <div className="h-36 relative">
                            <canvas ref={chartRefs.current.cpu}></canvas>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-2xl font-bold text-gray-800">{serverData.cpu_usage}%</span>
                            </div>
                        </div>
                    </div>

                    {/* RAM Usage Gauge */}
                    <div className="bg-slate-50 p-5 rounded-xl">
                        <div className="text-sm font-medium text-gray-700 mb-3 text-center">
                            RAM Kullanımı
                        </div>
                        <div className="h-36 relative">
                            <canvas ref={chartRefs.current.ram}></canvas>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                <span className="text-2xl font-bold text-gray-800">{serverData.ram_used} GB</span>
                                <span className="text-xs text-gray-500">/ {serverData.ram_total} GB</span>
                            </div>
                        </div>
                        <div className="text-center text-sm text-blue-600 mt-2 bg-white p-2 rounded-lg shadow-sm">
                            {((serverData.ram_used / serverData.ram_total) * 100).toFixed(1)}% kullanımda
                        </div>
                    </div>

                    {/* Process RAM Usage Gauge */}
                    <div className="bg-slate-50 p-5 rounded-xl">
                        <div className="text-sm font-medium text-gray-700 mb-3 text-center">
                            Uygulama RAM
                        </div>
                        <div className="h-36 relative">
                            <canvas ref={chartRefs.current.processRam}></canvas>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                <span className="text-2xl font-bold text-gray-800">{serverData.process_ram_used.toFixed(2)} GB</span>
                                <span className="text-xs text-gray-500">kullanımda</span>
                            </div>
                        </div>
                        <div className="text-center text-sm text-blue-600 mt-2 bg-white p-2 rounded-lg shadow-sm">
                            Toplam: {serverData.process_ram_allocated.toFixed(2)} GB
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};