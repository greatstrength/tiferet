try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
    'description': 'The Core Library for the Spirit of Harmony',
    'author': 'Andrew Shatz',
    'url': r'https://github.com/greatstrength/aikicore',
    'download_url': r'https://github.com/greatstrength/aikicore',
    'author_email': 'andrew@greatstrength.me',
    'version': '0.2.3',
    'license': 'BSD 3',
    'install_requires': [
        'schematics>=2.1.1',
        'pyyaml>=6.0.1'
    ],
    'packages': [
        'aikicore',
        'aikicore.config',
        'aikicore.objects',
    ],    
    'scripts': [],
    'name': 'aikicore'
}

setup(**config)