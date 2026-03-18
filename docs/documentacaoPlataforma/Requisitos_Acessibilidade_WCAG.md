# Tabela de Requisitos de Acessibilidade (WCAG 2.1) - MVP CityFlow

Este documento mapeia as diretrizes essenciais de acessibilidade web (WCAG 2.1) para as implementações técnicas diretas que a equipa de Frontend (React + Tailwind CSS) tem obrigatoriamente de cumprir no MVP. Os critérios focam-se nas Personas estabelecidas (Limitações Motoras, Baixa Visão e Daltonismo).

| ID | Critério WCAG 2.1 | Nível | Objetivo na App CityFlow | Implementação Técnica (React / Tailwind CSS) |
| :---: | :--- | :---: | :--- | :--- |
| **1.4.3** | **Contraste Mínimo** | AA | Garantir que a *Persona de Baixa Visão/Daltonismo* consegue ler textos de UI (menus, erros) sem esforço. | O rácio de contraste deve ser de **4.5:1**. Usar classes fixas utilitárias do Tailwind como `text-gray-900 bg-white` (Normal) ou `text-yellow-400 bg-gray-900` (Modo Alto Contraste). *Obrigatório validar paleta de cores primárias com ferramenta como WebAIM.* |
| **1.4.6** | **Contraste Aprimorado** | AAA | Garantir contraste exímio nos componentes vitais: Botão "Reportar Obstáculo" e "Calcular Rota". | O rácio de contraste deve ser superior a **7:1**. Ex: Fundo `bg-blue-700` com texto `text-white` pesado (`font-bold`). |
| **2.5.5** | **Tamanho do Alvo (Target Size)** | AAA | Prevenir "Miss-clicks" graves pela *Persona em Cadeira de Rodas* com tremores ou a andar em piso irregular. | Todos os elementos interativos (`<button>`, `<input>`, marcadores Leaflet) terão um **mínimo absoluto de 44x44 CSS pixels**. Implementação Tailwind: adicionar `min-h-[44px] min-w-[44px] p-4` em todos os botões clique. |
| **1.4.4** | **Redimensionamento de Texto** | AA | Permitir zoom pelo SO (Android/iOS) até 200% sem quebrar o layout da navegação ou ocultar texto. | Usar as unidades rem do Tailwind em vez de px rígidos (`text-base`, `text-lg`). O container pai não deve ter `overflow-hidden` sem scroll para evitar cortes nas instruções "Turn-by-turn" quando muito ampliadas. |
| **3.3.2** | **Rótulos e Instruções** | AA | Reduzir a carga cognitiva do utilizador ao inserir as coordenadas no motor de rotas. | `<input>` de Origem/Destino nunca pode depender apenas do `placeholder`. Requer `<label htmlFor="origem" className="sr-only">` para leitores de ecrã ou rótulo visível para a *Persona Idosa*. |
| **4.1.2** | **Nome, Função e Valor (ARIA)** | A | O estado de carregamento do botão (spin no Dijkstra) e alertas dinâmicos da viagem têm de ser lidos. | O componente de Spinner enquanto espera pela API deve ter `role="status" aria-live="polite"`. O botão de "Modo Easy Read" que abre e fecha precisa de `aria-expanded={isOpen}` no estado do React. |
| **1.3.3** | **Características Sensoriais** | A | Não depender exclusividade da cor na UI do Mapa (protegendo a *Persona Daltónica*). | Ao exibir um erro "Rua Cortada", a UI não pode usar apenas "O vermelho está cortado". O Tailwind tem de ter `flex items-center gap-2` juntando a cor a um Ícone W3C explícito (ex: triângulo de alerta `LucideIcon`). |
| **2.4.7** | **Foco Visível (Focus Visible)** | AA | Navegação pelo teclado ou dispositivos de switch adaptados quando o *touch* falha por fraqueza muscular. | Eliminar `outline: none` (anti-padrão). Obrigar ao uso da classe `focus:ring-2 focus:ring-blue-500 focus:outline-none` do Tailwind para todos os forms e controlos do CityFlow. |

## Resumo Dev: Check-list de Componente (Frontend)
Antes de os programadores do lado Web fazerem o *commit* de qualquer ecrã/componente (ex: `ProfileSelector.jsx`), devem responder a estas 3 perguntas:
1. Tem o tamanho de `44px` (Tailwind `h-11 w-11` ou superior)?
2. Posso navegar por ele todo só batendo com o `[TAB]` no teclado e vendo um anel de luz à volta dele?
3. Tem um contraste testado forte contra o fundo (não há cinzas claros sobre brancos)?
