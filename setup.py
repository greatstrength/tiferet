try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
    'description': 'The Core Library for the Spirit of Harmony',
    'author': 'Andrew Shatz',
    'url': r'https://github.com/greatstrength/app',
    'download_url': r'https://github.com/greatstrength/app',
    'author_email': 'andrew@greatstrength.me',
    'version': '1.0.0-alpha.0',
    'license': 'BSD 3',
    'install_requires': [
        'schematics>=2.1.1',
        'pyyaml>=6.0.1'
    ],
    'packages': [
        'app',
        'app.clients',
        'app.commands',
        'app.configs',
        'app.containers',
        'app.contexts',
        'app.data',
        'app.objects',
        'app.repositories',
        'app.services',
    ],    
    'scripts': [],
    'name': 'app',
    'entry_points': {
        'console_scripts': [
            'tiferet = tiferet_cli:main'
        ]
    }
}

setup(**config)