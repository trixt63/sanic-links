from sanic import Blueprint
from sanic.response import json
from app.databases.mongodb import MongoDB

links_bp = Blueprint('link_blueprint')
_db = MongoDB()

# Get all customed links from a URL
@links_bp.route('/get-all-links', methods={'GET'})
async def get_all_links(request):
    args = request.args
    url  = request.args.get('url')
    result = _db.get_all_links(url)
    return json(result)


@links_bp.route('/create-link', methods={'POST'})
async def create_link(request):
    body = request.json
    original_url = body['url']
    customed_link = _db.create_link(original_url)
    # return link
    return json({
        'message': f'{customed_link}',
    })
 

@links_bp.route('/get-original-url', methods=['GET', 'POST'])
async def get_original_url(request):
    link = request.args.get('link')
    # get URL from a link
    result = _db.get_original_url(link)
    # increment the "view" counter in that link's document
    new_link_view = result['view'] + 1
    updated_link_view = {'$set':{'view': new_link_view}}
    _db.update_link(link, updated_link_view)
    # return API result
    return json(result)


@links_bp.route('/get-view-logs', methods={'GET'})
async def get_view_logs(request):
    url = request.args.get('url')
    view_logs = _db.get_url(url)['view_logs']
    return json(view_logs)
