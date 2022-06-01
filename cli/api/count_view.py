# cli/api/count_view_logs.py
# main code for the API
import time
import click

from app.databases.mongodb import MongoDB
from app.utils.logger_utils import get_logger

logger = get_logger('Count view logs')

_db = MongoDB()

def _get_url_views(url):
    '''Get the number of views from an URL, by adding the views from individual links'''
    url_view = 0
    links = _db.get_all_links(url)['links'] # get all links belong to that url
    for link in links:
        link_views = _db.get_link(link)['view'] # get "view" of each link
        url_view += link_views # then add to the "view" of the URL
    return url_view

@click.command()
@click.option('--minute', '-m', default= 5, help='Time interval (in minutes) to update view logs')
def count_view(minute):
    '''Calculate the view_logs of an URL'''
    urls = _db.get_all_urls()
    while True:
        try:
            urls_views_before = dict()
            urls_views_after = dict()
            # calculate url in the past
            for url in urls:
                urls_views_before[url] = _get_url_views(url)
            # calculate url view after sleep
            time.sleep(minute * 60)
            for url in urls:
                urls_views_after[url] = _get_url_views(url)
            # update the view log
            current_time = int(time.time())
            for url in urls:
                cursor = _db.get_url(url)
                if cursor == None:
                    view_logs = dict()
                else:
                    view_logs = cursor['view_logs']
                # The view is calculated by subtracting the old url_view from the new url_view 
                view_logs[str(current_time)] = urls_views_after[url] - urls_views_before[url]
                updated_view_logs = {'$set': {'view_logs': view_logs}}
                _db.update_url(url, updated_view_logs)
            logger.info(f'Update view_logs at {current_time}')
        except Exception as ex:
            logger.exception(ex)