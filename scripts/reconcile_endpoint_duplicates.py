"""Reconcile reviewed duplicate inventory rows without hiding unimplemented endpoints."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    path = ROOT / "docs/endpoint-coverage-ledger.json"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    rows = {r["row"]: r for r in ledger["rows"]}
    aliases = {3736: 2952, 4114: 2659}
    bybit = [
        706,
        701,
        702,
        705,
        700,
        703,
        707,
        704,
        695,
        693,
        688,
        694,
        692,
        696,
        689,
        687,
        691,
        690,
        697,
        708,
        708,
        698,
        698,
        698,
        708,
        708,
        708,
        699,
    ]
    aliases.update(zip(range(4513, 4541), bybit, strict=True))
    for number in range(4132, 4157):
        channel = rows[number]["channel"]
        matches = [
            r
            for r in rows.values()
            if r["exchange"] == "hyperliquid"
            and r["kind"] == "WS"
            and r["status"] == "protocol"
            and channel in r["endpoint"].split(" / ")
        ]
        if len(matches) == 1:
            aliases[number] = matches[0]["row"]
    for start, end, targets in [
        (3693, 3715, [3177, 3178, 3179, 3180]),
        (4826, 4844, [3115, 3116, 3117]),
    ]:
        for number in range(start, end):
            channel = rows[number]["channel"]
            for target in targets:
                topics = rows[target]["endpoint"].split(": ", 1)[-1].split(" (", 1)[0].split(", ")
                if channel in topics:
                    aliases[number] = target
                    break
    lighter = [
        2770,
        2771,
        2772,
        2774,
        2775,
        2775,
        2777,
        2778,
        2777,
        2779,
        2779,
        2776,
        2779,
        2779,
        2779,
        2778,
        2779,
        2779,
        2773,
        2779,
        2779,
        2780,
    ]
    aliases.update(zip(range(4687, 4709), lighter, strict=True))
    aliases.update(
        {
            4080: 3041,
            4081: 3040,
            4085: 3040,
            4086: 3040,
            4087: 3040,
            4088: 3040,
            4089: 3040,
            4090: 3040,
            4091: 3040,
            4092: 3042,
            4166: 3040,
            4167: 3040,
            4542: 3040,
        }
    )
    aliases[3714] = 3180
    # Same topic and API version, with exact per-topic official source URLs.
    for row in rows.values():
        if (
            row["status"] != "pending"
            or row["kind"] != "WS"
            or row["exchange"] not in {"bitget", "kraken", "mexc"}
        ):
            continue
        matches = [
            r
            for r in rows.values()
            if r["exchange"] == row["exchange"]
            and r["status"] == "protocol"
            and r.get("official_source") == row["official_source"]
        ]
        if len(matches) == 1:
            aliases[row["row"]] = matches[0]["row"]
    aliases.update(
        {
            4470: 1813,
            4488: 1802,
            4489: 1803,
            4491: 1817,
            4492: 1818,
            4493: 1818,
            4494: 1818,
            4495: 1818,
            4496: 1817,
            4497: 1817,
            4498: 1818,
            4499: 1817,
            4501: 1817,
            4502: 1817,
            4503: 1814,
            4504: 1814,
            4505: 1814,
            4506: 1814,
            4507: 1814,
            4750: 2270,
            4723: 2263,
            4748: 2276,
        }
    )
    bingx = [
        1981,
        1977,
        1980,
        1980,
        1975,
        1980,
        1978,
        1979,
        1983,
        1984,
        1977,
        1978,
        1976,
        1979,
        1980,
        1980,
        1975,
        1981,
        1980,
    ]
    aliases.update(zip(range(4449, 4468), bingx, strict=True))
    for number in (
        list(range(4177, 4191))
        + list(range(4197, 4211))
        + list(range(4247, 4258))
        + list(range(4260, 4271))
    ):
        aliases[number] = 2989
    for number in list(range(4191, 4196)) + list(range(4211, 4218)) + [4259, 4272]:
        aliases[number] = 2990
    # Match the API family, not the SDK function name shared by distinct markets.
    for first, last, target in [
        (4287, 4297, 13),
        (4297, 4316, 4),
        (4316, 4326, 5),
        (4326, 4344, 12),
        (4344, 4364, 3),
        (4364, 4415, 11),
        (4415, 4419, 7),
        (4419, 4434, 1),
        (4434, 4441, 10),
    ]:
        aliases.update(dict.fromkeys(range(first, last), target))
    for row in rows.values():
        if row["status"] != "pending" or row["kind"] != "REST":
            continue
        keys = ("exchange", "http_method", "path", "host", "actions", "operation")
        matches = [
            r
            for r in rows.values()
            if r["status"] == "implemented" and all(r.get(k) == row.get(k) for k in keys)
        ]
        if matches:
            aliases[row["row"]] = min(r["row"] for r in matches)
    for number, target in aliases.items():
        row, original = rows[number], rows[target]
        # Explicit migration decisions supersede this historical grouping pass.
        if row.get("replacement_routes") or row["status"] == "unavailable":
            continue
        if original["status"] not in {"protocol", "implemented"}:
            raise ValueError(f"Duplicate {number} has unimplemented target {target}")
        row.update(
            status="superseded",
            superseded_by=target,
            note=(
                f"Duplicate of row {target}; "
                "the existing operation covers this official inventory entry."
            ),
            evidence=original["evidence"],
        )
        if row.get("channel"):
            original["channels"] = sorted(set(original.get("channels", [])) | {row["channel"]})
        original["official_sources"] = sorted(
            set(original.get("official_sources", [])) | {row["official_source"]}
        )
    ledger["counts"] = dict(Counter(r["status"] for r in rows.values()))
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reconciled {len(aliases)} duplicates; {ledger['counts'].get('pending', 0)} pending.")


if __name__ == "__main__":
    main()
