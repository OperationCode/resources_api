import pytest
from tests import conftest

def test_internal_server_error_handler(module_client, module_db, fake_error):
    client = module_client

    self.assertRaises(Exception, client.get('api/v1/resources'))
