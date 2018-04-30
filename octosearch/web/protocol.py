import json
import base64
import hmac
import hashlib
import urllib.parse

PROTOCOL = 'octosearch'
VERSION = 'v1'


def open(url, secret, user):
    """Create a signed octosearch:// open url"""
    if (not user) or (not secret):
        raise Exception('User and secret cannot be empty')

    return _url('open', {'url': url}, secret, user)


def register(url, secret, user):
    """Create an octosearch:// register url"""
    if (not user) or (not secret):
        raise Exception('User and secret cannot be empty')

    return _url('register', {
        'url': url,
        'secret': _user_secret(user, secret)
    })


def _user_secret(user, secret):
    """Hash secret with user to generate a unique per-user id"""
    return hashlib.sha256(secret.encode() + b':' + user.encode()).hexdigest()


def _url(action, payload, secret=None, user=None):
    """This function does the heavy lifting of creating an octosearch:// url"""
    # Serialize payload to json and base64 encode it
    json_payload = json.dumps(payload).encode()
    base64_payload = base64.b64encode(json_payload)

    url = PROTOCOL + r"://" + VERSION + "/" + action + "/" + base64_payload.decode()

    if secret:
        # Sign with hmac
        if not user:
            raise Exception('User cannot be empty if url is to be signed with secret')

        h = hmac.new(
            _user_secret(user, secret).encode(),
            base64_payload,
            digestmod='sha256'
        )

        url = url + "/" + h.hexdigest()

    return url


def use_octosearch_protocol(url):
    browser_protocols = ['http', 'https', 'ftp']

    if urllib.parse.urlparse(url).scheme in browser_protocols:
        return False

    return True

