// import React from 'react'; // Eğer global React tanımına güveniyorsanız bu yorum kalabilir, aksi halde açın.

const RecentUsersWidget = ({ title }) => {
    const [users, setUsers] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const fetchRecentUsers = async () => {
            try {
                const response = await fetch('/api/recent-users');
                if (!response.ok) {
                    throw new Error('Failed to fetch recent users');
                }
                const data = await response.json();
                // API doğrudan dizi döndürüyor, data.users değil
                setUsers(data);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchRecentUsers();
    }, []);

    return (
        // Ana konteyner: bg-white -> dark:bg-gray-800, shadow-md -> dark:shadow-md
        <div className="bg-white rounded-lg shadow-md p-6 h-full dark:bg-gray-800 dark:shadow-md">
            <h3 className="text-xl font-bold mb-4 text-black dark:text-white">{title}</h3>

            {loading && (
                <div className="flex justify-center items-center h-40 text-gray-700 dark:text-gray-300">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            )}

            {error && (
                <div className="text-center text-red-500 p-4 dark:text-red-400">
                    Error: {error}
                </div>
            )}

            {!loading && !error && users.length === 0 && (
                <div className="text-center text-gray-500 p-4 dark:text-gray-400">
                    No users found.
                </div>
            )}

            {!loading && !error && users.length > 0 && (
                <div className="overflow-y-auto max-h-80">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Username
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Email
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Roles
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                                    Date
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                            {users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                                            <a href={`/admin/user/${user.id}/roles`} className="hover:text-blue-600 dark:hover:text-blue-400">
                                                {user.username}
                                            </a>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500 dark:text-gray-400">
                                            {user.email}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex flex-wrap gap-1">
                                            {user.roles.map((role, index) => (
                                                <span
                                                    key={index}
                                                    className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                                                    {role}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">

                                        <div className="text-sm text-gray-500 dark:text-gray-400">
                                            {user.registered}
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
window.RecentUsersWidget = RecentUsersWidget;