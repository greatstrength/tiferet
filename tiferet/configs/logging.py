# *** configs

# ** config: default_logging_settings
DEFAULT_LOGGING_SETTINGS = dict(
    id='default_logging',
    version=1,
    disable_existing_loggers=False,
    formatters=[
        dict(
            name='simple',
            description='Simple log formatter',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    ],
    handlers=[
        dict(
            name='console',
            description='Console log handler',
            module_path='logging',
            class_name='StreamHandler',
            level='INFO',
            formatter='simple',
            stream='ext://sys.stdout'
        ),
        dict(
            name='file',
            description='File log handler',
            module_path='logging',
            class_name='FileHandler',
            level='DEBUG',
            formatter='simple',
            filename='app.log'
        )
    ],
    loggers=[
        dict(
            name='tiferet',
            level='DEBUG',
            handlers=['console', 'file'],
            propagate=True,
            description='Tiferet application logger'
        ),
        dict(
            name='root',
            level='WARNING',
            handlers=['console'],
            description='Root logger for the application',
            is_root=True
        )
    ]
)