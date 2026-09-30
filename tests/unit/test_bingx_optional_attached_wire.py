"""Optional blank BingX TP/SL inputs are absent on every order transport."""

import importlib
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_round_seven_wire import close
from tests.unit.test_round_six_wire import invoke


@pytest.mark.asyncio
@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.parametrize('native', [False, True])
@pytest.mark.parametrize('method', ['place_swap_order', 'place_coin_swap_order', 'place_swap_batch_order'])
@pytest.mark.parametrize('blank', ['', '  \t', None])
async def test_blank_attached_order_keys_are_omitted(asynchronous, native, method, blank):
    prefix = 'dcex.async_support' if asynchronous else 'dcex'
    cls = importlib.import_module(f'{prefix}.bingx.client').Client
    with _http_server({'code': 0, 'data': {}}) as (base, received):
        client = cls(api_key='key', api_secret='secret', base_url=base, preload_product_table=False)
        if asynchronous:
            await client.async_init()
        try:
            if method == 'place_swap_batch_order':
                order = dict(symbol='BTC-USDT', side='BUY', type='MARKET', positionSide='LONG', quantity='1', takeProfit=blank, stopLoss=blank)
                args = {'batchOrders' if native else 'batch_orders': [order]}
            else:
                args = dict(product_symbol='BTC-USD' if 'coin' in method else 'BTC-USDT', side='BUY', type_='MARKET', quantity='1')
                args.update({'positionSide' if native else 'position_side': 'LONG'})
                if blank is not None or not native:
                    args.update({'takeProfit' if native else 'take_profit': blank, 'stopLoss' if native else 'stop_loss': blank})
            await invoke(client, method, args, native)
            request = received.get(timeout=10)
            payload = parse_qs(urlsplit(request['path']).query or request['body'], keep_blank_values=True)
            if method == 'place_swap_batch_order':
                payload = json.loads(payload['batchOrders'][0])[0]
            assert 'takeProfit' not in payload and 'stopLoss' not in payload, payload
        finally:
            await close(client)
