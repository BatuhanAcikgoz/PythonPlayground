// import React from 'react'; // Eğer global React tanımına güveniyorsanız bu yorum kalabilir, aksi halde açın.
// Chart.js'i HTML dosyanızdan global olarak yüklediğinizi varsayıyorum.
// Eğer ThemeContext'i kullanıyorsanız, onu da import etmeniz gerekebilir:
// import { useTheme } from './ThemeContext'; // Veya ThemeContext'in bulunduğu doğru yol

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

        // Dark mode'a göre Chart'ın kullanılmayan kısmının arka plan rengini belirle
        const unusedColor = document.documentElement.classList.contains('dark')
            ? 'rgba(75, 85, 99, 0.9)' // Dark mode'da biraz daha koyu gri (gray-600 gibi)
            : 'rgba(241, 245, 249, 0.9)'; // Light mode'da mevcut slate-100 gibi

        if (charts.current[label]) {
            charts.current[label].data.datasets[0].data = [percentage, 100 - percentage];
            charts.current[label].data.datasets[0].backgroundColor[0] = color;
            charts.current[label].data.datasets[0].backgroundColor[1] = unusedColor; // Renk güncellemesi
            charts.current[label].update('none');
            return charts.current[label];
        }

        charts.current[label] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percentage, 100 - percentage],
                    backgroundColor: [color, unusedColor], // Başlangıçta da dynamic renk kullan
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
        // Bu renkler dark mode'da da genellikle iyi görünür, değiştirmeye gerek yok
        if (value < 60) return 'rgba(59, 130, 246, 0.9)'; // mavi (blue-500)
        if (value < 80) return 'rgba(99, 102, 241, 0.9)'; // indigo (indigo-500)
        return 'rgba(79, 70, 229, 0.9)'; // mor (violet-500)
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
        // Ana konteyner: bg-white -> dark:bg-gray-800, shadow-md -> dark:shadow-md (veya shadow-xl)
        <div className="bg-white rounded-xl shadow-md p-6 dark:bg-gray-800 dark:shadow-xl">
            <div className="flex justify-between items-center mb-6">
                {/* Başlık: text-gray-800 -> dark:text-white, ikon: text-blue-600 -> dark:text-blue-400 */}
                <h3 className="text-xl font-medium text-gray-800 flex items-center dark:text-white">
                    <svg className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path>
                    </svg>
                    {title || "Sunucu Durumu"}
                </h3>
                {lastUpdated && (
                    <div className="text-sm text-blue-600 py-1 px-3 bg-blue-50 rounded-full flex items-center dark:text-blue-400 dark:bg-blue-900">
                        <svg className="w-4 h-4 mr-1 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        {formatTime(lastUpdated)}
                    </div>
                )}
            </div>

            {loading && !serverData && (
                <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 dark:border-blue-400"></div>
                </div>
            )}

            {error && (
                <div className="text-center text-red-500 p-4 rounded-lg bg-red-50 dark:text-red-400 dark:bg-red-900">
                    <svg className="w-6 h-6 mx-auto mb-2 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    {error}
                </div>
            )}

            {serverData && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Sistem Bilgisi Kutusu: bg-slate-50 -> dark:bg-gray-700 */}
                    <div className="bg-slate-50 p-5 rounded-xl dark:bg-gray-700">
                        {/* Başlık: text-gray-700 -> dark:text-gray-300, ikon: text-blue-600 -> dark:text-blue-400 */}
                        <div className="text-sm font-medium text-gray-700 mb-4 flex items-center dark:text-gray-300">
                            <svg className="w-4 h-4 mr-1 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                            </svg>
                            Sistem Bilgisi
                        </div>
                        <div className="space-y-3">
                            {/* Bilgi Satırları: bg-white -> dark:bg-gray-600, shadow-sm -> dark:shadow-none */}
                            <div className="flex justify-between bg-white p-3 rounded-lg shadow-sm dark:bg-gray-600 dark:shadow-none">
                                {/* Metin: text-gray-500 -> dark:text-gray-400, font-medium text-gray-900 -> dark:text-white */}
                                <span className="text-gray-500 dark:text-gray-400">Python:</span>
                                <span className="font-medium text-gray-900 dark:text-white">{serverData.python_version}</span>
                            </div>
                            <div className="flex justify-between bg-white p-3 rounded-lg shadow-sm dark:bg-gray-600 dark:shadow-none">
                                <span className="text-gray-500 dark:text-gray-400">Flask:</span>
                                <span className="font-medium text-gray-900 dark:text-white">{serverData.flask_version}</span>
                            </div>
                            <div className="flex justify-between bg-white p-3 rounded-lg shadow-sm dark:bg-gray-600 dark:shadow-none">
                                <span className="text-gray-500 dark:text-gray-400">MySQL:</span>
                                <span className="font-medium text-gray-900 dark:text-white">{serverData.mysql_version}</span>
                            </div>
                        </div>
                    </div>

                    {/* CPU Usage Gauge Kutusu: bg-slate-50 -> dark:bg-gray-700 */}
                    <div className="bg-slate-50 p-5 rounded-xl dark:bg-gray-700">
                        {/* Başlık: text-gray-700 -> dark:text-gray-300 */}
                        <div className="text-sm font-medium text-gray-700 mb-3 text-center dark:text-gray-300">
                            CPU Kullanımı
                        </div>
                        <div className="h-36 relative">
                            <canvas ref={chartRefs.current.cpu}></canvas>
                            <div className="absolute inset-0 flex items-center justify-center">
                                {/* Yüzde metni: text-gray-800 -> dark:text-white */}
                                <span className="text-2xl font-bold text-gray-800 dark:text-white">{serverData.cpu_usage}%</span>
                            </div>
                        </div>
                    </div>

                    {/* RAM Usage Gauge Kutusu: bg-slate-50 -> dark:bg-gray-700 */}
                    <div className="bg-slate-50 p-5 rounded-xl dark:bg-gray-700">
                        {/* Başlık: text-gray-700 -> dark:text-gray-300 */}
                        <div className="text-sm font-medium text-gray-700 mb-3 text-center dark:text-gray-300">
                            RAM Kullanımı
                        </div>
                        <div className="h-36 relative">
                            <canvas ref={chartRefs.current.ram}></canvas>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                {/* GB metni: text-gray-800 -> dark:text-white */}
                                <span className="text-2xl font-bold text-gray-800 dark:text-white">{serverData.ram_used} GB</span>
                                {/* Toplam GB metni: text-gray-500 -> dark:text-gray-400 */}
                                <span className="text-xs text-gray-500 dark:text-gray-400">/ {serverData.ram_total} GB</span>
                            </div>
                        </div>
                        {/* Alt bilgi kutusu: bg-white -> dark:bg-gray-600, shadow-sm -> dark:shadow-none, text-blue-600 -> dark:text-blue-400 */}
                        <div className="text-center text-sm text-blue-600 mt-2 bg-white p-2 rounded-lg shadow-sm dark:bg-gray-600 dark:shadow-none dark:text-blue-400">
                            {((serverData.ram_used / serverData.ram_total) * 100).toFixed(1)}% kullanımda
                        </div>
                    </div>

                    {/* Process RAM Usage Gauge Kutusu: bg-slate-50 -> dark:bg-gray-700 */}
                    <div className="bg-slate-50 p-5 rounded-xl dark:bg-gray-700">
                        {/* Başlık: text-gray-700 -> dark:text-gray-300 */}
                        <div className="text-sm font-medium text-gray-700 mb-3 text-center dark:text-gray-300">
                            Uygulama RAM
                        </div>
                        <div className="h-36 relative">
                            <canvas ref={chartRefs.current.processRam}></canvas>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                {/* GB metni: text-gray-800 -> dark:text-white */}
                                <span className="text-2xl font-bold text-gray-800 dark:text-white">{serverData.process_ram_used.toFixed(2)} GB</span>
                                {/* Kullanımda metni: text-gray-500 -> dark:text-gray-400 */}
                                <span className="text-xs text-gray-500 dark:text-gray-400">kullanımda</span>
                            </div>
                        </div>
                        {/* Alt bilgi kutusu: bg-white -> dark:bg-gray-600, shadow-sm -> dark:shadow-none, text-blue-600 -> dark:text-blue-400 */}
                        <div className="text-center text-sm text-blue-600 mt-2 bg-white p-2 rounded-lg shadow-sm dark:bg-gray-600 dark:shadow-none dark:text-blue-400">
                            Toplam: {serverData.process_ram_allocated.toFixed(2)} GB
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Bileşeni global olarak kullanılabilir hale getirin
window.ServerStatusWidget = ServerStatusWidget;