const RecentSubmissions = ({ title }) => {
    const [submissions, setSubmissions] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const fetchRecentSubmissions = async () => {
            try {
                const response = await fetch('/api/last-submissions');
                if (!response.ok) {
                    throw new Error('API yanıtı başarısız oldu');
                }
                const data = await response.json();
                setSubmissions(data);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchRecentSubmissions();
    }, []);

    return (
        <div className="bg-white rounded-lg shadow-md p-6 h-full">
            <h3 className="text-xl font-bold mb-4">{title || "Son Gönderimler"}</h3>

            {loading && (
                <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            )}

            {error && (
                <div className="text-center text-red-500 p-4">
                    Hata: {error}
                </div>
            )}

            {!loading && !error && submissions.length === 0 && (
                <div className="text-center text-gray-500 p-4">
                    Gönderim bulunamadı.
                </div>
            )}

            {!loading && !error && submissions.length > 0 && (
                <div className="overflow-y-auto max-h-80">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Kullanıcı
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Soru
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Sonuç
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Süre (ms)
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Tarih
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {submissions.map((submission) => (
                                <tr key={submission.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                            <a href={`/admin/user/${submission.user_id}`} className="hover:text-blue-600">
                                                {submission.username}
                                            </a>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                            <a href={`/admin/question/${submission.question_id}`} className="hover:text-blue-600">
                                                {submission.question_title}
                                            </a>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm">
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${submission.is_correct ? 
                                                'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {submission.is_correct ? 'Başarılı' : 'Başarısız'}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                            {submission.execution_time.toFixed(2)}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500">
                                            {submission.created_at}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};