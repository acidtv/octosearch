import json
import base64
import hmac

PROTOCOL = 'octosearch'
VERSION = 'v1'


def open(url, secret):
    """Create a signed octosearch:// open url"""
    return _url('open', {'url': url}, secret)


def register(url, secret):
    """Create a octosearch:// register url"""
    return _url('register', {'url': url, 'secret': secret})


def _url(action, payload, secret=None):
    """This function does the heavy lifting of creating a octosearch:// url"""
    # Serialize payload to json and base64 encode it
    json_payload = json.dumps(payload).encode()
    base64_payload = base64.b64encode(json_payload)

    url = PROTOCOL + r"://" + VERSION + "/" + action + "/" + base64_payload.decode()

    if secret:
        # Sign with hmac
        h = hmac.new(secret.encode(), base64_payload, digestmod='sha256')
        url = url + "/" + h.hexdigest()

    return url
