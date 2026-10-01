"""Regenerate fully static RU/RO pages from the English homepage (stdlib only)."""
import json
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROWS = json.loads((ROOT / 'translations.json').read_text(encoding='utf-8'))
assert len({row[0] for row in ROWS}) == len(ROWS), 'Duplicate translation keys'


class Translator(HTMLParser):
    def __init__(self, language, column):
        super().__init__(convert_charrefs=True)
        self.language = language
        self.translations = {row[0]: row[column] for row in ROWS}
        self.output = []

    def translate(self, value):
        key = value.strip()
        if not key or not any(c.isalpha() for c in key):
            return value
        if key not in self.translations:
            raise ValueError(f'Missing {self.language} translation: {key!r}')
        return value.replace(key, self.translations[key], 1)

    def tag(self, tag, attrs, closing):
        values = dict(attrs)
        result = []
        for key, value in attrs:
            if tag == 'html' and key == 'lang':
                value = self.language
            elif key in ('alt', 'aria-label') or (tag == 'meta' and values.get('name') == 'description' and key == 'content'):
                value = self.translate(value)
            elif tag == 'link' and values.get('rel') == 'canonical' and key == 'href':
                value = f'https://elenakrasnova-dolls.github.io/{self.language}/'
            elif key == 'aria-current' and values.get('hreflang'):
                continue
            result.append(key if value is None else f'{key}="{escape(value, quote=True)}"')
        if tag == 'a' and values.get('hreflang') == self.language:
            result.append('aria-current="page"')
        self.output.append('<' + tag + (' ' if result else '') + ' '.join(result) + closing)

    def handle_starttag(self, tag, attrs):
        self.tag(tag, attrs, '>')

    def handle_startendtag(self, tag, attrs):
        self.tag(tag, attrs, '/>')

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')

    def handle_data(self, data):
        self.output.append(escape(self.translate(data), quote=False))

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')

    def handle_comment(self, data):
        self.output.append(f'<!--{data}-->')


if __name__ == '__main__':
    source = (ROOT / 'index.html').read_text(encoding='utf-8')
    for language, column in [('ru', 1), ('ro', 2)]:
        parser = Translator(language, column)
        parser.feed(source)
        parser.close()
        destination = ROOT / language / 'index.html'
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(''.join(parser.output), encoding='utf-8')
        print(f'Generated {language}/index.html')
