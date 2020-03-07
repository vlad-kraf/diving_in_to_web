REVIEW_CHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'objects',
    'properties' : {
        'feedback': {
            'type': 'string',
            'minLength': 3,
            'maxLength': 10,
        },
        'grade' : {
            'type': 'integer',
            'maximum': 100,
            'minimum': 1
        },
    },
    'required': ['feedback', 'grade'],
}