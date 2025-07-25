# *** configs

# ** config: default_formatters
DEFAULT_FORMATTERS = [
    dict(
        id='default',
        name='Default Formatter',
        description='The default logging formatter.',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
]

# ** config: default_handlers
DEFAULT_HANDLERS = [
    dict(
        id='default_root',
        name='Default Root Handler',
        description='The default root logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='WARNING',
        formatter='default',
        stream='ext://sys.stderr'
    ),
    dict(
        id='default',
        name='Default Handler',
        description='The default logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter='default',
        stream='ext://sys.stdout'
    ),
    dict(
        id='debug',
        name='Debug Handler',
        description='A handler for debugging purposes.',
        module_path='logging',
        class_name='StreamHandler',
        level='DEBUG',
        formatter='default',
        stream='ext://sys.stdout'
    )
]

# ** config: default_loggers
DEFAULT_LOGGERS = [
    dict(
        id='root',
        name='Default Root Logger',
        description='The default logging configuration.',
        level='WARNING',
        handlers=['default_root'],
        propagate=False,
        is_root=True
    ),
    dict(
        id='default',
        name='Default Logger',
        description='The default logging configuration.',
        level='INFO',
        handlers=['default'],
        propagate=True,
        is_root=False
    ),
    dict(
        id='debug',
        name='Debug Logger',
        description='A logger for debugging purposes.',
        level='DEBUG',
        handlers=['debug'],
        propagate=True,
        is_root=False
    )
]

