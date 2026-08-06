"""Monta um HTML único, com os vídeos dentro — o que abre no celular.

Motivo: a pré-visualização do iOS (app Arquivos / Quick Look) roda o HTML numa
caixa fechada, sem acesso aos arquivos vizinhos. Por isso, na pasta, nem os
vídeos nem os pôsteres apareciam — só o que já estava embutido. Aqui não sobra
nada de fora.

Os vídeos NÃO entram como data: URI no src. O Safari exige requisição por faixa
de bytes para tocar vídeo, coisa que data: não oferece; blob: oferece. Então o
base64 fica guardado num <script type="text/plain"> e vira blob no navegador.
"""
import base64, re, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEVE = ROOT / 'assets/video/leve'
SAIDA = pathlib.Path('/home/user/hellogrowth-apresentacao-celular.html')

html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'css/styles.css').read_text(encoding='utf-8')


def b64(caminho, mime):
    return f'data:{mime};base64,' + base64.b64encode(pathlib.Path(caminho).read_bytes()).decode()


# ---- CSS, fontes e imagens, igual à build da pasta -------------------------
for bloco in re.findall(r'@font-face \{.*?\}', css, re.S):
    if 'latin-ext' in bloco:
        css = css.replace(bloco, '')
for f in ('assets/fonts/inter-latin.woff2', 'assets/fonts/inter-latin-italic.woff2'):
    css = css.replace(f'url("../{f}")', f'url("{b64(ROOT / f, "font/woff2")}")')
assert '../assets/' not in css

link = '<link rel="stylesheet" href="css/styles.css">'
assert link in html
html = html.replace(link, '<style>\n' + css.strip() + '\n</style>')
html = re.sub(r'\s*<link rel="preload"[^>]*>', '', html)
html = html.replace('href="assets/favicon.svg"', f'href="{b64(ROOT / "assets/favicon.svg", "image/svg+xml")}"')
html = html.replace('src="assets/logo-hellogrowth.svg"',
                    f'src="{b64(ROOT / "assets/logo-hellogrowth.svg", "image/svg+xml")}"')

alt = ('Notebook exibindo o dashboard da HelloGrowth, com cards de oportunidades '
       'geradas, vendas convertidas e NPS registrados.')
img = ('<img class="hero-stage__base" src="' + b64(ROOT / 'assets/hero-laptop-2400.webp', 'image/webp') + '"\n'
       '                 width="2400" height="1630" fetchpriority="high"\n'
       f'                 alt="{alt}">')
html, n = re.subn(r'<picture>.*?</picture>', lambda _: img, html, flags=re.S)
assert n == 1
for rel in set(re.findall(r'assets/hero-card-[\w-]+\.webp', html)):
    html = html.replace(rel, b64(ROOT / rel, 'image/webp'))
html, n = re.subn(r'<a class="logo" href="/">(.*?)</a>',
                  lambda m: f'<span class="logo">{m.group(1)}</span>', html, flags=re.S)
assert n == 1

# ---- pôsteres embutidos ---------------------------------------------------
html = html.replace('poster="assets/video/capa-motion.png"',
                    f'poster="{b64(ROOT / "assets/video/capa-motion.png", "image/png")}"')
for i in (1, 2, 3, 4):
    html = html.replace(f'poster="assets/video/poster{i}.webp"',
                        f'poster="{b64(ROOT / f"assets/video/poster{i}.webp", "image/webp")}"')

# ---- vídeos embutidos ----------------------------------------------------
# O WebM 4:4:4 não entra: aqui só interessa o H.264, que toca em tudo.
html, n = re.subn(r'\s*<source src="assets/video/passo\d\.webm"\s*\n?\s*'
                  r"type='video/webm; codecs=\"vp09\.01\.30\.08\"'>", '', html)
assert n == 4, f'esperava remover 4 sources webm, removi {n}'


def embutir(rel_html, arquivo):
    """Troca o src do <source> pelo arquivo inteiro, em data:."""
    global html
    alvo = f'<source src="{rel_html}" type="video/mp4">'
    assert html.count(alvo) == 1, f'esperava 1 ocorrência de {rel_html}'
    html = html.replace(alvo, f'<source src="{b64(arquivo, "video/mp4")}" type="video/mp4">')


for i in (1, 2, 3, 4):
    embutir(f'assets/video/passo{i}.mp4', LEVE / f'passo{i}.mp4')
embutir('assets/video/motion-hellogrowth.mp4', LEVE / 'motion.mp4')

html = html.replace('<a href="assets/video/motion-hellogrowth.mp4">Baixar o Motion institucional</a>',
                    'Baixe a versão em pasta para assistir.')

# Os laços ganham `autoplay`. Na página servida por rede isso não existe, porque
# forçaria o download dos quatro vídeos de uma vez; aqui eles já estão dentro do
# arquivo, então não custa nada — e é o caminho nativo do WebKit para vídeo mudo
# em laço, o único que funciona onde o JavaScript não roda.
html, n = re.subn(r'<video class="step-loop" loop muted playsinline',
                  '<video class="step-loop" autoplay loop muted playsinline', html)
assert n == 4, f'esperava 4 laços com autoplay, marquei {n}'

# Melhoria para quando o script roda: blob: no lugar de data:. O Safari exige
# que a origem do vídeo responda a requisição por faixa de bytes — data: não
# responde, blob: responde. Sem script, fica o data: do <source>, que já basta
# em Chrome, Firefox e Edge.
leitor = """
<script>
(function () {
  if (!window.fetch || !window.URL || !URL.createObjectURL) return;
  Array.prototype.forEach.call(document.querySelectorAll('video'), function (v) {
    var s = v.querySelector('source[type="video/mp4"]');
    if (!s || s.src.slice(0, 5) !== 'data:') return;
    fetch(s.src).then(function (r) { return r.blob(); }).then(function (b) {
      var tocava = !v.paused;
      v.src = URL.createObjectURL(b);
      if (tocava) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
    }).catch(function () { /* fica o data:, que é o caminho sem script */ });
  });
})();
</script>
"""

alvo = '<script>\n(function () {\n  window.__hgAnim = true;'
assert alvo in html
html = html.replace(alvo, leitor + alvo, 1)

# preload="none" não faz sentido com o arquivo já dentro
html = html.replace('preload="none"', 'preload="auto"')

sem_comentarios = re.sub(r'<!--.*?-->', '', html, flags=re.S)
# \s antes do atributo para não casar com data-hg-src="…", que é interno
externos = [u for u in re.findall(r'\s(?:src|href|poster)="((?!data:)[^"]*)"', sem_comentarios)
            if not u.startswith(('#', 'mailto:', 'tel:', 'http'))]
assert not externos, f'ficou dependendo de arquivo externo: {externos}'

SAIDA.write_text(html, encoding='utf-8')
print(f'videos embutidos : {html.count(chr(34)) and html.count("data:video/mp4")}')
print(f'arquivos externos: {externos or "nenhum"}')
print(f'arquivo          : {SAIDA}')
print(f'tamanho          : {SAIDA.stat().st_size / 1048576:.1f} MB')
