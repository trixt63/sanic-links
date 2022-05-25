from sanic_openapi.openapi2 import doc


class PostName:
    name = doc.String(description="Name", required=True)


name_json_schema = {
    'type': 'object',
    'required': ['name'],
    'properties': {
        'name': {'type': 'string'}
    }
}
