"""Validate static pages, translation freshness, navigation, and contact links."""
import runpy
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


generator = runpy.run_path(str(ROOT / 'scripts/build-languages.py'))
english = (ROOT / 'en/index.html').read_text(encoding='utf-8')
for lang, path, column in [('ru', 'index.html', 1), ('en', 'en/index.html', None), ('ru', 'ru/index.html', 1), ('ro', 'ro/index.html', 2)]:
    source = (ROOT / path).read_text(encoding='utf-8')
    if column:
        translator = generator['Translator'](lang, column)
        translator.feed(english)
        translator.close()
        assert source == ''.join(translator.output), f'{path}: regenerate translations'
    page = Page(source)
    ids = [a['id'] for _, a in page.elements if 'id' in a]
    assert len(ids) == len(set(ids)), f'{path}: duplicate IDs'
    assert next(a['lang'] for t, a in page.elements if t == 'html') == lang
    links = [a for t, a in page.elements if t == 'a']
    assert sum(a.get('href') == 'tel:+37369089897' for a in links) == 1
    assert any(a.get('href') == 'mailto:aliona.krasnova1980@gmail.com' for a in links)
    assert sum('photos.google.com' in a.get('href', '') for a in links) == 7
    active = [a for a in links if a.get('aria-current') == 'page']
    assert len(active) == 1 and active[0]['hreflang'] == lang
    assert {a['hreflang'] for a in links if 'hreflang' in a} == {'en', 'ru', 'ro'}
    assert {a['hreflang']: a['href'] for a in links if 'hreflang' in a} == {'ru': '/', 'ro': '/ro/', 'en': '/en/'}
    assert not any(t == 'script' for t, _ in page.elements)
    for tag, attrs in page.elements:
        if tag == 'img':
            assert 'alt' in attrs
        for key in ('href', 'src'):
            value = attrs.get(key, '')
            if value.startswith('#'):
                assert value[1:] in ids, f'{path}: missing anchor {value}'
            elif value.startswith('/'):
                local = ROOT / urlsplit(value).path.lstrip('/')
                if local.is_dir():
                    local /= 'index.html'
                assert local.is_file(), f'{path}: missing file {value}'
    print(f'PASS {path}: language, translations, contacts, albums, anchors, and local assets')
