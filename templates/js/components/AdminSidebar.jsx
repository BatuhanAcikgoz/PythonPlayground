// import React from 'react'; // Bu satırı yorum satırı yapın veya silin

// Eğer ThemeContext'i kullanıyorsanız, onu da import etmeniz gerekebilir:
// import { useTheme } from './ThemeContext'; // veya ThemeContext'in bulunduğu doğru yol

const AdminSidebar = () => {
  // ThemeContext'i App.jsx'te kullanıyorsunuz. Sidebar'da kullanmak için buraya da import etmeniz gerekir.
  // Eğer sidebar'ın kendisi doğrudan temayı değiştiren bir kontrol içermiyorsa,
  // sadece dışarıdan gelen darkMode prop'una veya genel body sınıfına güvenmek yeterli olabilir.
  // Bu örnekte, 'dark' sınıfının body'ye veya ana conteynere eklenip Tailwind'in bunu tanımasını bekliyoruz.

  const urls = window.ADMIN_URLS || {
    dashboard: "/admin/",
    users: "/admin/users",
    programmingQuestions: "/admin/programming-questions",
    newProgrammingQuestion: "/admin/programming-questions/new",
    newProgrammingQuestionAi: "/admin/programming-questions/new_ai",
    testQuestion: "/admin/programming-questions",
    badges: "/admin/badges",
    newBadge: "/admin/badges/new",
    settings: "/admin/settings",
    viewSubmissions: "/admin/programming-questions"
  };

  const sidebar_translations = (window.APP_DATA && window.APP_DATA.sidebar_translations) || {
    dashboard: "Dashboard",
    users: "Kullanıcılar",
    manage_users: "Kullanıcıları Yönet",
    add_user: "Yeni Kullanıcı Ekle",
    edit_user: "Kullanıcı Düzenle",
    programming_questions: "Programlama Soruları",
    manage_questions: "Soruları Yönet",
    add_question: "Yeni Soru Ekle",
    add_question_ai: "Yeni Soru Ekle (AI)",
    view_submissions: "Çözümleri Görüntüle",
    test_questions: "Soruları Test Et",
    settings: "Ayarlar",
    badges: "Rozetler",
    manage_badges: "Rozetleri Yönet",
    add_badge: "Yeni Rozet Ekle",
    view_question: "Soruyu Görüntüle",
    edit_question: "Soruyu Düzenle"
  };

  return (
    // Sidebar'ın genel konteyneri:
    // Mevcut body ve App div'inin dark mode mantığına uygun olarak
    // bu sidebar da light modda bg-white, dark modda bg-gray-900 olacak.
    // text-black dark:text-white sınıflarını buraya ekleyerek tüm metinlerin varsayılan rengini ayarlıyoruz.
    <div className="w-64 min-h-screen shadow-lg bg-white text-black dark:bg-gray-900 dark:text-white">
      {/* Admin Panel Başlığı */}
      <div className="p-4 border-b border-gray-300 dark:border-gray-700">
        {/* Başlığın rengini de light modda siyah, dark modda beyaz olarak belirliyoruz. */}
        <h2 className="text-xl font-semibold text-black dark:text-white">Admin Panel</h2>
      </div>
      <nav className="mt-4">
        <ul>

          {/* Dashboard */}
          <li className="mb-1">
            <a
              href={urls.dashboard}
              // Metin rengi: light modda siyah, dark modda beyaz.
              // Hover renkleri de orijinal kodunuzdaki gibi kalacak.
              className="flex items-center py-2 px-4 text-black dark:text-white hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10l9-7 9 7v10a2 2 0 01-2 2H5a2 2 0 01-2-2V10z" />
              </svg>
              {sidebar_translations.dashboard}
            </a>
          </li>

          {/* Users Section */}
          <li className="mb-1">
            {/* Başlık (tıklanabilir değil) - light modda siyah, dark modda beyaz */}
            <div className="flex items-center py-2 px-4 text-black dark:text-white">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              {sidebar_translations.users}
            </div>
            <ul className="pl-10">
              <li>
                <a className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.manage_users}
                </a>
              </li>
              {/* Add User ve Edit User için URL'ler ve linkler eklenebilir. */}
              {/* <li>
                <a href={urls.addUser} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.add_user}
                </a>
              </li>
              <li>
                <a href={urls.editUser} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.edit_user}
                </a>
              </li> */}
            </ul>
          </li>

          {/* Programming Questions Section */}
          <li className="mb-1">
            {/* Başlık (tıklanabilir değil) - light modda siyah, dark modda beyaz */}
            <div className="flex items-center py-2 px-4 text-black dark:text-white">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {sidebar_translations.programming_questions}
            </div>
            <ul className="pl-10">
              <li>
                <a href={urls.programmingQuestions} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.manage_questions}
                </a>
              </li>
              <li>
                <a href={urls.newProgrammingQuestion} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.add_question}
                </a>
              </li>
              <li>
                <a href={urls.newProgrammingQuestionAi} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.add_question_ai}
                </a>
              </li>
              <li>
                <a href={urls.viewSubmissions} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.view_submissions}
                </a>
              </li>
              <li>
                <a href={urls.testQuestion} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.test_questions}
                </a>
              </li>
            </ul>
          </li>

          {/* Badges Section */}
          <li className="mb-1">
            <div className="flex items-center py-2 px-4 text-black dark:text-white">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
              </svg>
              {sidebar_translations.badges}
            </div>
            <ul className="pl-10">
              <li>
                <a href={urls.badges} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.manage_badges}
                </a>
              </li>
              <li>
                <a href={urls.newBadge} className="block py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
                  {sidebar_translations.add_badge}
                </a>
              </li>
            </ul>
          </li>

          {/* Settings */}
          <li className="mb-1">
            <a href={urls.settings} className="flex items-center py-2 px-4 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-black dark:hover:text-white">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {sidebar_translations.settings}
            </a>
          </li>

        </ul>
      </nav>
    </div>
  );
};

// Bu satırı kaldırın veya aşağıdaki gibi değiştirin:
// export default AdminSidebar;

// Bileşeni global olarak kullanılabilir hale getirin
window.AdminSidebar = AdminSidebar;