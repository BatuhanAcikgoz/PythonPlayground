// import React from 'react'; // Eğer global React tanımına güveniyorsanız bu yorum kalabilir, aksi halde açın.

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
        // Ana konteyner: bg-white -> dark:bg-gray-800, shadow-md -> dark:shadow-md
        <div className="bg-white rounded-lg shadow-md p-6 h-full dark:bg-gray-800 dark:shadow-md">
            <h3 className="text-xl font-bold mb-4 text-black dark:text-white">{title || "Son Gönderimler"}</h3>

            {loading && (
                <div className="flex justify-center items-center h-40 text-gray-700 dark:text-gray-300">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            )}

            {error && (
                <div className="text-center text-red-500 p-4 dark:text-red-400">
                    Hata: {error}
                </div>
            )}

            {!loading && !error && submissions.length === 0 && (
                <div className="text-center text-gray-500 p-4 dark:text-gray-400">
                    Gönderim bulunamadı.
                </div>
            )}

            {!loading && !error && submissions.length > 0 && (
                <div className="overflow-y-auto max-h-80">

                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">

                        <thead className="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Kullanıcı
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Soru
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Sonuç
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Süre (ms)
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Tarih
                                </th>
                            </tr>
                        </thead>

                        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                            {submissions.map((submission) => (

                                <tr key={submission.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                                            <a href={`/admin/user/${submission.user_id}`} className="hover:text-blue-600 dark:hover:text-blue-400">
                                                {submission.username}
                                            </a>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">

                                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                                            <a href={`/admin/question/${submission.question_id}`} className="hover:text-blue-600 dark:hover:text-blue-400">
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

                                        <div className="text-sm text-gray-900 dark:text-white">
                                            {submission.execution_time.toFixed(2)}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">

                                        <div className="text-sm text-gray-500 dark:text-gray-400">
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

// Bileşeni global olarak kullanılabilir hale getirin
window.RecentSubmissions = RecentSubmissions;