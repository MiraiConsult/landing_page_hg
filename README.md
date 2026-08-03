# HelloGrowth — Landing Page

Conversão em HTML/CSS do design `HelloGrowth — Landing` (Figma → PDF, artboard de 1440 × 9576 px).

Página estática, sem build e sem dependências externas: é só abrir o `index.html` ou publicar a pasta.

```
├── index.html
├── css/styles.css
├── assets/
│   ├── laptop-dashboard.png / .webp   ← extraído do arquivo original
│   ├── favicon.svg
│   └── fonts/                         ← Plus Jakarta Sans (variável) + licença OFL
└── README.md
```

## Rodando localmente

Abrir o `index.html` direto no navegador funciona, **exceto pelas fontes**: o `file://`
bloqueia o carregamento de webfonts por CORS e a página cai na fonte de sistema.
Para ver o resultado real, sirva por HTTP:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## O que ainda precisa ser preenchido

O design já vinha com marcações de conteúdo pendente, e elas foram mantidas como
blocos visíveis de placeholder para não passarem despercebidas:

| Local | O que falta | Onde mexer |
|---|---|---|
| Seção "A plataforma" | Vídeo institucional (Motion Hello Growth V8) | `index.html` — há um comentário com a tag `<video>` pronta para substituir a div |
| Passos 01–04 | `gif-passo1.gif` … `gif-passo4.gif` | trocar cada `div.ph--gif` por `<img>` |
| Seção "Investimento" | Planos e valores — marcado como `[AJUSTAR]` no design | bloco `div.ph--price` |
| CTAs | Link real de agendamento (Calendly / WhatsApp) | 2 ocorrências marcadas com `<!-- TODO -->`; hoje apontam para a âncora `#agendar` |

Os placeholders de GIF são `4:3` e o de vídeo é `16:9`, iguais às caixas do design —
trocar por mídia nessa proporção não desloca o layout.

## Decisões que vale saber

**Tipografia.** As fontes vieram vetorizadas (Type3) no PDF, então o nome da família
original se perdeu. Usei **Plus Jakarta Sans** (variável 200–800, com itálico real),
que é a correspondência aberta mais próxima do desenho geométrico do original.
Se você souber qual é a fonte de verdade, é trocar os quatro `@font-face` no topo do
`styles.css` — nada mais no CSS depende dela.

A fonte é **auto-hospedada** em vez de vir do CDN do Google: carrega mais rápido, não
quebra se o CDN estiver bloqueado e evita a requisição a um terceiro (relevante para LGPD).

**Cores.** Todas amostradas pixel a pixel do arquivo original e centralizadas em
variáveis CSS no `:root`. A paleta:

| Token | Hex | Uso |
|---|---|---|
| `--lime` | `#bfff00` | acento principal, CTA |
| `--ink` | `#05211c` | fundo escuro |
| `--teal` | `#1b6b5b` | faixa institucional, bordas |
| `--deep` | `#004d3f` | títulos sobre fundo claro |
| `--green` / `--green-2` | `#34a852` / `#28ae60` | logo, eyebrows, números |
| `--paper` | `#edefed` | fundo claro / texto sobre escuro |
| `--gold` | `#f4b301` | estrelas |

**Mock do WhatsApp.** Reconstruído em HTML/CSS em vez de virar imagem — fica nítido em
qualquer tela, pesa quase nada e o texto das mensagens dá pra editar direto no HTML.

**Responsivo.** O design só existia em 1440 px. As quebras de layout abaixo disso são
decisão de implementação: tipografia fluida com `clamp()` e grids que colapsam em
720 px / 960 px. Testado sem overflow horizontal em 1440, 1180, 834, 390 e 320 px.

**Acessibilidade.** HTML semântico, hierarquia de headings sem saltos, skip link,
`alt` descritivo na imagem, mock do chat com `aria-label` resumindo a conversa,
foco visível e `prefers-reduced-motion` respeitado.

## Ponto de atenção no texto

A frase da seção "Por que existimos" está como no design original:

> "Dentista excelente perde paciente para os seus **concorrente** porque não tem processo e reputação."

O certo seria "concorrent**es**". Mantive fiel ao design em vez de corrigir por conta
própria — vale ajustar antes de publicar (`index.html`, seção `.band-teal`).
