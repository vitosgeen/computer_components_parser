from urllib.parse import urlparse


def get_domain(url):
    get_domain = urlparse(url).netloc
    return get_domain

def get_origin(url):
    get_origin = urlparse(url).scheme + "://" + urlparse(url).netloc
    return get_origin
    