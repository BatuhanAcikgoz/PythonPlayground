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
]

templates_path = ['_templates']
exclude_patterns = []
language = 'tr'

# Tema yapılandırması
html_theme = 'furo'
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "announcement": "Bu dokümantasyon geliştirilme aşamasındadır.",
    "light_css_variables": {
        "color-brand-primary": "#2980B9",
        "color-brand-content": "#2980B9",
        "font-stack": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
        "font-stack--monospace": "SFMono-Regular, Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace",
    },
}

html_static_path = ['_static']
html_css_files = ['custom.css']

# Autodoc ayarları
autodoc_member_order = 'groupwise'  # bysource yerine
autoclass_content = 'both'
autodoc_typehints = 'description'  # Tip bilgilerini açıklamalarda göster