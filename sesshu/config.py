from cerberus import Validator

# Define the configuration schema (for validation).
SCHEMA = {
    'logging': {
        'type': 'dict',
        'schema': {
            'path': {'type': 'string'},
            'name': {'type': 'string'}
        }
    },
    'plugin': {
        'type': 'list',
        'schema': {'type': 'string'}
    },
    'workers': {
        'type': 'dict',
        'schema': {
            'count': {'type': 'integer', 'min': 1}
        }
    },
    'bus': {
        'type': 'dict',
        'schema': {
            'input': {
                'type': 'dict',
                'schema': {
                    'queue': {'type': 'string'}
                }
            },
            'output': {
                'type': 'dict',
                'schema': {
                    'topic': {'type': 'string'}
                }
            }
        }
    }
}


def validate(config):
    ''' Test whether the provided configuration object is valid. '''
    v = Validator(SCHEMA)
    if not v.validate(config):
        raise AttributeError(v.errors)
