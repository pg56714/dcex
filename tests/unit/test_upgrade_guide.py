"""Keep the bilingual upgrade guide complete for public consent requirements."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
GUIDES = [ROOT / 'docs/upgrade-0.34.0.md', ROOT / 'docs/upgrade-0.34.0.zh_tw.md']


def consent_methods():
    names = set()
    for path in (ROOT / 'dcex').rglob('*.py'):
        parts = path.relative_to(ROOT / 'dcex').parts
        if len(parts) < 2 or parts[0] in {'async_support', 'ws', 'base', 'utils', 'product_table'}:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding='utf8'))):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                args = {arg.arg for arg in node.args.args + node.args.kwonlyargs}
                if args & {'confirm', 'all_symbols'}:
                    names.add(parts[0] + '.' + node.name)
    return names


@pytest.mark.parametrize('path', GUIDES, ids=lambda p: p.name)
def test_upgrade_guides_cover_every_public_consent_method(path):
    text = path.read_text(encoding='utf8')
    assert all(f'`{name}`' in text for name in consent_methods())
    assert all(term in text for term in ['margin_mode', 'position_side', 'leverage', 'set_dcp', 'result["ok"]', 'result["errors"]', 'float/bool', 'subaccountId', 'depth=5', 'ModuleNotFoundError'])
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if not target.startswith('https://'):
            assert (path.parent / target.split('#')[0]).is_file(), target


@pytest.mark.parametrize('readme,link', [
    ('README.md', 'docs/upgrade-0.34.0.md'),
    ('README.zh_tw.md', 'docs/upgrade-0.34.0.zh_tw.md'),
    ('crates/dcex/README.md', '../../docs/upgrade-0.34.0.md'),
    ('crates/dcex/README.zh_tw.md', '../../docs/upgrade-0.34.0.zh_tw.md'),
])
def test_readmes_link_the_matching_upgrade_guide(readme, link):
    path = ROOT / readme
    assert f']({link})' in path.read_text(encoding='utf8')
    assert (path.parent / link).is_file()
