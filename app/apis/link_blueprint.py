from sanic import Blueprint
from sanic.response import json
from sanic.response import text
from sanic.response import raw 
from app.databases.mongodb import MongoDB

links_bp = Blueprint('link_blueprint')
_db = MongoDB()

# @links.route('/get-jwt', methods={'GET'})
# async def get_jwt(request):
#     password = request.args.get("password")
#     if password != Config.JWT_PASSWORD:
#         raise ApiUnauthorized("Wrong password")
#     token = generate_jwt()
#     return json({'token': str(token)})

# Get all customed links from a URL
@links_bp.route('/get-link', methods={'GET'})
async def get_link(request):
    args = request.args
    url  = request.args.get('url')
    result = _db.get_link(url)
    return json(result)


@links_bp.route('/create-link', methods={'POST'})
async def create_link(request):
    body = request.json
    original_url = body['url']
    shortened_link = _db.create_link(original_url)
    # return link
    return json({
        'message': f'{shortened_link}',
    })
 

@links_bp.route('/get-url', methods={'GET'})
async def get_url(request):
    link = request.args.get('link')
    result = _db.get_url(link)
    return json(result)


