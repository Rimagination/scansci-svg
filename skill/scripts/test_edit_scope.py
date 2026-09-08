"""Small, dependency-free regression checks for local-edit scope."""
import tempfile
from pathlib import Path
from check_edit_scope import compare

BASE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<defs><linearGradient id="paint"><stop stop-color="red"/></linearGradient></defs>
<g id="building"><g id="window"><rect id="glass" width="20" height="20" fill="url(#paint)"/></g>
<path id="roof" d="M0 0L80 0L40 20Z"/><text id="label">A B</text></g></svg>'''

def main():
    with tempfile.TemporaryDirectory(prefix='scansci-scope-') as directory:
        before, after = Path(directory)/'before.svg', Path(directory)/'after.svg'
        before.write_text(BASE, encoding='utf-8')
        def run(svg, allow=('window',), original=BASE):
            before.write_text(original, encoding='utf-8')
            after.write_text(svg, encoding='utf-8')
            return compare(before, after, list(allow))
        edited = BASE.replace('width="20"', 'width="18"')
        r = run(edited)
        assert r['scope_check_passed'] and r['target_changed']['window']
        assert r['target_verified'] is None
        assert run(BASE)['target_changed']['window'] is False
        assert not run(edited.replace('id="roof"', 'id="roof" fill="blue"'))['scope_check_passed']
        assert not run(edited.replace('id="building"', 'id="building" transform="translate(2)"'))['scope_check_passed']
        assert not run(edited.replace('stop-color="red"', 'stop-color="blue"'))['scope_check_passed']
        assert not run(edited.replace('A B', 'AB'))['scope_check_passed']
        assert not run(edited.replace('id="window"', 'id="other"'))['scope_check_passed']
        assert not run(edited.replace('id="roof"', 'id="window"'))['scope_check_passed']
        assert not run('<svg>')['scope_check_passed']
        assert not run(edited, allow=[])['scope_check_passed']
        root_id = BASE.replace('<svg ', '<svg id="scene" ')
        assert not run(root_id, allow=['scene'], original=root_id)['scope_check_passed']
        shared = BASE.replace('</svg>', '<use href="#glass" x="50"/></svg>')
        assert not run(shared.replace('width="20"', 'width="18"'), original=shared)['scope_check_passed']
        css = BASE.replace('</svg>', '<style>#window + path {fill: red}</style></svg>')
        assert not run(css.replace('width="20"', 'width="18"'), original=css)['scope_check_passed']
        assert run(edited.replace('\n', '\n  '))['scope_check_passed']
        # A defs block inside the allowed group must still be protected.
        nested = BASE.replace('<g id="window">', '<g id="window"><defs><linearGradient id="local"><stop stop-color="pink"/></linearGradient></defs>')
        assert not run(nested.replace('pink', 'orange'), original=nested)['scope_check_passed']
    print('PASS: 15 scope checks (including unchanged target, malformed SVG, shared references and CSS)')

if __name__ == '__main__':
    main()
