from urllib.parse import urlparse


def get_domain(url):
    get_domain = urlparse(url).netloc
    return get_domain

def get_origin(url):
    get_origin = urlparse(url).scheme + "://" + urlparse(url).netloc
    return get_origin
    
def get_url_without_last_slash(url):
    if url[-1] == "/":
        return url[:-1]
    return url

# remove last part of url after slash and return url
def get_url_without_last_part(url):
    return url.rsplit('/', 1)[0]

def get_url_without_first_part(url):
    return url.split('/', 1)[1]

def get_url_without_first_and_last_part(url):
    return get_url_without_last_part(get_url_without_first_part(url))

def get_last_part_from_url(url):
    return url.rsplit('/', 1)[1]

def get_part_before_last_from_url(url):
    url_without_last_part = get_url_without_last_part(url)
    return get_last_part_from_url(url_without_last_part)