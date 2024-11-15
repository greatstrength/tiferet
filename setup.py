try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
    'description': 'A multi-purpose application framework embodying beauty in form.',
    'author': 'Andrew Shatz',
    'url': r'https://github.com/greatstrength/app',
    'download_url': r'https://github.com/greatstrength/app',
    'author_email': 'andrew@greatstrength.me',
    'version': '1.0.0-alpha.3',
    'license': 'BSD 3',
    'install_requires': [
        'schematics>=2.1.1',
        'pyyaml>=6.0.1',
        'dependencies>=7.7.0'

    ],
    'packages': [
        'tiferet',
        'tiferet.clients',
        'tiferet.commands',
        'tiferet.configs',
        'tiferet.contexts',
        'tiferet.data',
        'tiferet.domain',
        'tiferet.repos',
        'tiferet.services',
    ],    
    'scripts': [],
    'name': 'tiferet'
}

setup(**config)