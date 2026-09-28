"""Offline signing and validation for options kill-switch and MMP controls."""

# ruff: noqa: ANN001, ANN201, D103
import pytest

from tests.unit.test_binance_risk_endpoints import test_risk_wire as assert_risk_wire

CASES = [
    ("get_options_cancel_countdown", {}, "GET", "/eapi/v1/countdownCancelAll", {}),
    (
        "set_options_cancel_countdown",
        {"underlying": "BTCUSDT", "countdown_time": 5000},
        "POST",
        "/eapi/v1/countdownCancelAll",
        {"underlying": "BTCUSDT", "countdownTime": "5000"},
    ),
    (
        "set_options_cancel_countdown",
        {"underlying": "BTCUSDT", "countdown_time": 0},
        "POST",
        "/eapi/v1/countdownCancelAll",
        {"underlying": "BTCUSDT", "countdownTime": "0"},
    ),
    (
        "send_options_cancel_heartbeat",
        {"underlyings": ["BTCUSDT", "ETHUSDT"]},
        "POST",
        "/eapi/v1/countdownCancelAllHeartBeat",
        {"underlyings": "BTCUSDT,ETHUSDT"},
    ),
    (
        "get_options_mmp_config",
        {"underlying": "BTCUSDT"},
        "GET",
        "/eapi/v1/mmp",
        {"underlying": "BTCUSDT"},
    ),
    (
        "reset_options_mmp",
        {"underlying": "BTCUSDT"},
        "POST",
        "/eapi/v1/mmpReset",
        {"underlying": "BTCUSDT"},
    ),
    (
        "set_options_mmp_config",
        {
            "underlying": "BTCUSDT",
            "window_time": 5000,
            "frozen_time": 0,
            "qty_limit": "1",
            "delta_limit": "2.5",
        },
        "POST",
        "/eapi/v1/mmpSet",
        {
            "underlying": "BTCUSDT",
            "windowTimeInMilliseconds": "5000",
            "frozenTimeInMilliseconds": "0",
            "qtyLimit": "1",
            "deltaLimit": "2.5",
        },
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method,kwargs,verb,path,expected", CASES)
async def test_options_controls(asynchronous, method, kwargs, verb, path, expected):
    await assert_risk_wire(asynchronous, method, kwargs, verb, path, expected, True, False)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "method,kwargs",
    [
        ("set_options_cancel_countdown", {"underlying": "BTCUSDT", "countdown_time": 4999}),
        ("set_options_cancel_countdown", {"underlying": "BTCUSDT", "countdown_time": -1}),
        ("send_options_cancel_heartbeat", {"underlyings": []}),
        ("send_options_cancel_heartbeat", {"underlyings": ["BTCUSDT", " "]}),
        (
            "set_options_mmp_config",
            {
                "underlying": "BTCUSDT",
                "window_time": 5001,
                "frozen_time": 0,
                "qty_limit": "1",
                "delta_limit": "2.5",
            },
        ),
    ],
)
async def test_options_controls_reject_before_transport(asynchronous, method, kwargs):
    from tests.unit.test_binance_risk_endpoints import test_invalid_risk_parameters

    await test_invalid_risk_parameters(asynchronous, method, kwargs)
