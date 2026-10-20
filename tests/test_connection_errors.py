from types import SimpleNamespace
from unittest.mock import Mock
import asyncio
import socket
import aiohttp
import pytest
from custom_components.casvi.api import CasviClient, CasviError


@pytest.mark.asyncio
@pytest.mark.parametrize('error,expected', [
    (asyncio.TimeoutError(), 'timed out'),
    (aiohttp.ClientConnectorError(SimpleNamespace(host='intranet.casvi.es', port=443, ssl=True), socket.gaierror(-2, 'DNS failed')), 'DNS'),
    (aiohttp.ClientConnectionError('private data'), 'ClientConnectionError'),
])
async def test_connection_diagnostics(error, expected):
    client = CasviClient('private-user', 'private-password')
    client._session = SimpleNamespace(request=Mock(side_effect=error))
    with pytest.raises(CasviError) as caught:
        await client._request('/controles/test.php', {'password': 'private-password'})
    assert expected in str(caught.value)
    assert 'private' not in str(caught.value)
