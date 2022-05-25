from pymongo import MongoClient
from uuid import uuid4
from app.constants.mongodb_constants import MongoCollections, MongoIndex, MongoKeys
from config import MongoDBConfig
from app.utils.time_utils import get_timestamp
from app.utils.logger_utils import get_logger # logger utility

logger = get_logger('MongoDB')

class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'
        self.connection_url = connection_url.split('@')[-1]
        self.client = MongoClient(connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]
        self._links_col = self.db[MongoCollections.links]
        self._urls_col = self.db[MongoCollections.urls]
        self._create_index()

    def _create_index(self):
        if MongoIndex.link_index not in self._links_col.index_information():
            self._links_col.create_index([('_id', 'hashed')], name=MongoIndex.link_index)
        logger.info('Indexed !!!')

    # Get all customed links from a URL
    def get_link(self, url):
        try:
            filter_ = {'url': url} # query with URL
            cursor = self._links_col.find(filter_)
            queried_result = list(cursor) 
            links = list()
            for result in queried_result:
                links.append(result['link'])
            nonce = len(links)
            result = {'nonce': nonce, 'links': links}
            return result 
        except Exception as ex:
            logger.exception(ex)
        return None
    
    # generate a link from an url
    def _generate_link(self, url):
        shortened_link = str(uuid4())
        return shortened_link

    # Create a new link from an URL and insert into database
    def create_link(self, url):
        try: 
            link = self._generate_link(url) # create the new link
            # update in the database
            filter_ = {'url': url}
            old_url_doc = self._urls_col.find_one(filter_)
            # if the URL already in the database:
            if(old_url_doc != None):
                # update the "links" collection
                old_url = dict(old_url_doc)
                new_links_doc = {'url':url, 'nonce':old_url['n_links'], 'link':link , 'view':0} # new document for the "links" collection
                self._links_col.insert_one(new_links_doc)
                # update the "urls" collection 
                updated_url_doc = { '$set': {'n_links':old_url['n_links']+1, 'last_updated_at': get_timestamp()}}
                self._urls_col.update_one(filter_, updated_url_doc)
            else:
                new_links_doc = {'url':url, 'nonce':0, 'link':link, 'view': 0} # new document for the "links" collection
                new_urls_doc = {'url':url, 'n_links':1, 'view_logs': {}, 'last_updated_at':get_timestamp()} # new document for the "links" collection
                self._links_col.insert_one(new_links_doc)
                self._urls_col.insert_one(new_urls_doc)
            return link
        except Exception as ex:
            logger.exception(ex) 

    # From a link, gets the URL and the infos about that URL
    def get_url(self, link):
        try:
            link_filter = {'link': link}
            link_doc = self._links_col.find_one(link_filter, {'url':1, 'nonce': 1, 'view': 1}) # find one instance of the input link
            if link_doc != None:
                # Update the view on the link's document 
                link_view = link_doc['view']
                update_link_view = {'$set': {'view': link_view+1}}
                self._links_col.update_one(link_filter, update_link_view)
                # Update the views log in the URL collection
                url = link_doc['url'] # Get the URL
                url_filter = {'url': url}
                url_doc = self._urls_col.find_one(url_filter)
                view_logs = url_doc['view_logs']
                timestamp = get_timestamp()
                if timestamp in view_logs: # if timestamp is already in the view log then increment the view count
                    view_logs[timestamp] = view_logs[timestamp] + 1
                else: # else view count = 1
                    view_logs[timestamp] = 1
                update_url_view_logs = {'$set': {'view_logs': view_logs}}
                self._urls_col.update_one(url_filter, update_url_view_logs)
                # Return the URL and the nonce of the input link 
                result = {'url': link_doc['url'], 'nonce': link_doc['nonce']}
                return result 
            else:
                return None  
        except Exception as ex:
            logger.exception(ex) 

    # From an URL, get the view logs
    def get_view_logs(self, url):
        try:
            filter_ = {'url':url}
            url_doc = self._urls_col.find_one(filter_)
            return url_doc['view_logs']
        except Exception as ex:
            logger.exception(ex)





