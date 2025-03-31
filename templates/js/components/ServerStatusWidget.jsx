const ServerStatusWidget = ({ title }) => {
    const [serverData, setServerData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const fetchServerStatus = async () => {
            try {
                const response = await fetch('/api/server-status');
                if (!response.ok) {
                    throw new Error('Failed to fetch server status');
                }
                const data = await response.json();
                setServerData(data);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchServerStatus();
    }, []);

    const renderProgressBar = (current, total, label, color) => {
        // Calculate percentage, but handle edge cases
        const percentage = total > 0 ? Math.min(Math.round((current / total) * 100), 100) : 0;

        return (
            <div className="mb-4">
                <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{label}</span>
                    <span className="text-sm font-medium text-gray-700">{percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                        className={`h-2.5 rounded-full ${color}`}
                        style={{ width: `${percentage}%` }}>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">{title}</h3>

            {loading && (
                <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            )}

            {error && (
                <div className="text-center text-red-500 p-4">
                    Error loading server status: {error}
                </div>
            )}

            {serverData && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Version information */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-3">Versions</h4>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Python:</span>
                                <span className="font-medium">{serverData.python_version}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Flask:</span>
                                <span className="font-medium">{serverData.flask_version}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">MySQL:</span>
                                <span className="font-medium">{serverData.mysql_version}</span>
                            </div>
                        </div>
                    </div>

                    {/* Resource usage */}
                    <div className="bg-gray-50 p-4 rounded-lg col-span-1 lg:col-span-2">
                        <h4 className="font-medium text-gray-700 mb-3">Resource Usage</h4>

                        {/* CPU Usage */}
                        {renderProgressBar(
                            serverData.cpu_usage,
                            100,
                            `CPU Usage: ${serverData.cpu_usage}%`,
                            'bg-blue-600'
                        )}

                        {/* System RAM Usage */}
                        {renderProgressBar(
                            serverData.ram_used,
                            serverData.ram_total,
                            `System RAM: ${serverData.ram_used} GB / ${serverData.ram_total} GB`,
                            'bg-green-600'
                        )}

                        {/* Process RAM Usage as percentage of allocated memory */}
                        {renderProgressBar(
                            serverData.process_ram_used,
                            serverData.process_ram_allocated,
                            `App Memory Usage: ${serverData.process_ram_used} GB / ${serverData.process_ram_allocated} GB`,
                            'bg-amber-500'
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};