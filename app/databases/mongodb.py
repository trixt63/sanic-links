import time
from pymongo import MongoClient
from uuid import uuid4
from app.constants.mongodb_constants import MongoCollections, MongoIndex, MongoKeys
from config import MongoDBConfig
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

    def get_all_urls(self):
        '''Get all URLS in the database'''
        try:
            cursor = self._urls_col.find({}, {'url': 1})
            queried_result = list(cursor)
            urls = list()
            for result in queried_result:
                urls.append(result['url'])
            return urls
        except Exception as ex:
            logger.exception(ex)
        return None

    def get_link(self, link):
        '''Get a document from the "links" collection'''
        try:
            filter_ = {'link': link}
            cursor = self._links_col.find_one(filter_)
            return cursor
        except Exception as ex:
            logger.exception(ex)

    def get_all_links(self, url):
        '''Get all links from an URL'''
        try:
            filter_ = {'url': url} # query with URL
            cursor = self._links_col.find(filter_)
            queried_result = list(cursor) 
            links = list()
            for result in queried_result:
                links.append(result['link'])
            n_links = len(links)
            result = {'n_links': n_links, 'links': links}
            return result 
        except Exception as ex:
            logger.exception(ex)
        return None
    
    # generate a link from an url
    def _generate_link(self, url):
        '''Generate a link from an UEL'''
        shortened_link = str(uuid4())
        return shortened_link

    def create_link(self, url):
        '''Create a new link from an URL and insert into database'''
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
                # update the "urls" collection: increment "n_links"
                updated_url_doc = { '$set': {'n_links':old_url['n_links']+1, 'last_updated_at': int(time.time())}}
                self._urls_col.update_one(filter_, updated_url_doc)
            else:
                new_links_doc = {'url':url, 'nonce':0, 'link':link, 'view': 0} # new document for the "links" collection
                new_urls_doc = {'url':url, 'n_links':1, 'view_logs': {}, 'last_updated_at':int(time.time())} # new document for the "links" collection
                self._links_col.insert_one(new_links_doc)
                self._urls_col.insert_one(new_urls_doc)
            return link
        except Exception as ex:
            logger.exception(ex) 

    def update_link(self, link, updated_link_doc):
        '''Update a document in the "links" collection'''
        try:
            self._links_col.update_one({'link':link}, updated_link_doc) 
        except Exception as ex:
            logger.exception(ex)
            logger.warning(f'Some thing went wrong with updating link {link}')

    def get_original_url(self, link):
        ''' From a link, gets the URL and the infos about that URL'''
        try:
            link_filter = {'link': link}
            link_doc = self._links_col.find_one(link_filter, {'url':1, 'nonce': 1, 'view': 1}) # find one instance of the input link
            if link_doc != None:
                # Return the URL and the nonce of the input link 
                result = {'url': link_doc['url'], 'nonce': link_doc['nonce'], 'view':link_doc['view']}
                return result 
            else:
                return None  
        except Exception as ex:
            logger.exception(ex) 

    def get_url(self, url):
        '''Get a document from the "urls" collection''' 
        try:
            filter_ = {'url': url}
            cursor = self._urls_col.find_one(filter_)
            return cursor
        except Exception as ex:
            logger.exception(ex)

    def update_url(self, url, updated_url_doc):
        '''Update a document from the "urls" collection''' 
        try:
            current_time = int(time.time())
            self._urls_col.update_one({'url':url}, updated_url_doc)
            self._urls_col.update_one({'url':url}, {'$set': {'last_updated_at': current_time}})
        except Exception as ex:
            logger.exception(ex)
            logger.warning(f'Some thing went wrong with updating url {url}')

            