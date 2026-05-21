# Plano de Testes de Usabilidade (CityFlow MVP)

Este documento define a grelha de observação empírica para testes de usabilidade em laboratório ou em *guerrilla testing* com utilizadores reais (ou estudantes a representar as personas estabelecidas).

O objetivo é medir o esforço cognitivo e a fricção da interface, não a matemática do backend (já validada em QA).

| Cenário de teste | Tarefa no frontend | Tempo esperado (*benchmark*) | Erros críticos a observar (*red flags*) | Critério de sucesso empírico |
| :--- | :--- | :--- | :--- | :--- |
| **CT-01: Configuração inicial rápida das restrições** | "Abre a aplicação e configura-a para evitar escadas e pavimentos muito irregulares." | **< 20 segundos** | 1. O utilizador anda perdido pelo ecrã do mapa sem encontrar o ícone de perfil.<br>2. O utilizador fica confuso com a nomenclatura técnica (não percebe *inclinação* nem *piso*). | O utilizador encontra o menu de perfil por iniciativa própria, foca o slider base, ajusta, pressiona "Guardar" e regressa ao mapa visivelmente descansado sem questionar o moderador. |
| **CT-02: Intervenção cidadã em tempo real** | "Imagina que vais a andar e descobres um passeio aberto em obras. Avisa os outros utilizadores." | **< 10 segundos** | 1. Frustração temporal — o utilizador demora mais de 10 s a "procurar" o botão de alerta (sem destaque suficiente / não respeita o touch target WCAG).<br>2. *Miss-click* — o alerta é cancelado. | O olhar do utilizador desce para o botão primário vermelho no rodapé. O dedo acerta à primeira sem zoom. O utilizador lê o *toast* dinâmico "obstáculo mapeado". |
| **CT-03: Compreensão rápida da rota (Easy Read)** | (O utilizador recebe um telemóvel com modo de alto contraste ligado e uma rota pré-carregada.) "Segue as indicações e diz-me a próxima curva." | **< 15 segundos** | 1. Sobrecarga visual — o utilizador tenta ler todos os nomes de rua à volta da origem (*cognitive load*).<br>2. Dificuldade em distinguir a *polyline* geométrica do basemap por contrastes em conflito (violação 4.5:1). | O utilizador não hesita perante o ruído visual; foca a instrução isolada no topo e aponta fisicamente para a direção real ("Tenho de virar à direita aqui"), ativando mentalmente o processo motor. |

### Registo da sessão (investigadores IPC)
CT-01, CT-02 e CT-03 devem ser cronometrados formalmente. Se o P90 (90.º percentil de utilizadores) exceder o *tempo esperado*, a interface volta à prancheta (refactoring de componentes).
