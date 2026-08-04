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
│   └── fonts/                    ← Inter (variável) + licença OFL
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

## O que ainda precisa ser preenchido

O design já vinha com marcações de conteúdo pendente, mantidas como blocos visíveis
para não passarem despercebidas:

| Local | O que falta | Onde mexer |
|---|---|---|
| Seção "A plataforma" | Vídeo institucional (Motion Hello Growth V8) | `index.html` — há um comentário com a tag `<video>` pronta para substituir a div |
| Passos 01–04 | `gif-passo1.gif` … `gif-passo4.gif` | trocar cada `div.ph--gif` por `<img>` |
| CTAs | Link real de agendamento (Calendly / WhatsApp) | 2 ocorrências marcadas com `<!-- TODO -->`; hoje apontam para a âncora `#agendar` |

Os placeholders de GIF são `4:3` e o de vídeo é `16:9`, iguais às caixas do design —
trocar por mídia nessa proporção não desloca o layout.

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
cima da pílula quando ela crescia. As três compartilham o mesmo ciclo de 4s e se diferenciam só
pelo `animation-delay`, o que mantém a ordem sempre correta. O atraso inicial de 1,4s
existe porque brilho e entrada disputam a mesma propriedade `transform` — sem ele o
brilho atropelaria a animação de entrada.

**Traços dos rótulos.** Um ponto de luz corre de uma ponta à outra em replay, para chamar
a leitura. É um gradiente de 55% da largura deslocado por `background-position`; a cor do
ponto muda conforme o fundo (branco no escuro, lima no claro) para sempre parecer luz.

## Um ponto de atenção

**O eyebrow "POR QUE EXISTIMOS?" está invisível no Figma.** Na faixa verde, o texto
e o traço estão em `#1b6b5b` — exatamente a cor do fundo daquela seção. Todos os outros
eyebrows da página são legíveis, então isso parece um descuido, não intenção. Aqui ele
foi deixado legível (`rgba(237,240,238,.85)`). Se for proposital, é só ajustar
`.eyebrow--on-teal` no `styles.css`.
