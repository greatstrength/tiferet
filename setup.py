try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
    'description': 'A multi-purpose application framework embodying beauty in form.',
    'author': 'Andrew Shatz',
    'url': r'https://github.com/greatstrength/tiferet',
    'download_url': r'https://github.com/greatstrength/tiferet',
    'author_email': 'andrew@greatstrength.me',
    'version': '2.0.0-alpha.0',
    'license': 'BSD 3',
    'install_requires': [
        'schematics>=2.1.1',
        'pyyaml>=6.0.1',
        'dependencies>=7.7.0'
    ],
    'packages': [
        'tiferet',
        'tiferet.configs',
        'tiferet.contexts',
        'tiferet.handlers',
        'tiferet.models',
        'tiferet.commands',
        'tiferet.contracts',
        'tiferet.data',
        'tiferet.proxies',
        'tiferet.clients',
    ],    
    'scripts': [],
    'name': 'tiferet',
    'extras_require': {
        'test': ['pytest>=8.3.3', 'pytest_env>=1.1.5'],
    }
}

setup(**config)