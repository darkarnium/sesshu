import requests
import urlparse
import bs4
import re

from sesshu import constant


def validate(uri):
    ''' Validates that the input uri is 'safe'. '''
    p = urlparse.urlparse(uri)
    if p.scheme not in ['http', 'https']:
        raise AttributeError('URL scheme not supported.')
    if p.netloc == '':
        raise AttributeError('Blank location not supported.')


def fetch(uri):
    ''' Attempts to fetch a list of Javascript includes from the target. '''
    try:
        response = requests.get(
            uri,
            headers={
                'User-Agent': constant.HTTP_USER_AGENT
            }
        )
    except requests.exceptions.RequestException:
        return None

    # Ensure the request was successful and the response has data.
    if response.status_code is not 200 or len(response.text) < 1:
        return None

    # Use bs4 to make things more manageable.
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    sources = []

    # Locate all 'script' tags which have 'src' attributes, and store.
    for script in soup.find_all('script'):
        source = script.get('src')
        if source is not None:
            sources.append(source)

    return sources
