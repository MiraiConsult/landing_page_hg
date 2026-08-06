"""Monta a pasta que o usuário abre com dois cliques.

O index.html sai com CSS, fontes, logo e imagens do hero embutidos — porque o
file:// bloqueia webfont por CORS e a página cairia na fonte de sistema. Os
vídeos ficam de fora: <video src="..."> relativo funciona no file:// sem
problema, e embutir 110 MB em base64 (+33%) deixaria o HTML impraticável.
"""
import base64, re, pathlib, shutil, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = pathlib.Path('/home/user/hellogrowth-apresentacao')

html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'css/styles.css').read_text(encoding='utf-8')


def b64(rel, mime):
    return f'data:{mime};base64,' + base64.b64encode((ROOT / rel).read_bytes()).decode()


# 1) fora os @font-face de latin-ext: nenhum caractere da página usa esse subset
removidos = 0
for bloco in re.findall(r'@font-face \{.*?\}', css, re.S):
    if 'latin-ext' in bloco:
        css = css.replace(bloco, '')
        removidos += 1

for f in ('assets/fonts/inter-latin.woff2', 'assets/fonts/inter-latin-italic.woff2'):
    css = css.replace(f'url("../{f}")', f'url("{b64(f, "font/woff2")}")')
assert '../assets/' not in css, 'sobrou caminho relativo no CSS'

link = '<link rel="stylesheet" href="css/styles.css">'
assert link in html
html = html.replace(link, '<style>\n' + css.strip() + '\n</style>')
html = re.sub(r'\s*<link rel="preload"[^>]*>', '', html)

# 2) imagens pequenas embutidas; o <picture> com srcset vira uma imagem só
html = html.replace('href="assets/favicon.svg"', f'href="{b64("assets/favicon.svg", "image/svg+xml")}"')
html = html.replace('src="assets/logo-hellogrowth.svg"',
                    f'src="{b64("assets/logo-hellogrowth.svg", "image/svg+xml")}"')
alt = ('Notebook exibindo o dashboard da HelloGrowth, com cards de oportunidades '
       'geradas, vendas convertidas e NPS registrados.')
img = ('<img class="hero-stage__base" src="' + b64('assets/hero-laptop-2400.webp', 'image/webp') + '"\n'
       '                 width="2400" height="1630" fetchpriority="high"\n'
       f'                 alt="{alt}">')
html, n = re.subn(r'<picture>.*?</picture>', lambda _: img, html, flags=re.S)
assert n == 1, f'esperava 1 <picture>, achei {n}'

cards = re.findall(r'assets/hero-card-[\w-]+\.webp', html)
assert len(cards) == 5, f'esperava 5 cards, achei {len(cards)}'
for rel in set(cards):
    html = html.replace(rel, b64(rel, 'image/webp'))

# num arquivo avulso o href="/" do logo levaria para a raiz do disco
html, n = re.subn(r'<a class="logo" href="/">(.*?)</a>',
                  lambda m: f'<span class="logo">{m.group(1)}</span>', html, flags=re.S)
assert n == 1

# 3) o que pode continuar externo é só a pasta de vídeo
sem_comentarios = re.sub(r'<!--.*?-->', '', html, flags=re.S)
externos = [u for u in re.findall(r'(?:src|href|poster)="((?!data:)[^"]*)"', sem_comentarios)
            if not u.startswith(('#', 'mailto:', 'tel:', 'http'))]
fora = [u for u in externos if not u.startswith('assets/video/')]
assert not fora, f'ficou dependendo de arquivo que não vai na pasta: {fora}'

# 4) monta a pasta
if DEST.exists():
    shutil.rmtree(DEST)
(DEST / 'assets/video').mkdir(parents=True)
(DEST / 'index.html').write_text(html, encoding='utf-8')
for rel in sorted(set(externos)):
    shutil.copy2(ROOT / rel, DEST / rel)

leiame = """APRESENTAÇÃO HELLOGROWTH
========================

Para abrir: dê dois cliques no arquivo index.html.
Ele abre no seu navegador. Não precisa de internet nem instalar nada.

IMPORTANTE: mantenha o index.html e a pasta assets sempre juntos,
no mesmo lugar. Se separar, os vídeos param de aparecer.

Para enviar para alguém, mande a pasta inteira compactada (.zip).
"""
(DEST / 'LEIA-ME.txt').write_text(leiame, encoding='utf-8')

# 5) zip para enviar
zip_path = pathlib.Path('/home/user/hellogrowth-apresentacao.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(DEST.parent))

total = sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file())
print(f'@font-face latin-ext removidos : {removidos}')
print(f'arquivos externos (só vídeo)   : {len(set(externos))}')
print(f'index.html                     : {(DEST / "index.html").stat().st_size / 1048576:.2f} MB')
print(f'pasta                          : {total / 1048576:.1f} MB  -> {DEST}')
print(f'zip                            : {zip_path.stat().st_size / 1048576:.1f} MB  -> {zip_path}')
