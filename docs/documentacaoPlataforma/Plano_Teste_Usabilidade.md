# Plano de Testes de Usabilidade (CityFlow MVP)

Este documento define a grelha de observação empírica para testes de usabilidade em laboratório ou em *guerrilla testing* com utilizadores reais (ou estudantes a representar as personas estabelecidas).

O objetivo é medir o esforço cognitivo e a fricção da interface, não a matemática do backend (já validada em QA — ver `Cenarios_Teste_Aceitacao.md`).

A coluna **Estado** indica se o cenário foi efetivamente executado durante o desenvolvimento do MVP (✅) ou se ficou planeado para fases futuras (🔜).

## Cenários do MVP entregue

| Cenário de teste | Tarefa no frontend | Tempo esperado (*benchmark*) | Erros críticos a observar (*red flags*) | Critério de sucesso empírico | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **CT-01: Configuração inicial das restrições de perfil** | "Abre a aplicação. Configura-a para um utilizador em cadeira de rodas: até 8 % de inclinação, 1,2 m de largura mínima e a evitar escadas." | **< 30 segundos** | 1. O utilizador anda perdido pelo ecrã sem perceber onde estão os sliders.<br>2. Não percebe que o *toggle* azul é interativo.<br>3. Tenta clicar nos rótulos textuais. | O utilizador identifica os três controlos imediatamente, ajusta cada um, e percebe o valor numérico visível à direita. | ✅ |
| **CT-02: Definir uma rota e interpretar o resultado** | "Clica no mapa em dois pontos diferentes para definir partida e destino. Pressiona 'Calcular rota segura'. Diz-me o que entendes do resultado mostrado." | **< 45 segundos** | 1. O utilizador não percebe que tem de clicar no mapa para definir os pontos.<br>2. Não distingue o marcador azul (partida) do vermelho (destino).<br>3. Não interpreta o *badge* verde/vermelho da inclinação crítica. | O utilizador clica intuitivamente, percebe os marcadores, lê as três métricas (distância, tempo, inclinação) e identifica visualmente se o limite de conforto foi excedido. | ✅ |
| **CT-03: Trocar de cidade e reformular** | "Muda a cidade para Paris. Volta a definir uma rota nova. Diz-me se notas alguma diferença no comportamento da app." | **< 30 segundos** | 1. O utilizador não vê o dropdown "Cidade".<br>2. Ao trocar, espera que a rota anterior continue (não percebe que o estado se limpa). | O utilizador abre o dropdown sem dificuldade, escolhe Paris, vê o mapa voar para Châtelet e refaz o trajeto sem reler instruções. | ✅ |
| **CT-04: Recuperação de erro (clique inválido)** | "Clica no mapa fora da zona de cobertura ou numa zona sem ruas (ex.: floresta). Diz-me o que acontece." | **< 20 segundos** | 1. O utilizador interpreta o alerta vermelho como um *bug*.<br>2. Não percebe que o clique é simplesmente ignorado. | O utilizador lê o alerta, percebe o limite (250 m de proximidade à rua pedonal mais próxima) e clica novamente sem hesitar. | ✅ |

## Cenários planeados para a versão pós-MVP

Estes cenários dependem de funcionalidades ainda no *roadmap* (alto contraste, *crowdsourcing*, modo *Easy Read*):

| Cenário | Tarefa | Estado |
| :--- | :--- | :---: |
| **CT-05: Intervenção cidadã** | Reportar uma rua cortada em tempo real através de um botão massivo dedicado. | 🔜 |
| **CT-06: Modo Easy Read** | Seguir um itinerário com toda a interface oculta exceto a próxima manobra. | 🔜 |
| **CT-07: Alto contraste** | Ler a interface inteira numa palete escura adaptada para daltonismo. | 🔜 |

### Registo da sessão (investigadores IPC)
CT-01 a CT-04 devem ser cronometrados formalmente. Se o P90 (90.º percentil de utilizadores) exceder o *tempo esperado*, a interface volta à prancheta (refactoring de componentes). Os resultados dos testes presenciais conduzidos pelo grupo na fase de validação do MVP estão consolidados no anexo de testes do relatório académico.
