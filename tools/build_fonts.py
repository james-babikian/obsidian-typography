"""Trim the snippet fonts to Latin-script languages, keep every OpenType feature and variable axis, and write the snippet.

Every font comes from fonts/ (SIL OFL). The snippet is one file: the rules and settings of snippets/typography.css,
then the font settings and rules of snippets/typography-fonts.head.css, then the @font-face rules. Output goes into
private/snippets/ (git-ignored, because it is built).
Usage: py -I tools/build_fonts.py
"""
import base64, pathlib, re, sys
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'private'

# All Latin-script languages: Basic Latin to Latin Extended-B, IPA modifiers, combining marks, Latin Extended
# Additional (Vietnamese), punctuation, super/subscripts, currency, letterlike symbols, number forms, arrows (Obsidian's
# footnote back-link uses U+21A9), minus and fraction slash, Latin Extended-C and -D, f-ligatures.
UNICODES = ('U+0000-024F,U+0259,U+02B0-02FF,U+0300-036F,U+1E00-1EFF,U+2000-206F,U+2070-209F,U+20A0-20CF,'
            'U+2100-218F,U+2190-21FF,U+2212-2215,U+2C60-2C7F,U+A720-A7FF,U+FB00-FB06,U+FEFF,U+FFFD')


def faces():
    """Yield (source path, CSS family, CSS style, CSS weight) for every face in the snippet."""
    alg = ROOT / 'fonts' / 'alegreya'
    yield alg / 'Alegreya-Roman.ttf', 'Alegreya Full', 'normal', '400 900'
    yield alg / 'Alegreya-Italic.ttf', 'Alegreya Full', 'italic', '400 900'
    sans = ROOT / 'fonts' / 'alegreya-sans'
    for name, style, weight in [('Regular', 'normal', '400'), ('Italic', 'italic', '400'), ('Medium', 'normal', '500'), ('Bold', 'normal', '700')]:
        yield sans / f'AlegreyaSans-{name}.ttf', 'Alegreya Sans Full', style, weight
    for name, style, weight in [('Regular', 'normal', '400'), ('Italic', 'italic', '400'), ('Bold', 'normal', '700'), ('BoldItalic', 'italic', '700')]:
        yield ROOT / 'fonts' / 'courier-prime' / f'CourierPrime-{name}.ttf', 'Courier Prime Full', style, weight
    # iA Writer Mono reserves the names "iA Writer" and "Plex" (SIL OFL); the trimmed copy is renamed Quill Mono.
    for name, style, weight in [('Regular', 'normal', '400'), ('Italic', 'italic', '400'), ('Bold', 'normal', '700'), ('BoldItalic', 'italic', '700')]:
        yield ROOT / 'fonts' / 'ia-writer-mono' / f'iAWriterMonoS-{name}.ttf', 'Quill Mono Full', style, weight
    yield ROOT / 'fonts' / 'jetbrains-mono' / 'JetBrainsMono-Roman.ttf', 'JetBrains Mono Full', 'normal', '100 800'
    yield ROOT / 'fonts' / 'jetbrains-mono' / 'JetBrainsMono-Italic.ttf', 'JetBrains Mono Full', 'italic', '100 800'


# Name records that carry a font's name (family, subfamily, unique id, full name, PostScript name, typographic family and
# subfamily, WWS names). Copyright, trademark, licence and designer records are kept as they are.
NAME_IDS = (1, 3, 4, 6, 16, 17, 18, 21, 22)
RENAMES = {'iA Writer Mono S': 'Quill Mono', 'iAWriterMonoS': 'QuillMono'}
RESERVED = ('iA Writer', 'iAWriter', 'Plex')


def rename(font):
    """Replace a reserved font name in the naming records of a modified (trimmed) copy, as the SIL OFL requires."""
    for rec in font['name'].names:
        if rec.nameID not in NAME_IDS:
            continue
        s = rec.toUnicode()
        for old, new in RENAMES.items():
            s = s.replace(old, new)
        if any(r in s for r in RESERVED):
            raise SystemExit(f'reserved name left in name ID {rec.nameID}: {s}')
        rec.string = s


def trim(src, dest):
    """Write a woff2 copy of src cut down to UNICODES, with all layout features, axes, hinting and name records kept."""
    font = TTFont(src)
    opts = subset.Options()
    opts.layout_features = ['*']
    opts.name_IDs = ['*']          # keeps copyright, trademark and licence notices (MB Type licence ¶10)
    opts.name_languages = ['*']
    opts.notdef_outline = True
    opts.glyph_names = False
    opts.flavor = 'woff2'
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=subset.parse_unicodes(UNICODES))
    sub.subset(font)
    if 'iAWriter' in src.name:
        rename(font)
    font.flavor = 'woff2'
    font.save(dest)
    return font


def features(font):
    """Return the sorted GSUB feature tags of a font."""
    if 'GSUB' not in font:
        return []
    return sorted({r.FeatureTag for r in font['GSUB'].table.FeatureList.FeatureRecord})


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    (OUT / 'woff2').mkdir(parents=True, exist_ok=True)
    rules = []
    for src, family, style, weight in faces():
        dest = OUT / 'woff2' / (src.stem.replace(' ', '-') + '.woff2')
        font = trim(src, dest)
        feats = features(font)
        print(f'{src.name:32} -> {dest.name:34} {dest.stat().st_size // 1024:4} KB  '
              f'onum={"onum" in feats} smcp={"smcp" in feats} glyphs={len(font.getBestCmap())}')
        b64 = base64.b64encode(dest.read_bytes()).decode()
        rules.append(f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
                     f"src:url(data:font/woff2;base64,{b64}) format('woff2');font-display:block}}")
    (OUT / 'fontfaces.css').write_text('\n'.join(rules) + '\n', encoding='utf-8', newline='\n')
    print('fontfaces.css', (OUT / 'fontfaces.css').stat().st_size // 1024, 'KB')
    snippets = OUT / 'snippets'
    snippets.mkdir(exist_ok=True)
    old = snippets / 'typography-fonts.css'   # the separate font snippet of earlier versions
    if old.exists():
        old.unlink()
    text = RULES.rstrip('\n') + '\n\n' + HEADER.rstrip('\n') + '\n\n' + '\n'.join(rules) + '\n'
    (snippets / 'typography.css').write_text(text, encoding='utf-8', newline='\n')
    # The OFL fonts all use SIL OFL 1.1 (only spacing and the FAQ address differ): one file with every copyright line.
    ofl = [ROOT / 'fonts' / d / f for d, f in (('alegreya', 'OFL.txt'), ('alegreya-sans', 'OFL.txt'), ('jetbrains-mono', 'OFL.txt'),
                                              ('courier-prime', 'OFL.txt'), ('ia-writer-mono', 'LICENSE.md'))]
    lines = [l.strip() for f in ofl for l in f.read_text(encoding='utf-8').splitlines() if re.match(r'Copyright (\d|©|\(c\))', l.strip())]
    note = ('Quill Mono is a Modified Version of iA Writer Mono S: trimmed to Latin-script languages and renamed, because\n'
            '"iA Writer" and "Plex" are Reserved Font Names.\n')
    body = ofl[0].read_text(encoding='utf-8').split('\n', 1)[1]
    (snippets / 'OFL.txt').write_text('\n'.join(lines) + '\n\n' + note + body, encoding='utf-8', newline='\n')
    print('snippets/typography.css', (snippets / 'typography.css').stat().st_size // 1024, 'KB')


RULES = (ROOT / 'snippets' / 'typography.css').read_text(encoding='utf-8')
HEADER =(ROOT / 'snippets' / 'typography-fonts.head.css').read_text(encoding='utf-8')


if __name__ == '__main__':
    main()
