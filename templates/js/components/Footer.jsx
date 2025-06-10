// Footer.jsx (Babel ile tarayıcıda çalışacak hali)

const Footer = () => {
    const { darkMode, toggleTheme } = window.useTheme();

    // APP_DATA'ya ve içindeki alt objelere güvenli erişim
    const appData = window.APP_DATA || {};
    const footerTrans = appData.footerTrans || {
        allRights: "Tüm Hakları Saklıdır.", // Varsayılan değerler
        platformDesc: "Eğitici ve etkileşimli bir platform.", // Varsayılan değerler
    };
    const currentLang = appData.currentLang || 'tr'; // Varsayılan dil 'tr'

    const [langDropdownOpen, setLangDropdownOpen] = React.useState(false);

    const languages = {
        tr: { name: "Türkçe", flag: "🇹🇷" },
        en: { name: "English", flag: "🇬🇧" }
    };

    React.useEffect(() => {
        if (!langDropdownOpen) return;

        const handleOutsideClick = (event) => {
            if (!event.target.closest('.lang-dropdown-container')) {
                setLangDropdownOpen(false);
            }
        };

        document.addEventListener('click', handleOutsideClick);
        return () => document.removeEventListener('click', handleOutsideClick);
    }, [langDropdownOpen]);

    return (
        <footer className="bg-gray-800 text-white py-4 mt-auto
                           dark:bg-gray-900 dark:text-gray-200"> {/* Dark mode stilleri eklendi */}
            <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    {/* Tema Değiştirme Butonu */}
                    <button
                        onClick={toggleTheme}
                        className="mt-2 md:mt-0 px-3 py-1 rounded text-sm focus:outline-none transition-colors duration-200
                                   bg-gray-700 hover:bg-gray-600 text-white
                                   dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-100" // Buton için dark/light stilleri
                        aria-label="Toggle dark mode"
                    >
                        {darkMode ? (
                            <span className="flex items-center">
                                <svg className="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
                                </svg>
                                Light Mode
                            </span>
                        ) : (
                            <span className="flex items-center">
                                <svg className="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 4a1 1 0 011 1v1a1 1 0 11-2 0V7a1 1 0 011-1zm-4 4a1 1 0 00-1 1v1a1 1 0 102 0v-1a1 1 0 00-1-1zm5.657-5.657a1 1 0 010 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zm-7.071 7.071a1 1 0 010 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM3 10a1 1 0 011-1h1a1 1 0 110 2H4a1 1 0 01-1-1zm9-5a1 1 0 011-1h1a1 1 0 110 2h-1a1 1 0 01-1-1zm-6.343 9.343a1 1 0 010 1.414l-.707.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0z" clipRule="evenodd"></path>
                                </svg>
                                Dark Mode
                            </span>
                        )}
                    </button>

                    {/* Language Dropdown */}
                    <div className="order-2 md:order-3 mb-4 md:mb-0 relative lang-dropdown-container">
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setLangDropdownOpen(!langDropdownOpen);
                            }}
                            className="flex items-center px-3 py-1 rounded text-sm focus:outline-none transition-colors duration-200
                                       bg-gray-700 hover:bg-gray-600 text-white
                                       dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-100" // Buton için dark/light stilleri
                        >
                            <span className="mr-1">{languages[currentLang].flag}</span>
                            <span className="mr-1">{languages[currentLang].name}</span>
                            <svg className={`h-4 w-4 transition-transform ${langDropdownOpen ? 'transform rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7"></path>
                            </svg>
                        </button>

                        {langDropdownOpen && (
                            <div className="absolute bottom-full mb-2 right-0 w-32 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10
                                            dark:bg-gray-700 dark:ring-gray-700"> {/* Dropdown menüsü için dark mode stilleri */}
                                <div className="py-1" role="menu" aria-orientation="vertical">
                                    {Object.entries(languages).map(([code, lang]) => (
                                        <a
                                            key={code}
                                            href={`/language/${code}`}
                                            className={`flex items-center px-4 py-2 text-sm transition-colors duration-150
                                            ${currentLang === code
                                                ? 'bg-gray-100 text-gray-900 dark:bg-gray-600 dark:text-gray-100' // Seçili öğe için dark mode stilleri
                                                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600' // Diğer öğeler için dark mode stilleri
                                            }`}
                                            role="menuitem"
                                        >
                                            <span className="mr-2">{lang.flag}</span>
                                            {lang.name}
                                        </a>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Footer Text */}
                    <div className="order-1 md:order-2 mb-4 md:mb-0 text-center flex-grow">
                        <p className="text-white dark:text-gray-200">&copy; {new Date().getFullYear()} PythonPlayground. {footerTrans.allRights}</p>
                        <p className="text-gray-400 text-xs mt-1 dark:text-gray-400">{footerTrans.platformDesc}</p>
                    </div>

                    <div className="hidden md:block order-3 md:order-1"></div>
                </div>
            </div>
        </footer>
    );
};

window.Footer = Footer;