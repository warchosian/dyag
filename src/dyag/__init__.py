"""
dyag - Markdown to HTML converter with diagram support
"""

import os
import warnings

# Configurer HF_HOME dès le début pour éviter les warnings de transformers
# (remplace l'ancien TRANSFORMERS_CACHE qui est déprécié)
if 'TRANSFORMERS_CACHE' in os.environ and 'HF_HOME' not in os.environ:
    os.environ['HF_HOME'] = os.environ['TRANSFORMERS_CACHE']

# Supprimer l'avertissement de dépréciation de TRANSFORMERS_CACHE
# car nous le gérons déjà en configurant HF_HOME
warnings.filterwarnings('ignore', message='.*TRANSFORMERS_CACHE.*', category=FutureWarning)

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["__version__", "__author__", "__email__"]
