// ThemeContext.js

const ThemeContext = React.createContext();

const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = React.useState(() => {
    return localStorage.getItem("theme") === "dark";
  });

  React.useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  const toggleTheme = () => setDarkMode(prev => !prev);

  return (
    <ThemeContext.Provider value={{ darkMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

const useTheme = () => React.useContext(ThemeContext);

// ❗ Tarayıcıda çalışabilmesi için bu şekilde global window objesine at
window.ThemeContext = ThemeContext;
window.ThemeProvider = ThemeProvider;
window.useTheme = useTheme;
