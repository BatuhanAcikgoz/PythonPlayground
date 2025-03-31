const AdminSidebar = () => {
    const translations = {
        dashboard: "Dashboard",
        users: "Users",
        manage_users: "Manage Users",
        add_user: "Add New User",
        courses: "Courses",
        manage_courses: "Manage Courses",
        add_course: "Add New Course",
        questions: "Questions",
        manage_questions: "Manage Questions",
        add_question: "Add New Question",
        settings: "Settings"
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
                        <a href="/admin" className="flex items-center py-2 px-4 text-gray-300 hover:bg-gray-700 hover:text-white">
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
                                <a href="/admin/users" className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.manage_users}
                                </a>
                            </li>
                            <li>
                                <a href="/admin/user/new" className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.add_user}
                                </a>
                            </li>
                        </ul>
                    </li>

                    {/* Courses Section */}
                    <li className="mb-1">
                        <div className="flex items-center py-2 px-4 text-gray-300">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                            </svg>
                            {translations.courses}
                        </div>
                        <ul className="pl-10">
                            <li>
                                <a href="/admin/courses" className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.manage_courses}
                                </a>
                            </li>
                            <li>
                                <a href="/admin/course/new" className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.add_course}
                                </a>
                            </li>
                        </ul>
                    </li>

                    {/* Questions Section */}
                    <li className="mb-1">
                        <div className="flex items-center py-2 px-4 text-gray-300">
                            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            {translations.questions}
                        </div>
                        <ul className="pl-10">
                            <li>
                                <a href="/admin/questions" className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.manage_questions}
                                </a>
                            </li>
                            <li>
                                <a href="/admin/question/new" className="block py-2 px-4 text-gray-400 hover:bg-gray-700 hover:text-white">
                                    {translations.add_question}
                                </a>
                            </li>
                        </ul>
                    </li>

                    {/* Settings */}
                    <li className="mb-1">
                        <a href="/admin/settings" className="flex items-center py-2 px-4 text-gray-300 hover:bg-gray-700 hover:text-white">
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