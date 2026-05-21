# Arquitetura de Informação (CityFlow MVP)

Este documento dita a estrutura hierárquica e a organização de conteúdos do frontend do **CityFlow**. A tabela serve de *blueprint* a partir do qual os programadores constroem as vistas (componentes React) e o fluxo de navegação.

Para manter o foco no MVP e na usabilidade (carga cognitiva reduzida), a app segue uma arquitetura *single-page* agressiva com modais/gavetas móveis em vez de páginas separadas, garantindo que o mapa nunca sai da visão periférica do utilizador.

| Nome lógico (ecrã / componente base) | O que mostra / componentes visuais | Ações do utilizador (`onClick`, `onSubmit`) | Navegação (para onde o utilizador transita) |
| :--- | :--- | :--- | :--- |
| **`MapView` (pai / Home)** | O componente Leaflet/mapa (100 % do viewport `h-screen w-screen`). Mostra basemaps claros/escuros consoante o perfil. | Pan livre, `zoom-in`, `zoom-out`. | Mantém o utilizador neste ecrã o tempo todo. Aciona os ecrãs filhos listados em baixo. |
| **`Floating UI Layer`** (z-index acima do mapa) | Botão "centrar GPS", *toggle* "modo escuro / alto contraste", ícone circular de perfil em cima. | Alternar contraste dinâmico; centrar localização. Clicar na foto/ícone de perfil. | Expande modais de perfil ou chama APIs sem sair da página. O ícone de perfil abre o **`ProfileSettingsModal`**. |
| **`RoutePlannerPanel`** (rodapé flexível) | *Bottom sheet* (gaveta a subir do fundo). Input de origem, input de destino. Botão `[ Calcular rota ]` (44×44 px mín.). | Preencher inputs; acionar "Calcular". `onClick` numa área vazia do mapa injeta a morada reverso-geocoded no campo de destino. | Em submissão, a UI mantém-se, chama o backend, mostra o `LoadingSpinner` (WCAG `aria-live`) e transita o estado para **`ActiveNavigationOverlay`**. |
| **`ProfileSettingsModal`** (modal focada) | Botões de rádio (escolha única): "cadeira de rodas", "baixa visão", "sénior". Sliders para *hard constraints*: "largura da via" (0,5 m a 2 m), "inclinação máxima". | Ajustar variáveis da heurística e pressionar `[ Guardar perfil ]`. | Mostra *toast* "perfil aplicado". Fecha o modal automaticamente. O foco regressa ao **`MapView`**. |
| **`ActiveNavigationOverlay`** (modo de viagem Easy Read) | Esconde todos os inputs de texto. Limita a carga visual a: barra superior alta com a próxima direção ("virar em 50 m") e botão quadrado com a seta da manobra. O botão base vermelho `[ REPORTAR OBSTÁCULO ]` aparece. | Ler a indicação. Seguir a *polyline* grossa. SOS via *Reportar*. | Chegar ao destino devolve ao **`RoutePlannerPanel`** vazio. O botão de reporte dispara o *toast* "a recalcular alternativa" via API de *crowdsourcing*. |
| **`ErrorFeedbackToast`** (transversal) | Pequeno balão. Amarelo / vermelho consoante a severidade (WCAG). Expressa falhas do Pydantic de forma natural. Ex.: "aviso: sem rota para este perfil (424)". | Dispensar `onClick` ('X'). | Não transita. Auto-dispensa após 3000 ms. |

### Notas de frontend (React.js)
Dado o âmbito PWA / acessibilidade, os programadores nunca devem usar links `<a href="/definicoes">` planos entre estações. O ecrã do telemóvel não pode piscar nem limpar numa navegação dura.

O `MapView` é a raiz permanente (`/`) e todos os painéis deslizam suavemente pelo eixo Z, do fundo do telemóvel para junto do polegar (*Thumb-zone Design*).
