from sanic_openapi.openapi2 import doc


class PostJWT:
    password = doc.String(description='Password')


jwt_json_schema = {
    'type': 'object',
    'required': ['password'],
    'properties': {
        'password': {
            'type': 'string'
        }
    }
}
