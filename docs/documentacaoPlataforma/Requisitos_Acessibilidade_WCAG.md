# Requisitos de Acessibilidade (WCAG 2.1) — CityFlow MVP

Este documento mapeia as diretrizes essenciais WCAG 2.1 nas implementações técnicas diretas que a equipa de frontend (React + Tailwind CSS) tem de cumprir no MVP. Os critérios focam-se nas personas estabelecidas (limitações motoras, baixa visão e daltonismo).

| ID | Critério WCAG 2.1 | Nível | Objetivo no CityFlow | Implementação técnica (React / Tailwind CSS) |
| :---: | :--- | :---: | :--- | :--- |
| **1.4.3** | **Contraste mínimo** | AA | Garantir que a persona de baixa visão / daltonismo consegue ler textos da UI (menus, erros) sem esforço. | O rácio de contraste tem de ser **4,5:1**. Usar classes Tailwind como `text-gray-900 bg-white` (normal) ou `text-yellow-400 bg-gray-900` (modo alto contraste). *Obrigatório validar a paleta primária com o WebAIM.* |
| **1.4.6** | **Contraste melhorado** | AAA | Garantir contraste excelente nos componentes vitais ("Reportar obstáculo" e "Calcular rota"). | Rácio de contraste acima de **7:1**. Ex.: `bg-blue-700` com texto branco *bold*. |
| **2.5.5** | **Tamanho do alvo (Target Size)** | AAA | Prevenir *miss-clicks* graves na persona em cadeira de rodas, com tremores ou em piso irregular. | Todos os elementos interativos (`<button>`, `<input>`, marcadores Leaflet) com **pelo menos 44×44 CSS pixels**. Tailwind: `min-h-[44px] min-w-[44px] p-4`. |
| **1.4.4** | **Redimensionamento do texto** | AA | Permitir zoom do SO (Android/iOS) até 200 % sem quebrar o layout. | Usar unidades `rem` do Tailwind (`text-base`, `text-lg`) em vez de px rígidos. O contentor pai não pode ter `overflow-hidden` sem scroll, evitando cortes de texto turn-by-turn quando ampliado. |
| **3.3.2** | **Rótulos e instruções** | AA | Reduzir a carga cognitiva ao introduzir coordenadas. | O `<input>` de origem/destino não pode depender apenas do `placeholder`. Usar `<label htmlFor="origem" className="sr-only">` para leitores de ecrã ou um rótulo visível para a persona sénior. |
| **4.1.2** | **Nome, função e valor (ARIA)** | A | O estado do *spinner* e os alertas dinâmicos têm de ser lidos por leitores de ecrã. | O *spinner* enquanto espera pela API tem `role="status" aria-live="polite"`. O *toggle* do modo *Easy Read* precisa de `aria-expanded={isOpen}`. |
| **1.3.3** | **Características sensoriais** | A | Não depender exclusivamente da cor na UI do mapa (para a persona daltónica). | Ao mostrar um aviso "rua cortada", a UI não pode ser apenas "o vermelho está cortado". O Tailwind tem de combinar `flex items-center gap-2` juntando a cor a um ícone W3C explícito (ex.: triângulo `LucideIcon`). |
| **2.4.7** | **Foco visível** | AA | Navegação por teclado / *switch* deve sempre mostrar um anel de foco. | Eliminar `outline: none` (*anti-pattern*). Forçar `focus:ring-2 focus:ring-blue-500 focus:outline-none` em todos os formulários e controlos. |

## Checklist de desenvolvimento
Antes de fazer *commit* de qualquer ecrã / componente (ex.: `ProfileSelector.jsx`), responder a estas 3 perguntas:
1. Tem pelo menos 44 px de alvo (Tailwind `h-11 w-11` ou superior)?
2. Consigo navegar todo o componente com `[TAB]` e ver um anel de foco claro?
3. Passa num teste de contraste contra o fundo (sem cinzas claros sobre branco)?
