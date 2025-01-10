from urllib.parse import urlparse


def get_domain(url):
    get_domain = urlparse(url).netloc
    return get_domain