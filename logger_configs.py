LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s]: %(message)s'
        },
    },

    'handlers': {
        'error_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'errors.txt',
            'level': 'DEBUG'
        },
    },

    'loggers': {
        'error_logger': {
            'handlers': ['error_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}