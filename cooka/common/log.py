import os
import logging.config


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {processName} {threadName}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'tornado.access': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
        'tornado.application': {
                    'handlers': ['console'],
                    'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
                    'propagate': False,
                },
        'tornado.general': {
                    'handlers': ['console'],
                    'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
                    'propagate': False,
                },
        'cooka-web': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
        'cooka-common': {
                    'handlers': ['console'],
                    'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
                    'propagate': False,
        },
        'cooka-core': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                    'propagate': False,
        },
    },
}


logging.config.dictConfig(LOGGING)

log_web = logging.getLogger("cooka-web")
log_common = logging.getLogger("cooka-common")
log_core = logging.getLogger("cooka-core")


