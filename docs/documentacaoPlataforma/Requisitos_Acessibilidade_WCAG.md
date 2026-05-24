# Requisitos de Acessibilidade (WCAG 2.1) — CityFlow MVP

Este documento mapeia as diretrizes essenciais WCAG 2.1 nas implementações técnicas diretas que a equipa de frontend (React + Tailwind CSS) tem de cumprir no MVP. Os critérios focam-se nas personas estabelecidas (limitações motoras, baixa visão e daltonismo).

A coluna **Estado** indica se o critério está coberto pelo MVP entregue (✅) ou se será reforçado em fases futuras (🔜).

| ID | Critério WCAG 2.1 | Nível | Objetivo no CityFlow | Implementação técnica | Estado |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **1.4.3** | **Contraste mínimo** | AA | Garantir que a persona de baixa visão / daltonismo consegue ler textos da UI (menus, erros) sem esforço. | Texto principal `text-slate-800` sobre `bg-slate-50`/`bg-white` (≥ 4,5:1). Botão primário `bg-slate-800` com texto branco. Alertas vermelho/azul/verde usam variantes 700 sobre 50. | ✅ |
| **1.4.6** | **Contraste melhorado** | AAA | Garantir contraste excelente nos componentes vitais ("Calcular rota segura", *dropdown* de cidade). | Botão de cálculo: `bg-slate-800 text-white` (rácio ~16:1). *Toggle* "Evitar escadas" usa azul 600/branco. | ✅ |
| **2.5.5** | **Tamanho do alvo (Target Size)** | AAA | Prevenir *miss-clicks* graves na persona em cadeira de rodas, com tremores ou em piso irregular. | Botão "Calcular rota segura" tem ≥ 56 px de altura (py-4). Dropdown de cidade tem 48 px. Slider thumb com `accent-blue-600` mantém área de toque generosa. Botão flutuante mobile com 56×56 px. | ✅ |
| **1.4.4** | **Redimensionamento do texto** | AA | Permitir zoom do SO (Android/iOS) até 200 % sem quebrar o *layout*. | Tipografia em unidades `text-sm`/`text-base`/`text-lg`. A sidebar tem `overflow-y-auto` para acomodar zoom; o mapa redimensiona-se automaticamente. | ✅ |
| **3.3.2** | **Rótulos e instruções** | AA | Reduzir a carga cognitiva ao ajustar o perfil de acessibilidade. | Cada *slider* tem `<label>` visível (Inclinação máxima, Largura mínima da via). O `<select>`/dropdown tem `aria-label` "Escolhe a cidade" (com `sr-only`). | ✅ |
| **4.1.2** | **Nome, função e valor (ARIA)** | A | Os alertas dinâmicos têm de ser lidos por leitores de ecrã. | Toast informativo usa `role="status"`; alerta de erro usa `role="alert"`. Dropdown de cidade tem `role="listbox"` no painel aberto e `role="option"` + `aria-selected` em cada cidade. O botão de abrir tem `aria-haspopup="listbox"` e `aria-expanded`. | ✅ |
| **1.3.3** | **Características sensoriais** | A | Não depender exclusivamente da cor na UI (para a persona daltónica). | O *badge* de inclinação crítica combina cor (verde/vermelho) com ícones (`CheckCircle` / `AlertTriangle`). Os marcadores do mapa têm formas distintas além das cores (casa = partida, bandeira = destino). | ✅ |
| **2.4.7** | **Foco visível** | AA | Navegação por teclado / *switch* deve sempre mostrar um anel de foco. | Todos os controlos têm `focus:ring-2 focus:ring-blue-300` (ou similar). Dropdown e *toggle* respondem a `Enter` e `Space`. Pressionar `Esc` fecha o dropdown. | ✅ |
| **2.1.1** | **Acessível por teclado** | A | Toda a funcionalidade tem de ser usável apenas com teclado. | Sliders, *toggle* e dropdown são todos acessíveis via teclado. O clique no mapa para definir A/B continua a precisar de rato/toque — ver nota no *roadmap*. | 🟡 |
| **1.4.11** | **Contraste de elementos não-textuais** | AA | Bordas e ícones funcionais com ≥ 3:1. | Ícones `lucide-react` em `text-slate-400`–`text-slate-700` sobre fundos brancos / azul-claros, todos acima de 3:1. | ✅ |

## Compromissos e limitações conhecidas
*   **2.1.1 (Acessível por teclado):** a colocação dos pontos A/B no mapa continua a depender de interação por *pointer* (rato, dedo). No *roadmap* fica a alternativa de inputs de texto com geocodificação para utilizadores de teclado puro ou de tecnologias assistivas que não conseguem operar o Leaflet.
*   **Alto contraste explícito (UC03/RF-06):** o tema base já cumpre 1.4.3 AA. Um *toggle* dedicado para 7:1 AAA fica no *roadmap*.

## Checklist de desenvolvimento
Antes de fazer *commit* de qualquer ecrã / componente, responder a estas três perguntas:
1. Tem pelo menos 44 px de alvo (Tailwind `h-11 w-11` ou superior)?
2. Consigo navegar todo o componente com `[TAB]` e ver um anel de foco claro?
3. Passa num teste de contraste contra o fundo (sem cinzas claros sobre branco)?
