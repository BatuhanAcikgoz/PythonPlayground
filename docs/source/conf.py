# conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'PythonPlayground'
copyright = '2025, BatuhanAcikgoz'
author = 'BatuhanAcikgoz'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',  # Python standart kütüphane bağlantıları
    'sphinx.ext.autosummary',  # Otomatik özet oluşturma
    'sphinxext.opengraph',  # Doğru import path
]

# OpenGraph ayarları
ogp_site_url = "https://batuhanacikgoz.github.io/PythonPlayground/"
ogp_description_length = 300
ogp_type = "website"
ogp_site_name = "PythonPlayground"

templates_path = ['_templates']
exclude_patterns = []
language = 'tr'

html_title = "PythonPlayground"
html_theme = 'furo'
html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#43b1b0",  # Wagtail yeşil-mavi
        "color-brand-content": "#43b1b0",
        "color-admonition-background": "#f5fafa",
        "font-stack": "'Nunito Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        "font-stack--monospace": "'Inconsolata', monospace",
    },
    "dark_css_variables": {
        "color-brand-primary": "#59c1c0",
        "color-brand-content": "#59c1c0",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/batuhanacikgoz/PythonPlayground",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

html_js_files = [
    'https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;700&family=Inconsolata&display=swap',
]

html_static_path = ['_static']
html_css_files = ['custom.css']

# Autodoc ayarları
autodoc_member_order = 'groupwise'  # bysource yerine
autoclass_content = 'both'
autodoc_typehints = 'description'  # Tip bilgilerini açıklamalarda göster