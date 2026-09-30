"""Existing positional slots must never acquire a different meaning."""

import ast
import importlib
import inspect
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).parents[2]
BASELINE = json.loads((ROOT / 'tests/fixtures/python_signatures_0_33_0.json').read_text())
EXPORTS = json.loads((ROOT / 'tests/fixtures/python_public_exports_0_33_0.json').read_text())


def canonical(name):
    return name.replace('_', '').lower()


def public_callable(module, cls, name):
    imported = importlib.import_module(module)
    owner = getattr(imported, cls, None) if cls else imported
    if owner is None and (origin := EXPORTS['origins'].get(f'{module}:{cls}')):
        owner = getattr(importlib.import_module(origin[0]), origin[1], None)
    if owner is not None and hasattr(owner, name):
        return getattr(owner, name)
    # Account/trade methods moved to domain mixins; public Clients inherit them.
    client = importlib.import_module(module.rsplit('.', 1)[0] + '.client').Client
    return getattr(client, name)


def shifted_slots(old, new):
    return [(a, b) for a, b in zip(old, new) if canonical(a) != canonical(b)]


def test_all_existing_public_positional_slots_keep_their_meaning():
    errors = []
    for module, cls, name, signature in BASELINE['signatures'] + EXPORTS['constructors']:
        args = ast.parse(f'def f({signature}): pass').body[0].args
        old = [a.arg for a in args.posonlyargs + args.args if a.arg not in {'self', 'cls'}]
        function = public_callable(module, cls, name)
        if isinstance(function, property):
            function = function.fget
        new = [p.name for p in inspect.signature(function).parameters.values()
               if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.name not in {'self', 'cls'}]
        if changes := shifted_slots(old, new):
            errors.append((module, cls, name, changes))
    assert not errors, errors


def test_all_public_exports_keep_inherited_and_aliased_slots():
    errors = []
    for key, methods in EXPORTS['bindings'].items():
        module, cls = key.split(':')
        for name, signature in methods.items():
            function = public_callable(module, cls, name)
            new = [p.name for p in inspect.signature(function).parameters.values()
                   if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.name not in {'self', 'cls'}]
            if changed := shifted_slots(EXPORTS['positional'][signature], new):
                errors.append((key, name, changed))
    assert not errors, errors


CASES = [
    ('bingx', 'cancel_spot_order', ('BTC-USDT-SPOT', None, None, 'cid'), {'client_order_id': 'cid'}),
    ('bingx', 'get_spot_order', ('BTC-USDT-SPOT', None, None, 'cid'), {'client_order_id': 'cid'}),
    ('bingx', 'get_spot_orderbook_v2', ('BTC-USDT-SPOT', 100), {'depth': 100}),
    ('backpack', 'get_funding_payments', ('BTC-USDC-SWAP', 100), {'limit': 100}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize('async_client', [False, True])
@pytest.mark.parametrize('exchange,name,args,kwargs', CASES)
async def test_shifted_legacy_positional_calls_fail_before_dispatch(async_client, exchange, name, args, kwargs):
    prefix = 'dcex.async_support' if async_client else 'dcex'
    cls = importlib.import_module(f'{prefix}.{exchange}.client').Client
    instance = object.__new__(cls)
    sender = Mock(side_effect=AssertionError('must not dispatch'))
    instance._native_private = instance._native_public = sender
    with pytest.raises(TypeError):
        result = getattr(instance, name)(*args)
        if async_client:
            await result
    sender.assert_not_called()
    inspect.signature(getattr(instance, name)).bind(args[0], **kwargs)


def test_inserted_removed_and_reordered_slots_fail_compatibility_guard():
    assert shifted_slots(['symbol', 'account', 'limit'], ['symbol', 'limit'])
    assert shifted_slots(['symbol', 'limit'], ['symbol', 'depth', 'limit'])
    assert shifted_slots(['symbol', 'limit', 'offset'], ['symbol', 'offset', 'limit'])
    assert not shifted_slots(['orderId', 'recvWindow'], ['order_id', 'recv_window'])


@pytest.mark.parametrize('prefix', ['dcex', 'dcex.async_support'])
@pytest.mark.parametrize('exchange,old_args,keyword_args', [
    ('aster', (None, None, None, 'https://spot.example', 'https://futures.example', 10), {'timeout': 10}),
    ('kucoin', ('https://spot.example', 'https://futures.example', 'key'), {'api_key': 'key'}),
    ('lighter', ('https://api.example', 123), {'account_index': 123}),
])
def test_shifted_generated_constructors_reject_old_positions(prefix, exchange, old_args, keyword_args, monkeypatch):
    cls = importlib.import_module(f'{prefix}.{exchange}.client').AccountHTTP
    initialize = Mock(side_effect=AssertionError('must not initialize or send requests'))
    monkeypatch.setattr(cls, '__post_init__', initialize, raising=False)
    with pytest.raises(TypeError):
        cls(*old_args)
    initialize.assert_not_called()
    inspect.signature(cls).bind(**keyword_args)
