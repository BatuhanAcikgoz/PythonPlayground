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

# Furo teması kullanımı (daha modern bir tema)
html_theme = 'furo'  # sphinx_rtd_theme yerine
html_theme_options = {
    "light_css_variables": {
        "font-stack": "Lato, sans-serif",
        "font-stack--monospace": "Fira Code, monospace",
    },
    "sidebar_hide_name": False,
}

html_static_path = ['_static']
html_css_files = ['custom.css']

# Autodoc ayarları
autodoc_member_order = 'groupwise'  # bysource yerine
autoclass_content = 'both'
autodoc_typehints = 'description'  # Tip bilgilerini açıklamalarda göster