from core.config import LogSettings

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DEFAULT_HANDLERS = ['console', ]

log_settings = LogSettings()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT
        },
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(levelprefix)s %(client_addr)s - \
                   '%(request_line)s' %(status_code)s",
        },
    },
    'handlers': {
        'console': {
            'level': log_settings.LOG_HANDLERS_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': LOG_DEFAULT_HANDLERS,
            'level': log_settings.LOG_LOGGER_LEVEL,
        },
        'uvicorn.error': {
            'level': log_settings.LOG_LOGGER_LEVEL,
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': log_settings.LOG_LOGGER_LEVEL,
            'propagate': False,
        },
    },
    'root': {
        'level': log_settings.LOG_ROOT_LEVEL,
        'formatter': 'verbose',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}
