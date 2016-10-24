import requests
import urlparse
import re

from sesshu import constant


def validate(uri):
    ''' Validates that the input parameter is 'safe'. '''
    p = urlparse.urlparse(uri)
    if p.scheme not in ['http', 'https']:
        raise AttributeError('URL scheme not supported.')
    if p.netloc == '':
        raise AttributeError('Blank location not supported.')


def fetch(uri):
    ''' Attempts to fetch and process site robots for the given domain. '''
    try:
        response = requests.get(
            urlparse.urljoin(uri, '/robots.txt'),
            headers={
                'User-Agent': constant.HTTP_USER_AGENT
            }
        )
    except requests.exceptions.RequestException:
        return None

    # Ensure the request was successful and the response has data.
    if response.status_code is not 200 or len(response.text) < 1:
        return None

    robots = filter(None, response.text.splitlines())
    if robots is None or len(robots) < 1:
        return None

    # Filter entires to only 'Allow' and 'Disallow'.
    paths = []
    for robot in robots:
        (candidate, count) = re.subn(
            r'^(dis)*allow: ', '', robot, flags=re.IGNORECASE)

        # If an 'Allow' or 'Disallow' line strip out any comments and store.
        if count > 0:
            (stripped, count) = re.subn(r'\s*\#.*$', '', candidate)
            paths.append(stripped)

    return paths
