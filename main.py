from sanic import Sanic
from sanic import request
from app.apis.link_blueprint import links_bp 
from app.databases.mongodb import MongoDB

app = Sanic(__name__)
app.blueprint(links_bp)
db = MongoDB()

# cursor = db.get_url('https://fontawesome.com/v5/cheatsheet/free/solidabcde')
# result = cursor
# print(result)

app.run(host='0.0.0.0', port='8000', debug=True)

