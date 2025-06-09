// Footer.jsx (Babel ile tarayıcıda çalışacak hali)

const Footer = () => {
    const { darkMode, toggleTheme } = window.useTheme(); // ✅ window'dan al

    const footerTrans = window.APP_DATA.footerTrans;
    const currentLang = window.APP_DATA.currentLang;

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
        <footer className="bg-gray-800 text-white py-4 mt-auto">
            <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    {/* Dark/Light Toggle Button */}
                    <button
                        onClick={toggleTheme}
                        className="mt-2 md:mt-0 bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm focus:outline-none"
                    >
                        {darkMode ? "🌞 Light Mode" : "🌙 Dark Mode"}
                    </button>

                    {/* Language Dropdown */}
                    <div className="order-2 md:order-3 mb-4 md:mb-0 relative lang-dropdown-container">
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setLangDropdownOpen(!langDropdownOpen);
                            }}
                            className="flex items-center bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm focus:outline-none"
                        >
                            <span className="mr-1">{languages[currentLang].flag}</span>
                            <span className="mr-1">{languages[currentLang].name}</span>
                            <svg className={`h-4 w-4 transition-transform ${langDropdownOpen ? 'transform rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7"></path>
                            </svg>
                        </button>

                        {langDropdownOpen && (
                            <div className="absolute bottom-full mb-2 right-0 w-32 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                                <div className="py-1" role="menu" aria-orientation="vertical">
                                    {Object.entries(languages).map(([code, lang]) => (
                                        <a
                                            key={code}
                                            href={`/language/${code}`}
                                            className={`flex items-center px-4 py-2 text-sm ${currentLang === code ? 'bg-gray-100 text-gray-900' : 'text-gray-700 hover:bg-gray-100'}`}
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
                        <p>&copy; {new Date().getFullYear()} PythonPlayground. {footerTrans.allRights}</p>
                        <p className="text-gray-400 text-xs mt-1">{footerTrans.platformDesc}</p>
                    </div>

                    <div className="hidden md:block order-3 md:order-1"></div>
                </div>
            </div>
        </footer>
    );
};

// ✅ Export yok, bunun yerine globale ata
window.Footer = Footer;
