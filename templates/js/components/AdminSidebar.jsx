const AdminSidebar = () => {
    // URL'leri sabit değerler olarak tanımla (hardcoded değerler)
    const urls = window.ADMIN_URLS || {
        dashboard: "/admin/",
        users: "/admin/users",
        programmingQuestions: "/admin/programming-questions",
        newProgrammingQuestion: "/admin/programming-questions/new",
        testQuestion: "/admin/programming-questions", // ID gerekeceğinden dinamik oluşturulacak
        badges: "/admin/badges",
        newBadge: "/admin/badges/new",
        settings: "/admin/settings",
        viewSubmissions: "/admin/programming-questions" // Dinamik ID gerekeceğinden genel sayfaya yönlendirir
    };

    const translations = {
        dashboard: "Dashboard",
        users: "Kullanıcılar",
        manage_users: "Kullanıcıları Yönet",
        add_user: "Yeni Kullanıcı Ekle",
        edit_user: "Kullanıcı Düzenle",
        programming_questions: "Programlama Soruları",
        manage_questions: "Soruları Yönet",
        add_question: "Yeni Soru Ekle",
        view_submissions: "Çözümleri Görüntüle",
        test_questions: "Soruları Test Et",
        settings: "Ayarlar",
        badges: "Rozetler",
        manage_badges: "Rozetleri Yönet",
        add_badge: "Yeni Rozet Ekle",
        view_question: "Soruyu Görüntüle",
        edit_question: "Soruyu Düzenle",
    };

    return (
        <div className="bg-gray-800 text-white w-64 min-h-screen shadow-lg">
            <div className="p-4 border-b border-gray-700">
                <h2 className="text-xl font-semibold">Admin Panel</h2>
            </div>

            <nav className="mt-4">
                <ul>
                    {/* Dashboard */}
                    <li className="mb-1">
                        <a href={urls.dashboard} className="flex items-center py-2 px-4 text-gray-300 hover:bg-gray-700 hover:text-white">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                            </svg>
                            {translations.dashboard}
                        </a>
                    </li>

                    {/* Users Section */}
                    <li className="mb-1">
                        <div className="flex items-center py-2 px-4 text-gray-300">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            {translations.users}
                        </div>
                        <ul className="pl-10">
                            <li>
                                <a href={urls.users} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.manage_users}
                                </a>
                            </li>
                        </ul>
                    </li>

                    {/* Programming Questions Section */}
                    <li className="mb-1">
                        <div className="flex items-center py-2 px-4 text-gray-300">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            {translations.programming_questions}
                        </div>
                        <ul className="pl-10">
                            <li>
                                <a href={urls.programmingQuestions} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.manage_questions}
                                </a>
                            </li>
                            <li>
                                <a href={urls.newProgrammingQuestion} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.add_question}
                                </a>
                            </li>
                            <li>
                                <a href={urls.programmingQuestions} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.view_submissions}
                                </a>
                            </li>
                            <li>
                                <a href={urls.programmingQuestions} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.test_questions}
                                </a>
                            </li>
                        </ul>
                    </li>

                    {/* Badges Section */}
                    <li className="mb-1">
                        <div className="flex items-center py-2 px-4 text-gray-300">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"></path>
                            </svg>
                            {translations.badges}
                        </div>
                        <ul className="pl-10">
                            <li>
                                <a href={urls.badges} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.manage_badges}
                                </a>
                            </li>
                            <li>
                                <a href={urls.newBadge} className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.add_badge}
                                </a>
                            </li>
                        </ul>
                    </li>

                    {/* Settings */}
                    <li className="mb-1">
                        <a href={urls.settings} className="flex items-center py-2 px-4 text-gray-300 hover:bg-gray-700 hover:text-white">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            {translations.settings}
                        </a>
                    </li>
                </ul>
            </nav>
        </div>
    );
};