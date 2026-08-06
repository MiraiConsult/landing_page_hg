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

# ---- vídeos: <source> sai, o base64 vai para um <script> ------------------
html, n = re.subn(r'\s*<source src="assets/video/passo\d\.webm"\s*\n?\s*'
                  r"type='video/webm; codecs=\"vp09\.01\.30\.08\"'>", '', html)
assert n == 4, f'esperava remover 4 sources webm, removi {n}'

depositos = []
for i in (1, 2, 3, 4):
    html, k = re.subn(f'<source src="assets/video/passo{i}\\.mp4" type="video/mp4">',
                      f'<!-- vídeo em #v-passo{i} -->', html)
    assert k == 1
    depositos.append((f'v-passo{i}', LEVE / f'passo{i}.mp4'))

# Os quatro <video> são marcados de uma vez, na ordem do documento. Um replace
# por vez não serve: depois do primeiro, o trecho procurado continua casando
# com ele mesmo e todas as marcas se empilhavam no primeiro vídeo.
contador = [0]


def marcar(_):
    contador[0] += 1
    return f'<video class="step-loop" data-hg-src="v-passo{contador[0]}"'


html, n = re.subn(r'<video class="step-loop"', marcar, html)
assert n == 4, f'esperava marcar 4 vídeos de passo, marquei {n}'

html, n = re.subn(r'<source src="assets/video/motion-hellogrowth\.mp4" type="video/mp4">',
                  '<!-- vídeo em #v-motion -->', html)
assert n == 1
html = html.replace('<video class="platform-video"', '<video class="platform-video" data-hg-src="v-motion"', 1)
depositos.append(('v-motion', LEVE / 'motion.mp4'))

html = html.replace('<a href="assets/video/motion-hellogrowth.mp4">Baixar o Motion institucional</a>',
                    'Baixe a versão em pasta para assistir.')

blocos = '\n'.join(
    f'<script type="text/plain" id="{ident}">{base64.b64encode(caminho.read_bytes()).decode()}</script>'
    for ident, caminho in depositos)

leitor = """
<script>
/* Vídeos guardados como texto viram blob: aqui. Não vão como data: no src
   porque o Safari só toca vídeo de origem que atenda requisição por faixa de
   bytes — data: não atende, blob: atende. */
(function () {
  var vids = document.querySelectorAll('video[data-hg-src]');
  Array.prototype.forEach.call(vids, function (v) {
    var dep = document.getElementById(v.getAttribute('data-hg-src'));
    if (!dep) return;
    try {
      var bin = atob(dep.textContent.trim());
      var buf = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      v.src = URL.createObjectURL(new Blob([buf], { type: 'video/mp4' }));
      dep.textContent = '';   // libera a cópia em texto, que já não serve
    } catch (e) { /* sem vídeo, fica o pôster */ }
  });
})();
</script>
"""

# Ordem obrigatória: depósitos, leitor, script de animação. O leitor procura os
# depósitos por id, então eles têm de já existir no documento; e o de animação é
# quem dá play, então precisa achar o src já montado.
alvo = '<script>\n(function () {\n  window.__hgAnim = true;'
assert alvo in html
html = html.replace(alvo, blocos + '\n' + leitor + '\n' + alvo, 1)

# preload="none" não faz sentido com o arquivo já dentro
html = html.replace('preload="none"', 'preload="auto"')

sem_comentarios = re.sub(r'<!--.*?-->', '', html, flags=re.S)
# \s antes do atributo para não casar com data-hg-src="…", que é interno
externos = [u for u in re.findall(r'\s(?:src|href|poster)="((?!data:)[^"]*)"', sem_comentarios)
            if not u.startswith(('#', 'mailto:', 'tel:', 'http'))]
assert not externos, f'ficou dependendo de arquivo externo: {externos}'

SAIDA.write_text(html, encoding='utf-8')
print(f'videos embutidos : {len(depositos)}')
print(f'arquivos externos: {externos or "nenhum"}')
print(f'arquivo          : {SAIDA}')
print(f'tamanho          : {SAIDA.stat().st_size / 1048576:.1f} MB')
