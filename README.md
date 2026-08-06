# HelloGrowth — Landing Page

Implementação em HTML/CSS do design [Apresentação HG](https://www.figma.com/design/nvltdAz3asWyuA17yLMpnV/Apresenta%C3%A7%C3%A3o-HG?node-id=3-2)
(arquivo `nvltdAz3asWyuA17yLMpnV`, frame `3:2` — 1440 × 9576).

Página estática, sem build e sem dependências externas: é só abrir ou publicar a pasta.

```
├── index.html
├── css/styles.css
├── assets/
│   ├── logo-hellogrowth.svg      ← SVG exportado do Figma
│   ├── hero-laptop-*.webp        ← notebook sem os cards (bitmap 4096px)
│   ├── hero-laptop.png           ← fallback
│   ├── hero-card-*.webp          ← os 5 cards, recortados um a um
│   ├── favicon.svg               ← adição minha; não existe no design
│   ├── fonts/                    ← Inter (variável) + licença OFL
│   └── video/                    ← motion institucional, os 4 laços e os pôsteres
└── README.md
```

Cores, pesos, tamanhos, raios e espaçamentos foram lidos do Figma via MCP
(`get_design_context` / `get_variable_defs`), não estimados a partir de imagem.

## Rodando localmente

Abrir o `index.html` direto no navegador funciona, **exceto pelas fontes**: o `file://`
bloqueia webfonts por CORS e a página cai na fonte de sistema. Para ver o resultado real:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

Há dois arquivos gerados a partir do `index.html` — que é sempre o que se edita:

| Gerado por | Saída | Para quê |
|---|---|---|
| `tools/build_pasta.py` | pasta + `.zip` (110 MB) | qualidade máxima, computador |
| `tools/build_portatil.py` | um `.html` só (19 MB) | celular e envio por link/e-mail |

**Por que existem os dois.** A pré-visualização do iOS (app Arquivos / Quick Look) roda o
HTML numa caixa fechada, **sem acesso aos arquivos vizinhos**: na versão em pasta nem os
vídeos nem os pôsteres carregam, só o que já está embutido. Por isso a versão portátil não
deixa nada de fora.

**Nada ali pode depender de JavaScript.** A mesma pré-visualização também não roda script
— o sintoma que denunciou isso foi o feixe de luz dos rótulos funcionando (CSS puro)
enquanto o brilho das pílulas não (dependia de `.is-in`, posta por script). Então na
versão portátil os vídeos vão como `data:` direto no `<source>`, com `autoplay loop muted
playsinline`, que é o caminho nativo do WebKit para vídeo mudo em laço.

O `autoplay` existe **só** na versão portátil: na página servida por rede ele forçaria o
download dos quatro vídeos de uma vez.

Quando o script roda, ele troca o `data:` por `blob:` — o Safari só toca vídeo de origem
que responda a requisição por faixa de bytes, o que `data:` não faz e `blob:` faz. É
melhoria, não requisito: sem script fica o `data:`, que já basta em Chrome, Firefox e Edge.

Há ainda uma destrava por toque na página principal: alguns navegadores dentro de
aplicativos recusam qualquer `play()` que não venha de um gesto, mesmo com o vídeo mudo. O
primeiro toque serve de gesto e solta os laços parados.

Verificado com o navegador de **JavaScript desligado**: os laços tocam e as pílulas
brilham do mesmo jeito.

## O que ainda precisa ser preenchido

| Local | O que falta | Onde mexer |
|---|---|---|
| CTAs | Link real de agendamento (Calendly / WhatsApp) | 2 ocorrências marcadas com `<!-- TODO -->`; hoje apontam para a âncora `#agendar` |

Os placeholders de vídeo e de GIF **já foram preenchidos** — ver "Mídia" abaixo.

**A seção "Investimento" do design foi removida** a pedido. Se voltar a fazer sentido,
o histórico do git tem a marcação original.

## Tokens

As variáveis do Figma viraram custom properties no `:root` do `styles.css`:

| Token | Hex | Nome no Figma |
|---|---|---|
| `--lime` | `#bfff00` | lima |
| `--teal` | `#1b6b5b` | Color 2 |
| `--deep` | `#004d40` | verde-1 |
| `--green-2` | `#28ae61` | verde-3 |
| `--paper` | `#edf0ee` | claro |
| `--ink` | `#05221d` | — (fundo escuro) |
| `--green` | `#34a853` | — ("Mais" do hero, logo) |
| `--gold` | `#f5b301` | — (estrelas) |
| `--wa-*` | — | wa-bg, wa-in, wa-out, wa-text, wa-muted |

**Tipografia:** Inter (variável 100–900, com itálico), **auto-hospedada** em vez de vir
do CDN do Google: carrega mais rápido, não quebra se o CDN estiver bloqueado e evita
a requisição a um terceiro (relevante para LGPD).

## Decisões que vale saber

**Mock do WhatsApp** reconstruído em HTML/CSS em vez de imagem — fica nítido em
qualquer tela, pesa quase nada e o texto das mensagens dá pra editar direto no HTML.

**Responsivo.** O design só existe em 1440 px; as quebras abaixo disso são decisão de
implementação. Tipografia fluida com `clamp()`, grids colapsando em 720 px / 960 px.
Sem overflow horizontal em 1440, 1180, 834, 390 e 320 px.

Três ajustes valem explicação, todos em `@media (max-width: 959px)`:

**O notebook.** A imagem foi exportada com o notebook fora do centro de propósito — a
área vazia à esquerda é o que, no desktop, deixa a imagem invadir a coluna de texto. Sem
essa coluna a sobra vira espaço morto e o notebook encolhe num canto. A tinta ocupa
x 25,33%→97,17% da imagem (medido no canal alfa): alargar a caixa em `1/0,7184` e puxá-la
`-35,3%` para a esquerda faz o notebook preencher a largura. Os cards são posicionados em
porcentagem da mesma caixa, então acompanham sem ajuste.

**As pílulas do agente de IA** não quebram linha em largura nenhuma. Com `flex-wrap: wrap`
elas caíam duas em cima e uma embaixo entre 960 px e ~1090 px e no celular, o que desmancha
a leitura de sequência. Agora repartem a linha em partes iguais com teto nos 153 px do
design — em tela larga o teto vale e o resultado é idêntico ao Figma.

**Os ícones das pílulas são SVG, não caractere.** O iOS renderiza `✔` e `✦` como emoji,
com cor própria, ignorando o `color` do CSS: o tique aparecia escuro e ilegível sobre o
verde. O da anamnese virou três brilhos crescentes, sugerindo a sequência.

**Acessibilidade.** HTML semântico, hierarquia de headings sem saltos, skip link,
`alt` descritivo nas imagens, mock do chat com `aria-label` resumindo a conversa,
foco visível e `prefers-reduced-motion` respeitado.

**Quebras de linha por `<span>` em bloco**, não `<br>` — mantém as quebras do design
sem colar as palavras na leitura por tecnologia assistiva.

**Imagem do hero.** Vem de duas camadas separadas no Figma, na mesma caixa
(`72:3` "comp 1" = notebook, `72:2` "cards 1" = os cinco cards), ambas exportadas em
4096 × 3175. Como os cards estão sobre transparência, separá-los é só pegar os
componentes conectados do canal alpha — sai um por card, com a sombra, sem máscara nem
recorte manual. As posições em porcentagem saem da mesma origem, então batem sem ajuste. O notebook é servido por `srcset` em duas larguras —
1200 px (84 KB) para telas 1x e 2400 px (282 KB) para retina. O bloco recebe
`pointer-events: none` porque a área transparente passa por cima dos CTAs e roubaria
o clique.

## Animação

Revelação por scroll com `IntersectionObserver`, sem biblioteca nenhuma. A configuração
fica numa tabela única no fim do `index.html` — cada linha é
`[gatilho, itens, passo, atraso, variante]`, então mudar o ritmo de uma seção é mexer
em um número.

Só `opacity` e `transform` são animados, que são as duas propriedades que a GPU compõe
sem recalcular layout.

Três salvaguardas, porque animação que esconde conteúdo é risco real:

1. O estado inicial invisível depende da classe `.js` no `<html>`. **Sem JavaScript,
   nada fica escondido** — a página renderiza inteira.
2. Se o script de animação não rodar (erro, navegador antigo), um timeout de 2,5s
   remove a classe `.js` e devolve tudo à vista.
3. Com `prefers-reduced-motion: reduce` o script sai de cena logo no começo e nenhum
   elemento chega a ficar oculto.

Destaques: o chat do WhatsApp toca mensagem a mensagem quando entra em cena, o "+100"
conta a partir do zero, as réguas entre os passos são traçadas da esquerda para a
direita, os cards das dores entram cada um pelo seu lado do grid e a esteira de
"Como funciona" é desenhada em sequência, com as setas deslizando entre as etapas.

**Hero.** O notebook é uma imagem estática (`hero-laptop-*`); os cinco cards do
dashboard são recortes separados (`hero-card-*`) posicionados em porcentagem sobre ele.
Cada card flutua com duração, atraso e amplitude próprios — é a diferença entre eles
que dá a sensação de vento. A amplitude é percentual, então acompanha a escala da
imagem em telas menores.

**Pílulas do agente de IA.** Percurso luminoso em loop: cada pílula acende e cresce um
pouco, na ordem, e recomeça. O traço de ligação entre elas saiu do design — ficava por
cima da pílula quando ela crescia. As três compartilham o mesmo ciclo de 4s e se
diferenciam só pelo `animation-delay`, o que mantém a ordem sempre correta.

O brilho **não espera nada**: roda desde o carregamento, como o feixe de luz dos rótulos.
Antes dependia da classe `.is-in`, posta por JavaScript, e por isso não acontecia onde o
script não roda. A entrada das pílulas virou só opacidade (variante `fade`) — era ela que
disputava o `transform` com o brilho e obrigava o antigo atraso inicial de 1,4s.

**Traços dos rótulos.** Um ponto de luz corre de uma ponta à outra em replay, para chamar
a leitura. É um gradiente de 55% da largura deslocado por `background-position`; a cor do
ponto muda conforme o fundo (branco no escuro, lima no claro) para sempre parecer luz.

## Mídia

Entregue: um `.mov` de 58s (Motion Hello Growth V10), quatro GIFs dos passos e um PNG
de capa. Somavam 151 MB. Cada decisão abaixo foi medida, não estimada.

**Motion institucional — recodificação zero.** O `.mov` já vinha com H.264 em
`yuv420p` por dentro; era só o invólucro QuickTime. Trocar para `.mp4` é remux
(`-c copy`), não recompressão: o hash de cada quadro decodificado bate com o do
original. Ficou em 48,9 MB. Uma versão em CRF 18 daria 16,5 MB com diferença média de
0,32/255 — imperceptível, mas o pedido era não perder qualidade, então ficou o original.

**Passos — VP9 4:4:4 em vez de GIF.** GIF só comporta 256 cores por quadro e usa
pontilhado para simular o resto; os quatro somavam 100 MB. Convertidos para
1200 × 900 (o dobro exato da caixa de 600 × 450, ou seja, retina sem sobra),
`libvpx-vp9 -crf 32 -pix_fmt yuv444p`, 35 MB no total.

A escolha do 4:4:4 veio de uma medição: em 4:2:0 a diferença contra o GIF **não cede
com mais bitrate** — CRF 18 → 10 triplica o arquivo e a diferença fica em 11,1 → 11,0.
O gargalo é a subamostragem de cor, que borra as bordas do texto da interface. Separando
os pixels de texto dos de área lisa, o H.264 4:2:0 erra 7,89 no texto contra 3,82 do
VP9 4:4:4 — e ainda por cima o VP9 saiu **menor** (8,95 MB contra 6,59 MB no passo 1,
com a qualidade invertida a favor dele).

Cada `<video>` tem WebM e MP4: o navegador baixa só o primeiro que entende. O WebM
atende Chrome, Firefox e Edge; o MP4 existe para o Safari, que não decodifica VP9 4:4:4.

**O codec vai declarado no `<source>`, e isso não é detalhe.** Perguntado por
`type="video/webm"` puro, o Safari responde `maybe` — ele realmente toca WebM, só que
no perfil 0. Com essa resposta ele fica com o `<source>` do WebM e só descobre que não
decodifica o perfil 1 na hora de tocar, quando a escolha de fonte já passou e não há
volta ao MP4: o vídeo fica parado no pôster. Com
`type='video/webm; codecs="vp09.01.30.08"'` ele recusa de saída e pega o MP4 sozinho.

Há ainda uma rede de segurança no script: se um `<video>` terminar com `error`, a fonte
é trocada pelo MP4 na mão. O gatilho é só `v.error`, nunca demora — num 3G ruim o WebM
pode levar bem mais que alguns segundos até o primeiro quadro, e trocar por lentidão
rebaixaria a qualidade caladamente. Testado nos três cenários: normal fica no WebM,
WebM indecodificável cai no MP4, e WebM lento (6s) **não** troca.

**Capa.** O PNG entregue era 16 bits por canal sem necessidade. Reduzido a 8 bits:
1,80 MB → 216 KB com diferença zero.

**Comportamento.** O institucional tem controles e `preload="none"`, então só baixa
quando alguém dá play. Os quatro laços rodam mudos, sem controles, e um
`IntersectionObserver` os inicia ao entrar em cena e pausa ao sair — fora da tela seria
rede e processador à toa. Com `prefers-reduced-motion: reduce` nenhum toca sozinho: ficam
no pôster e ganham controles, para continuarem acessíveis a quem quiser ver.

**Pôsteres.** Primeiro quadro de cada laço, salvos em WebP (~170 KB). O do passo 4 é o
quadro 120 — o primeiro é fundo verde vazio e a caixa pareceria quebrada.

## Um ponto de atenção

**O eyebrow "POR QUE EXISTIMOS?" está invisível no Figma.** Na faixa verde, o texto
e o traço estão em `#1b6b5b` — exatamente a cor do fundo daquela seção. Todos os outros
eyebrows da página são legíveis, então isso parece um descuido, não intenção. Aqui ele
foi deixado legível (`rgba(237,240,238,.85)`). Se for proposital, é só ajustar
`.eyebrow--on-teal` no `styles.css`.
