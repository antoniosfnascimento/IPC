# Personas e Casos de Uso (CityFlow)

Com base nas funcionalidades diferenciadoras da aplicação **CityFlow** e da análise sociodemográfica aos públicos-alvo da disciplina de Interação Pessoa-Computador (IPC), as seguintes Personas representam os utilizadores críticos (Edge Cases) em torno dos quais a interface e o algoritmo de mapas foram construídos.

| Nome / Idade | Limitação Principal (Perfil) | Necessidade Primária na App (CityFlow) | Frustração Comum em Mapas Atuais (Google Maps/Apple Maps) |
| :--- | :--- | :--- | :--- |
| **João**, 34 anos | **Motora:** Cadeirante (Cadeira de Rodas Manual). | Caminhos com inclinação controlada e evasão rigorosa de passeios sem rebaixamento, escadas e pavimentos de terra solta. | Os mapas atuais mandam-no pelo caminho "Mais Rápido". Muitas vezes esse caminho inclui uma colina íngreme que lhe causa exaustão ou atira-o para ruas com calçada antiga impraticável e ele tem de recuar, desperdiçando energia. |
| **Maria**, 72 anos | **Sensorial (Visão Reduzida) e Física (Fadiga):** Idosa com cataratas parciais e que se desloca com o apoio de uma bengala. | Navegar com modo *Easy Read* (Interface Limpa), botões de grande escala, e priorizar distâncias planas que exijam pouco esforço respiratório. | As interfaces são confusas, cheias de informação desnecessária (restaurantes, hotéis). As letras são minúsculas. Os mapas não a avisam sobre obras no passeio (Crowdsourcing) que a obrigam a arriscar andar pela estrada. |
| **Ricardo**, 45 anos | **Cognitivo-Sensorial:** Daltónico (Deuteranopia - Dificuldade no eixo Verde/Vermelho). | Interpretar o mapa através de contrastes dinâmicos, padrões visuais óbvios ou *Feedback Háptico* (Vibração) quando erra a direção. | Linhas de rota vermelhas num mapa topo verde confundem-se totalmente. Não percebem logo a diferença gráfica entre uma via de trânsito rápido e uma rua pedonal secundária. Falta de multimodalidade para avisos de rotas alternativas. |

Estas Personas reforçam a justificação para a existência das variáveis `max_incline`, `avoid_stairs` e do modo *Easy Read*, além da funcionalidade extra do Crowdsourcing de obstáculos na via, que constituem as fundações do CityFlow.
