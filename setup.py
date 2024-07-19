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
    'version': '0.3.0-alpha.1',
    'license': 'BSD 3',
    'install_requires': [
        'schematics>=2.1.1',
        'pyyaml>=6.0.1'
    ],
    'packages': [
        'aikicore',
        'aikicore.clients',
        'aikicore.commands',
        'aikicore.configs',
        'aikicore.contexts',
        'aikicore.data',
        'aikicore.objects',
        'aikicore.repositories'
        'aikicore.services',
    ],    
    'scripts': [],
    'name': 'aikicore',
    'entry_points': {
        'console_scripts': [
            'tiferet = tiferet_cli:main'
        ]
    }
}

setup(**config)