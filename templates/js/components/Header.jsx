// static/js/components/Header.jsx
const Header = () => {
    // Access global variables from window.APP_DATA
    // **GÜNCELLEME BAŞLANGICI**
    const appData = window.APP_DATA || {}; // window.APP_DATA yoksa boş bir obje kullan
    const isLoggedIn = appData.isLoggedIn;
    const isAdmin = appData.isAdmin;
    const username = (appData.userData && appData.userData.username) || null; // userData yoksa null
    const userEmail = (appData.userData && appData.userData.email) || null; // userData yoksa null
    // **GÜNCELLEME SONU**

    const [dropdownOpen, setDropdownOpen] = React.useState(false);
    const headerTrans = appData.headerTrans || { // appData'dan çek
        home: "Ana Sayfa",
        questions: "Sorular",
        about: "Hakkında",
        leaderboard: "Sıralama",
        profile: "Profil",
        settings: "Ayarlar",
        logout: "Çıkış Yap",
        login: "Giriş Yap",
        register: "Kayıt Ol",
        appName: "Python Playground",
        tagline: "Python ile eğlenceli bir şekilde öğrenin",
    };

    // Generate MD5 hash for Gravatar
    const getGravatarURL = (email) => {
        // Default to a placeholder if no email
        if (!email) return "https://www.gravatar.com/avatar/?d=mp";

        // Convert email to lowercase and trim
        const processedEmail = email.toLowerCase().trim();

        // Create MD5 hash using a simple implementation
        const hash = Array.from(processedEmail).reduce((acc, char) => {
            return (((acc << 5) - acc) + char.charCodeAt(0)) & 0xFFFFFFFF;
        }, 0).toString(16);

        return `https://www.gravatar.com/avatar/${hash}?d=mp&s=40`;
    };

    // Close dropdown when clicking outside
    React.useEffect(() => {
        if (!dropdownOpen) return;

        const handleOutsideClick = (event) => {
            if (!event.target.closest('.user-dropdown-container')) {
                setDropdownOpen(false);
            }
        };

        document.addEventListener('click', handleOutsideClick);
        return () => document.removeEventListener('click', handleOutsideClick);
    }, [dropdownOpen]);

  return (
    <header className="bg-gradient-to-r from-gray-800 to-gray-700 text-white shadow-md">
            <div className="container mx-auto px-4 py-6">
                <div className="flex flex-col md:flex-row md:justify-between md:items-center">
                    <div className="flex items-center mb-4 md:mb-0">
                        <svg className="h-10 w-10 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                        <div>
                            <h1 className="text-2xl font-bold">{headerTrans.appName}</h1>
                            <p className="text-blue-100 text-sm">{headerTrans.tagline}</p>
                        </div>
                    </div>
                    <nav>
                        <ul className="flex space-x-6 items-center">
                            <li><a href="/" className="text-white hover:text-blue-200 font-medium">{headerTrans.home}</a></li>
                            <li><a href="/questions" className="text-white hover:text-blue-200 font-medium">{headerTrans.questions}</a></li>
                            <li><a href="/leaderboard" className="text-white hover:text-blue-200 font-medium">{headerTrans.leaderboard}</a></li>
                            <li><a href="/about" className="text-white hover:text-blue-200 font-medium">{headerTrans.about}</a></li>
                            {isLoggedIn ? ( // isLoggedIn zaten kontrol edildi
                                <React.Fragment>
                                    <li className="relative user-dropdown-container">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setDropdownOpen(!dropdownOpen);
                                            }}
                                            className="flex items-center text-blue-200 hover:text-white font-medium focus:outline-none"
                                        >
                                            <img src={getGravatarURL(userEmail)} alt={headerTrans.profile} className="w-8 h-8 rounded-full mr-2" />
                                            <span>{username}</span>
                                            <svg className={`ml-1 h-4 w-4 transition-transform ${dropdownOpen ? 'transform rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                            </svg>
                                        </button>

                                        {dropdownOpen && (
                                            <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                                                <div className="py-1" role="menu" aria-orientation="vertical">
                                                    {isAdmin ?(
                                                        <React.Fragment>
                                                            <a href="/admin" className="flex px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 items-center" role="menuitem">
                                                                <svg className="h-4 w-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                                                </svg>
                                                                {headerTrans.adminPanel}
                                                            </a>
                                                        </React.Fragment>
                                                     ): null}
                                                    <a href="/profil" className="flex px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 items-center" role="menuitem">
                                                        <svg className="h-4 w-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                                        </svg>
                                                        {headerTrans.profile}
                                                    </a>
                                                    <a href="/settings" className="flex px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 items-center" role="menuitem">
                                                        <svg className="h-4 w-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                                        </svg>
                                                        {headerTrans.settings}
                                                    </a>
                                                    <div className="border-t border-gray-100"></div>
                                                    <a href="/logout" className="flex px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 items-center" role="menuitem">
                                                        <svg className="h-4 w-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                                                        </svg>
                                                        {headerTrans.logout}
                                                    </a>
                                                </div>
                                            </div>
                                        )}
                                    </li>
                                </React.Fragment>
                            ) : (
                                <React.Fragment>
                                    <li><a href="/login" className="text-white hover:text-blue-200 font-medium">{headerTrans.login}</a></li>
                                    <li><a href="/register" className="text-white hover:text-blue-200 font-medium">{headerTrans.register}</a></li>
                                </React.Fragment>
                            )}
                        </ul>
                    </nav>
                </div>
            </div>
        </header>
    );
};