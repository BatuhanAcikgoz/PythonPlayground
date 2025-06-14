const RecentQuestionsWidget = ({ title }) => {
    const [questions, setQuestions] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const fetchRecentQuestions = async () => {
            try {
                const response = await fetch('/api/last-questions-detail');
                if (!response.ok) {
                    throw new Error('API yanıtı başarısız oldu');
                }
                const data = await response.json();
                setQuestions(data);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchRecentQuestions();
    }, []);

    // Zorluk seviyesini metne çevir
    const getDifficultyText = (level) => {
        switch(level) {
            case 1: return "Kolay";
            case 2: return "Orta";
            case 3: return "Zor";
            case 4: return "Çok Zor";
            default: return "Bilinmiyor";
        }
    };

    // Zorluk seviyesine göre sınıf belirle
    const getDifficultyClass = (level) => {
        switch(level) {
            case 1: return "bg-green-100 text-green-800";
            case 2: return "bg-blue-100 text-blue-800";
            case 3: return "bg-yellow-100 text-yellow-800";
            case 4: return "bg-red-100 text-red-800";
            default: return "bg-gray-100 text-gray-800";
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 h-full">
            <h3 className="text-xl font-bold mb-4">{title}</h3>

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

            {!loading && !error && questions.length === 0 && (
                <div className="text-center text-gray-500 p-4">
                    Soru bulunamadı.
                </div>
            )}

            {!loading && !error && questions.length > 0 && (
                <div className="overflow-y-auto max-h-80">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Soru Başlığı
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Zorluk
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Puan
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Tarih
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {questions.map((question) => (
                                <tr key={question.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                            <a href={`/admin/question/${question.id}`} className="hover:text-blue-600">
                                                {question.title}
                                            </a>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm">
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyClass(question.difficulty)}`}>
                                                {getDifficultyText(question.difficulty)}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                            {question.points}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500">
                                            {question.created_at}
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