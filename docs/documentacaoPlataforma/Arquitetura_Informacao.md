# Arquitetura de Informação (CityFlow MVP)

Este documento descreve a estrutura hierárquica e a organização de conteúdos do frontend do **CityFlow**. Serve de *blueprint* para os componentes React e o fluxo de interação.

A app é uma *Single-Page Application* agressiva: o mapa nunca desaparece. Em vez de modais flutuantes (planeados na visão original), o MVP entregue consolidou todos os controlos numa **sidebar fixa à esquerda** (em ecrãs `md` e maiores) ou num **drawer móvel** com a mesma estrutura (em ecrãs móveis), garantindo carga cognitiva reduzida e zero saltos de página.

## Estrutura entregue no MVP

| Nome lógico | O que mostra | Ações do utilizador | Estado |
| :--- | :--- | :--- | :---: |
| **`MapView`** (área principal) | Componente Leaflet a 100 % do *viewport* livre. Mostra basemap OpenStreetMap, marcadores de partida/destino e *polyline* da rota. | Pan livre, *zoom* dentro do raio de cobertura, clicar para definir A/B (1.º clique = partida, 2.º = destino, 3.º limpa a simulação). | ✅ |
| **Sidebar (desktop)** / **Drawer (mobile)** | Bloco vertical à esquerda em ≥ md (largura ~30 %); em mobile, abre como gaveta pelo botão flutuante "Definições". | Trocar de cidade, ajustar sliders, ativar/desativar escadas, ler estado da rota, ler mensagens de erro. | ✅ |
| **Bloco "Cidade"** | Dropdown estilizado (componente `CityDropdown`) com chip azul + chevron animado. Lista as cidades suportadas vindas de `GET /api/v1/cities`. | Clica no botão para abrir o *listbox*. Escolhe a cidade — o mapa voa para o novo centro e o estado é limpo. Fecha-se com clique fora ou tecla `Esc`. | ✅ |
| **Bloco "O Teu Trajeto"** | Estado textual da partida e do destino com ícones. | Apenas leitura — o utilizador interage com o mapa para definir os pontos. | ✅ |
| **Bloco "O Teu Perfil de Acessibilidade"** | Sliders de inclinação máxima (2 %–15 %) e largura mínima (0,5 m–2,0 m), e *toggle* "Evitar escadas". | Manipular cada controlo — o estado é guardado em memória até nova rota ser pedida. | ✅ |
| **Bloco "Alertas/Informações"** | Toasts dentro da sidebar: mensagem informativa azul (info de *snap-point*) e alerta vermelho (erros 422/424/rede). Usam `role="status"` e `role="alert"` para leitores de ecrã. | Auto-aparecem; desaparecem ao próximo clique válido. | ✅ |
| **Rodapé da sidebar** | Botão primário "Calcular rota segura" (44×44 px mínimo, WCAG 2.5.5). Quando há rota, mostra três métricas: distância, tempo estimado, inclinação crítica — com um *badge* verde/vermelho consoante o limite de conforto. | Clicar para acionar o `POST /api/v1/route`. | ✅ |
| **Toast superior "A validar ponto…"** | Pílula flutuante centrada no topo do mapa enquanto o servidor faz *snap*. | Apenas leitura — desaparece em ~50 ms numa rede normal. | ✅ |

## Componentes planeados (não no MVP)

Estes elementos faziam parte da visão original do CityFlow Inclusivo e ficam no *roadmap*:

| Nome lógico | O que faz | Estado |
| :--- | :--- | :---: |
| **`ContrastToggle`** | Floating Action Button no canto que muda o tema para alto contraste (`dark_matter`). | 🔜 |
| **`ActiveNavigationOverlay`** | Modo *Easy Read* durante a viagem real: oculta tudo exceto a próxima direção e o botão massivo "Reportar obstáculo". | 🔜 |
| **`ReportBarrierButton`** | Botão grande (≥ 44×44 px) que aciona o endpoint `POST /api/v1/report-barrier` com a localização atual via `navigator.geolocation`. | 🔜 |
| **`TurnByTurnAnnouncer`** | Usa Web Speech API e Vibration API para anunciar manobras conforme o utilizador se aproxima de um nó. | 🔜 |

## Notas de frontend (React.js)

*   `MapView` é a raiz permanente (`/`). Não existem outras rotas — toda a navegação é vertical / por estados internos.
*   A sidebar não é um modal; é uma coluna fixa em `md+` para manter o utilizador orientado. Em mobile, transforma-se num *drawer* lateral com o botão flutuante "Definições".
*   O componente `InteractiveMap` usa `useRef` para manter `city`, `startCoords` e `endCoords` sincronizados, evitando *stale closures* no handler de *click* do Leaflet.
*   Os controlos do mapa são acionados pelo clique direto sobre o componente; não há campos de texto para origem/destino no MVP (é uma decisão de UX para baixar a carga cognitiva — o ato de apontar é mais direto que digitar).
