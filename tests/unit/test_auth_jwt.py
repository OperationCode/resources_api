from app.api.auth import authenticate
from app.models import Key
from datetime import datetime, timedelta
from jwt import encode
from unittest.mock import patch

BOGUS_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDEfuFA5sEB92QE
86hggQBRTqqCb3ADOAg4vjXDJ+CXhqwASVD1ORnqr6B+tvFDOgmmR3QKu4rmn159
hJOfF6xfKQPD3yJKWKwHniA7n3ISBhanbOtYHJmABbdbTucmxrsrJsp1uHQtO1Y5
pW9dWXPGCfzvNAXL5xnFBgqBHEVXm75ZuYHpMYaIOtUWP8MAnFgZFqMQcPUcLmPM
n5DMA1jHStxVrG8b0Bolo39zJYG+JnQEFlpw3IYjcvV0gDG45LSbjFv4a9d2soh7
PkPZ+OTv0NNAH6zl9fTEtS29ZumZ8n7Ies+T4noQJQozpG0dy4MwyMakfbIFDxFI
UgxMQDNRAgMBAAECggEAc1I/4zZKqlvGIL3b4R90z0NLARhj9g+pi5ves7Wws11/
jv94eyNTGZCPsi6uNBVY2nTvHulooOeBrkrj1KgxKvxIUGmhl16pQCNGqZdvfDKE
kyhyixjl4eP486bANNrHuJCgnCxwSqebeGOmk3PPZbgw8TZn/H6aei6Mda/g5oPi
2zfyvG+DyrqWrOiNESfGRs7BxVZn7/jJfAXnQDDkDuvoEDyjupMMgR3l9xY6rOZP
+aVL0qJizt5H9BLtHYweoU2GRqnyVnsBNyL3AXpqAOaRFJpZXoXn5mJb/fZFhYE1
f7+dwkBq1lxstq85GmZNcK9IZJ6mGXlSxIBJ/hovkQKBgQDpyLKm6wM7zCShwljj
2CA1RRCkxW9skRchZLoyFoOSFDZLa0Y7Xl1SjmU1y02+NsTRzvWjmtd1vQozUDkc
MvgM1fjdo4D8XA48RG5K7l1/56CPk/0QIGVYaDWlv0nfGwfPLvUJvptBtdLzyXCi
9TurctJ7Rox/WUSr2oGR4W9o/QKBgQDXKw/hhQZLyOIYvBbi7WBTUW/7dP70rT5K
1VIOdcNDh4FhiEulWiqC0pA0w2qSOOIyZd2zdkaFOFMAfYnoEWF4HSNcOfXMQ/wp
iWcA7Jv2voFwHkxiUK51gM21BfV0v+YKSotwqsRLWYv997J/Hg5xWaDoRStRWm2N
t6Vs78895QKBgQCwSMA+EXSMwLDWsP/qPux6fqvAM4iDqxxv985XOpbXrhoK4MdC
uTNRr0IuQDFNP2tGcfLT/Ux+4Z8xdkq6MszMkQRpzILUyG2LkGZCZl9mtThjS8pF
QMhq05mwc/+2FmHbHqNzR6E2+W4qmjkvCBCIhbqlbls/JAceN1QAtqcV2QKBgGHh
d/76Wavd/WSNI8glff1I/a0hQt4hdUXrlsF3NtWgbe3lZ6wXwWDz0p/+CZvs/pE4
n8sE0f3GapO9iB+m0HUopC5PO46pmqt2kwHroON1NELBtbO/yi0v4+QmisuKhGZI
FPiy5kr0uGdW579F+AH+aOFgnd0LSuz+DuXojZk1AoGBANLTm9oujykwW/4lSBep
O8rd/SNpeaz4BwZiNg6yRNImeyQMQFqQUEoDohEhHkd9Y7wNW21I7jR+VA7qPWTk
lgfxGIOU16EyMffrBIIbpH+YMABG+MAxKrGbRVXr24VU6zAZqE9mEvujSYxnZW/C
DJQHadGUXFAGcrQKpxHv7QA0
-----END PRIVATE KEY-----"""

FAKE_EMAIL = 'test@example.org'
FAKE_APIKEY = 'abcdef1234567890'
SECRET_KEY = open(".dev/dev-jwt-key").read()
EXP = datetime.utcnow() + timedelta(seconds=10)
delta = timedelta(seconds=-11)

GOOD_AUTH = "Bearer " + encode({'email': FAKE_EMAIL, 'exp': EXP},
                               SECRET_KEY, algorithm='RS256')
BAD_AUTH = "Bearer " + encode({'email': FAKE_EMAIL, 'exp': EXP},
                              BOGUS_KEY, algorithm='RS256')
EXP_AUTH = "Bearer " + encode({'email': FAKE_EMAIL, 'exp': EXP + delta},
                              SECRET_KEY, algorithm='RS256')
NO_EXP_AUTH = "Bearer " + encode({'email': FAKE_EMAIL},
                                 SECRET_KEY, algorithm='RS256')


def create_fake_key(session, **kwargs):
    kwargs['email'] = kwargs.get('email', FAKE_EMAIL)
    kwargs['apikey'] = kwargs.get('apikey', FAKE_APIKEY)
    key = Key(**kwargs)
    session.add(key)
    session.commit()
    return key


def test_missing_auth_header(module_client):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {}
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_empty_auth_header(module_client):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': ''
        }
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_invalid_auth_header(module_client):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': 'bogus'
        }
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_no_expiration(module_client):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': NO_EXP_AUTH
        }
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_expired_token(module_client):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': EXP_AUTH
        }
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_invalid_signature_failure(module_client):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': BAD_AUTH
        }
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_authenticate_success(module_client, function_empty_db):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': GOOD_AUTH
        }
        result = wrapper()

    # Assert
    assert result == 1


def test_denied_apikey(module_client, function_empty_db):
    # Arrange
    def callback(*args, **kwargs):
        return 1
    create_fake_key(function_empty_db.session, denied=True)

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'authorization': GOOD_AUTH
        }
        result = wrapper()

    # Assert
    assert result[1] == 401
