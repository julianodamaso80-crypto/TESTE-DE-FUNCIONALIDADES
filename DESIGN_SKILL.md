# DESIGN SKILL — SpriteTest
## Referência: InsightX Dark SaaS (Dribbble - Kamrul Hasan Rifat)

<<<<<<< HEAD
### PALETA DE CORES OFICIAL

=======
### PALETA OFICIAL
>>>>>>> 62b36eb (design: insightx style - dark #1a1a1a + verde neon #a3e635 + DESIGN_SKILL.md)
| Token | Hex | Uso |
|---|---|---|
| Background | #1a1a1a | Body, página principal |
| Surface Card | #242424 | Cards, painéis |
<<<<<<< HEAD
| Surface Sidebar | #1e1e1e | Sidebar, nav lateral |
| Surface Input | #1e1e1e | Inputs, selects |
| Surface Border | #2e2e2e | Bordas de cards |
| Surface Hover | #2f2f2f | Hover states |
| Accent Primary | #a3e635 | Botões CTA, highlights, métricas positivas |
| Accent Green | #84cc16 | Hover do primary |
| Accent Bright | #4ade80 | Indicadores de sucesso |
| Text Primary | #ffffff | Títulos, valores |
| Text Secondary | #9ca3af | Labels, descrições |
| Text Muted | #6b7280 | Placeholders, hints |
| Error | #f87171 | Erros, falhas |
| Warning | #fbbf24 | Avisos |
| Info | #60a5fa | Informações, running |

### TIPOGRAFIA
- Fonte: Inter (Google Fonts)
- Títulos grandes: font-bold, tracking-tight
- Labels: font-medium, uppercase, tracking-widest, text-xs
- Valores métricos: font-bold, text-2xl ou text-3xl
- Corpo: font-normal, leading-relaxed

### COMPONENTES PADRÃO

#### Botão Primary
- bg: #a3e635 (primary-400)
- hover: #bef264 (primary-300)
- texto: #1a1a1a (dark-900) — SEMPRE escuro no fundo verde
- rounded-lg, font-semibold
- shadow: shadow-primary-950/30

#### Cards
- bg: #242424
- border: #2e2e2e
- rounded-xl
- SEM glassmorphism, SEM blur — design é flat e limpo

#### Sidebar
- bg: #1e1e1e (mais escuro que cards)
- link ativo: bg-primary-950/40, text-primary-400, border-primary-900/30
- separadores: section-title uppercase tracking-widest text-gray-600

#### Métricas (stat cards)
- Valor: text-white font-bold text-2xl
- Label: text-gray-400 text-xs uppercase
- Positivo: text-primary-400 (verde) com ↑
- Negativo: text-red-400 com ↓

#### Badges
- success: bg-emerald-950/60 text-emerald-400 border-emerald-900/40
- error: bg-red-950/60 text-red-400 border-red-900/40
- running: bg-blue-950/60 text-blue-400 border-blue-900/40
- warning: bg-amber-950/60 text-amber-400 border-amber-900/40
- primary: bg-primary-950/60 text-primary-400 border-primary-900/40

### PRINCÍPIOS VISUAIS
1. FLAT: sem glassmorphism, sem blur excessivo
2. DARK PURO: fundo quase preto, NÃO navy/azul
3. VERDE NEON como único accent — não roxo, não azul
4. Bordas SUTIS: quase invisíveis (#2e2e2e)
5. Espaçamento GENEROSO: padding mínimo p-6 nos cards
6. Hierarquia clara: branco > cinza claro > cinza escuro
7. Métricas em destaque com fonte bold grande
8. Inter em TUDO
=======
| Surface Sidebar | #1e1e1e | Sidebar nav lateral |
| Surface Border | #2e2e2e | Bordas sutis |
| Surface Hover | #2f2f2f | Hover states |
| Accent Primary | #a3e635 | Botões CTA, métricas positivas |
| Text Primary | #ffffff | Títulos, valores |
| Text Secondary | #9ca3af | Labels, descrições |
| Text Muted | #6b7280 | Placeholders |
| Error | #f87171 | Erros, falhas |
| Warning | #fbbf24 | Avisos |
| Info | #60a5fa | Running, informações |

### TIPOGRAFIA
- Fonte: Inter (Google Fonts)
- Títulos: font-bold tracking-tight
- Labels seção: text-xs uppercase tracking-widest font-semibold
- Valores métricos: font-bold text-2xl ou text-3xl text-white
- Corpo: leading-relaxed text-gray-400

### COMPONENTES
- btn-primary: bg #a3e635, texto #1a1a1a (SEMPRE escuro), rounded-lg
- btn-secondary: bg #242424, border #2e2e2e, texto gray-200
- card: bg #242424, border #2e2e2e, rounded-xl p-6
- sidebar: bg #1e1e1e (mais escuro que cards)
- sidebar-link ativo: bg primary-950/40, text primary-400, border primary-900/30
- stat-card: card com valor bold branco + label gray-500 uppercase + métrica verde ↑ ou vermelha ↓
- badges: rounded-full com bg-*-950/60 text-*-400 border-*-900/40

### PRINCÍPIOS
1. FLAT — sem glassmorphism nem blur excessivo
2. DARK PURO — fundo #1a1a1a, NÃO navy/azul
3. VERDE NEON #a3e635 como único accent
4. Bordas SUTIS — quase invisíveis #2e2e2e
5. Inter em TUDO
6. Métricas em destaque — números grandes, bold, brancos
7. Hierarquia: branco > gray-300 > gray-400 > gray-500 > gray-600
>>>>>>> 62b36eb (design: insightx style - dark #1a1a1a + verde neon #a3e635 + DESIGN_SKILL.md)
