# OrbeIA — Guará 1: checklist de preparação do MVP

Atualizado em 17 de outubro de 2026.

Base: [Plano do MVP](OrbeIA-Guara-1-plano-MVP.md).

O objetivo é preparar o desenvolvimento de um assistente pessoal em português brasileiro, com Qwen3 executado localmente pelo Ollama, um programa Python no terminal e duas ferramentas: calculadora e leitura de texto em uma pasta permitida.

Os itens marcados foram confirmados pelo responsável pelo projeto ou verificados localmente, conforme os registros de cada seção. Os demais representam trabalho pendente ou verificações ainda não registradas; não indicam necessariamente ausência de configuração.

## 1. Computador e ambiente

Etapa concluída. O ambiente virtual foi criado no projeto e verificado pelo CMD.

| Componente | Configuração informada |
| --- | --- |
| Processador | AMD Ryzen 5 7535U with Radeon Graphics, 2,90 GHz |
| RAM instalada | 16,0 GB; 14,8 GB utilizáveis |
| Placa gráfica | AMD Radeon(TM) Graphics, 995 MB informados pelo sistema |
| Armazenamento | 457 GB usados de 477 GB; aproximadamente 20 GB livres |
| Arquitetura | Sistema operacional de 64 bits, processador x64 |
| Sistema operacional | Windows 11 |

A quantidade de RAM utilizável não representa a memória livre durante a execução. Os 995 MB informados para a placa gráfica não devem ser interpretados como uma GPU dedicada disponível para o modelo. O planejamento continua priorizando CPU, conforme o MVP. O espaço livre deverá ser acompanhado durante os downloads.

- [x] Identificar o processador exato do ThinkPad.
- [x] Conferir a configuração de memória.
- [x] Conferir o armazenamento disponível.
- [x] Preparar Python, Git e um editor de código, conforme conclusão informada da etapa.
- [x] Criar o ambiente virtual `.venv` no projeto.
- [x] Registrar as versões de Python, Git e Ollama para reprodução do ambiente.

Versões verificadas: Python **3.9.13**, pip **22.0.4**, Git **2.49.0.windows.1** e Ollama **0.40.5**. O Python e o pip do `.venv` executaram corretamente; `pyvenv.cfg` confirma isolamento dos pacotes do sistema (`include-system-site-packages = false`).

Para ativar o ambiente no CMD, executar `.venv\Scripts\activate.bat`. Também é possível usar diretamente `.venv\Scripts\python.exe`, sem ativação. A criação foi feita com `py -m venv .venv`.

## 2. Validar o Qwen antes de construir a aplicação

Validação local concluída em 16 de outubro de 2026, entre 18:33 e 18:34 (America/Sao_Paulo). O modelo previsto já estava instalado; não foi necessário baixar outra variante. O limite de espera foi definido provisoriamente para permitir a avaliação e poderá ser ajustado à preferência pessoal.

- [x] Instalar o Ollama no Windows.
- [x] Executar o Qwen3 e realizar testes iniciais.
- [x] Registrar a versão do Ollama com `ollama --version`: **0.40.5**.
- [x] Confirmar a variante instalada e utilizada, consultando `ollama list`: **qwen3:1.7b**.
- [x] Validar a base prevista já instalada: execução real via API local do Ollama, sem download adicional.
- [x] Registrar a identificação e a quantização do modelo instalado: **8f68893c685c**, **Q4_K_M**, formato **GGUF**.
- [x] Registrar um teste de conversa em português brasileiro.
- [x] Registrar um problema com resposta conhecida.
- [x] Registrar uma tarefa pequena de código.
- [x] Medir o tempo da primeira resposta e das respostas seguintes.
- [x] Registrar o consumo aproximado de memória durante a execução.
- [x] Definir um limite provisório de espera: **até 30 segundos para uma resposta curta completa**, sujeito à preferência pessoal.

### Configuração e evidências

- Ollama: **0.40.5**; Python utilizado no teste: **3.9.13**.
- Modelo: `qwen3:1.7b`; metadados locais informam `parameter_size: 2.0B`, apesar do nome da variante. Mantida a identificação oficial da tag.
- Digest completo: `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`.
- Arquivo instalado: **1.359.293.444 bytes**, aproximadamente **1,36 GB**.
- Execução: API `http://localhost:11434/api/chat`, sem streaming; tempo medido até receber a resposta completa, não até o primeiro token.
- Parâmetros: `think: false`, `num_ctx: 2048`, `num_predict: 256`, `temperature: 0`, `seed: 42`.
- Nenhum modelo carregado no início da rodada registrada. As três chamadas seguintes reutilizaram o modelo carregado. Apenas a segunda chamada recebeu o histórico da primeira; os testes de matemática e código foram independentes.
- A API informou `size_vram: 0`, compatível com execução pela CPU nesta rodada.
- O comando `ollama` não estava no PATH da sessão de automação. A versão e a lista foram verificadas com o executável em `%LOCALAPPDATA%\Programs\Ollama\ollama.exe`. Isso não exige reinstalação.
- Não foi possível inventariar os aplicativos abertos pelas permissões desta sessão. O teste ocorreu com a carga de uso existente, sem fechar programas; essa condição limita comparações futuras.

### Resultados

| Teste | Tempo total observado | Carregamento informado pelo Ollama | Tokens gerados | Resultado |
| --- | --- | --- | --- | --- |
| Conversa em PT-BR, primeiro pedido | 7,76 s | 2,820 s | 49 | Resposta em português, em duas frases |
| Continuidade da conversa | 2,77 s | 0,006 s | 2 | Identificou corretamente a linguagem: Python |
| Problema com desconto e frete | 11,76 s | 0,009 s | 167 | Resultado correto: R$ 56,60; excedeu as três linhas solicitadas |
| Função Python `soma_pares` | 4,31 s | 0,005 s | 30 | Código revisado e executado: seis casos aprovados |

Os tempos totais incluem a chamada HTTP local. Os tempos internos totais informados pelo Ollama foram, respectivamente, 5,721 s, 0,703 s, 9,688 s e 2,271 s; não devem ser confundidos com o tempo percebido pelo cliente. A geração nas respostas mais longas ficou aproximadamente entre 17,7 e 19,1 tokens/s. Todas as respostas terminaram com `done_reason: stop`, sem atingir o limite de geração.

Pedidos, respostas completas, histórico enviado, tempos internos, contagens de tokens, medições de memória e verificações do código estão no [registro JSON da validação](benchmarks/validacao-qwen-secao-2.json).

Verificações realizadas:

- Conversa: orientação inicial para aprender Python, com avaliação do idioma e do limite de duas frases. As recomendações externas presentes na resposta não foram verificadas.
- Continuidade: pergunta sobre a linguagem mencionada no turno anterior; resposta esperada e obtida: `Python`.
- Matemática: `3 × 18 × 0,9 + 8 = 56,60`. Acertou o cálculo, com falha no limite de extensão solicitado.
- Código: soma de pares com lista vazia, mistura de pares e ímpares, negativos, zero, apenas ímpares e valores repetidos. As seis saídas coincidiram com as esperadas.

### Memória e decisão inicial

A memória física do Windows foi amostrada aproximadamente a cada 250 ms durante as chamadas. Valores em GiB (1 GiB = 1.073.741.824 bytes):

| Medida | Valor aproximado |
| --- | --- |
| RAM utilizável informada pelo Windows | 14,78 GiB |
| RAM total em uso antes da primeira chamada | 12,40 GiB |
| Pico observado de RAM total em uso durante a rodada | 14,04 GiB |
| RAM disponível no pico observado | 0,74 GiB |
| Tamanho do modelo carregado informado por `/api/ps` | 1,54 GiB |

O aumento observado de aproximadamente 1,64 GiB na memória total do sistema inclui variações de outros processos; não representa uma medição isolada do processo Ollama. O tamanho informado pela API também não é o consumo total de todos os processos do executor. O pico amostrado pode não capturar variações inferiores ao intervalo de medição.

**Decisão inicial:** manter Qwen3-1.7B, contexto de 2.048 tokens e respostas limitadas. A execução foi suficiente para iniciar o desenvolvimento, com todas as chamadas abaixo do limite provisório de 30 segundos. A pouca memória livre nesta condição de uso recomenda fechar aplicativos desnecessários antes de aumentar o contexto ou comparar com 4B. Esta rodada curta não valida desempenho em conversas longas nem o funcionamento de ferramentas.

Para reproduzir as medições, executar `py scripts/validar_qwen.py` na raiz do projeto com o Ollama ativo. O script usa apenas a biblioteca padrão e cria um JSON com data e hora em `resultados/benchmarks/`, pasta ignorada pelo Git. A referência inicial em `docs/benchmarks/` permanece preservada. O script registra se havia um modelo carregado inicialmente; repetir com modelo já carregado não representa partida a frio. A revisão dos resultados e os seis casos de código registrados na referência inicial foram feitos separadamente após a geração e precisam ser refeitos para cada nova referência. As orientações para selecionar e versionar novas medições estão em [docs/benchmarks](benchmarks/README.md).

### Comparação com raciocínio ativado

Em 16 de outubro de 2026, entre 19:07 e 19:09 (America/Sao_Paulo), os quatro pedidos foram repetidos com `think: true`, mantendo modelo, digest e demais parâmetros. Nenhum modelo estava carregado inicialmente. Tempos: conversa 14,26 s, continuidade 13,51 s, matemática 17,26 s e código 17,55 s. A continuidade acertou Python; a conversa excedeu duas frases. Matemática e código atingiram 256 tokens durante o raciocínio e não produziram resposta final. O raciocínio foi predominantemente em inglês, sem instrução específica para alterar seu idioma.

O total passou de 26,60 s para 62,58 s. O pico de memória do sistema foi 13,34 GiB, partindo de 11,82 GiB em uso; a diferença de carga inicial impede atribuir o pico menor ao modo de raciocínio. Resultados e ressalvas estão na [comparação revisada](benchmarks/comparacao-think-20261016.md) e no [JSON da nova rodada](benchmarks/validacao-qwen-think-20261016.json). A referência inicial foi preservada. Após avaliar a comparação, o responsável aprovou manter `think: false` com o orçamento atual, conforme seção 4; orçamento maior e instrução de idioma não foram testados.

## 3. Preparar o repositório

Estrutura local preparada em 16 de outubro de 2026. O Git foi inicializado na branch `main`; a conexão remota e o primeiro envio foram validados na mesma data.

- [x] Verificar a conexão deste repositório com o GitHub e se o envio funciona.
- [x] Preparar `.gitignore` para excluir `.venv`, `.env`, credenciais, pesos dos modelos e históricos pessoais.
- [x] Preparar os arquivos previstos: `README.md`, `Modelfile`, `app.py`, `tools.py`, `checks.json` e `requirements.txt`.
- [x] Registrar a origem Qwen3, a versão utilizada e sua licença em [modelo-base.md](modelo-base.md).
- [x] Documentar a regra de incluir em cada commit o trailer exigido, em sua própria linha final: `Co-authored-by: codex <codex@openai.com>`.
- [x] Criar `AGENTS.md` com contexto, escopo, organização, comandos, critérios de verificação e regras de versionamento.
- [x] Preparar `.gitmessage` com o trailer obrigatório.
- [x] Ativar o template local com `git config --local commit.template .gitmessage`.
- [x] Adicionar `.github/CODEOWNERS` com `* @joaoferreira-dev`.

Verificações na preparação inicial: o ponto de entrada `app.py` executou no `.venv`; `git check-ignore` confirmou a exclusão de ambiente, `.env`, credenciais, pesos, resultados e histórico. Naquele momento, `app.py` apenas informava o estado inicial. A implementação posterior da conversa e a validação de `guara1` estão registradas na seção 4; o registro de ferramentas permanece vazio e os 20 casos ainda serão escritos.

O remoto `origin` foi configurado em 16 de outubro de 2026 com a URL informada pelo responsável: `https://github.com/joaoferreira-dev/guara-1.git`. As URLs de busca e envio foram conferidas com `git remote -v`. Na revisão para o primeiro push, `git ls-remote origin` confirmou o acesso e o remoto vazio; o GitHub CLI confirmou o repositório público. O commit inicial `f61efd4` foi enviado com `git push -u origin main`, configurando o acompanhamento de `origin/main`. O template local `.gitmessage` foi ativado. As limitações de credencial e permissão registradas na verificação anterior foram superadas nesta execução autorizada.

Revisão anterior ao envio: `app.py` executou no `.venv`, os três arquivos Python passaram em `compileall`, os dois JSONs foram carregados com sucesso e `git diff --cached --check` não encontrou problemas. As exclusões de ambiente, credenciais, pesos, resultados e conversas foram conferidas; a busca por padrões comuns de credenciais não encontrou ocorrências nos arquivos revisados. A referência de benchmark foi preservada, sem repetir as chamadas ao modelo. A estrutura está apta ao versionamento inicial; a aplicação e a avaliação completa continuam pendentes.

O fluxo previsto é editar no ThinkPad, testar localmente, fazer commit e enviar ao GitHub. CI/CD não é requisito desta etapa.

## 4. Fechar as decisões mínimas da aplicação

Etapa concluída em 17 de outubro de 2026, conforme confirmação do responsável, incluindo a interface de terminal da seção 4.1. Decisões iniciais definidas e conversa mínima implementada em 16 de outubro de 2026. O responsável aprovou `think: false` após comparar as duas rodadas.

- [x] Escrever as instruções do Guará 1: identidade, português brasileiro, estilo de resposta e comportamento diante de incerteza.
- [x] Definir limites iniciais de contexto, histórico e tamanho das respostas.
- [x] Escolher como tratar o modo de raciocínio do Qwen e medir seu impacto na velocidade.
- [x] Decidir se o histórico ficará apenas na sessão ou também em arquivo local.
- [x] Definir comandos simples para sair e limpar a conversa.
- [x] Definir o comportamento quando o Ollama estiver indisponível ou a chamada demorar demais.
- [x] Preparar o `Modelfile` com a base escolhida e as instruções do assistente.
- [x] Validar a criação com `ollama create guara1 -f Modelfile`.
- [x] Testar a configuração com `ollama run guara1 --think=false`.

Implementação: `app.py` chama `/api/chat` com `think: false`, contexto de 2.048 tokens, até 256 tokens gerados, temperatura 0 e seed 42. Aceita entradas de até 1.000 caracteres e guarda no máximo três pares de conversa em memória. O histórico e o pedido enviado respeitam 2.400 caracteres, removendo pares antigos completos; isso não substitui uma contagem exata de tokens. O cliente limita a resposta HTTP a 64 KiB e o texto final a 4.000 caracteres. Os comandos são `/limpar` e `/sair`; EOF e Ctrl+C encerram a sessão.

O timeout de conexão e leitura é de 30 segundos, sem garantir um prazo absoluto para a operação inteira ou cancelamento da geração no servidor. Erros HTTP, modelo ausente, indisponibilidade, timeout e respostas inválidas geram orientação e entram no histórico como falhas da aplicação. Mensagens encaminhadas ao modelo fazem uma chamada, sem ferramentas nem repetição automática; recusas e consultas locais sobre a sessão não fazem chamadas. `keep_alive` é de dois minutos.

Verificação: nove testes com respostas simuladas passaram, cobrindo o pedido sem raciocínio, histórico, comandos, entradas inválidas, limites, respostas inválidas e falhas de rede. O terminal foi executado com dois pedidos sintéticos, `/limpar` e `/sair`: respondeu em português, lembrou Python e encerrou sem erro. O registro local inicial está em `resultados/validacao-conversa.json`. A continuidade respondeu `Python.` (pontuação adicional ao nome pedido); trata-se de limitação de formato do modelo.

No primeiro teste de apresentação pelo CLI, o modelo usou a expressão ambígua “treinado para ajudar”. As instruções foram reforçadas para explicitar a base Qwen3 e a ausência de treinamento pelo OrbeIA. Após recriar `guara1`, o mesmo teste retornou: “Sou Guará 1, assistente pessoal do projeto OrbeIA, baseado no Qwen3.” Isso confirma esse caso, sem garantir cumprimento de identidade em todos os pedidos. Os 20 casos completos continuam pendentes.

Uma rodada intermediária mostrou apresentação indevida em resposta a um pedido sobre aprender Python. A regra de apresentação foi restringida a solicitações explícitas. Na configuração final, três pedidos pelo terminal, com `/limpar` antes da apresentação e `/sair` ao final, concluíram em 13,02 s no total: dica sobre Python, continuidade `Python.` e apresentação correta. A dica chamou `input()` de “biblioteca”, uma imprecisão técnica: é uma função embutida. Essas falhas são do conteúdo do modelo, sem erro de integração observado. O registro local final está em `resultados/validacao-conversa-20261016-191615.json`. O modelo foi descarregado após os testes. Este teste curto não valida conversas longas nem substitui a avaliação completa.

Após editar o `Modelfile`, recriar a configuração no Ollama. Personalizar instruções e nome não modifica os pesos da base.

### Correção de alegação de leitura sem evidência

O responsável encontrou uma falha: ao pedir resumo de `README.md` e depois sua última frase, o modelo alegou acesso e inventou uma citação. A aplicação não tinha lido o arquivo. A orientação no `Modelfile` não foi suficiente, e a validação da resposta verificava somente estrutura, tamanho e falhas da API.

A correção mantém a leitura indisponível e adiciona um fluxo controlado pelo Python em `capabilities.py`. `/arquivo` ou uma referência reconhecida a arquivos responde que nenhum arquivo foi lido. Continuações reconhecidas recebem a mesma orientação sem chamadas ao modelo. Ao mudar de assunto, a conversa retoma automaticamente. Os pedidos recusados agora entram no histórico curto, identificados como respostas da aplicação, conforme o ajuste de memória abaixo. `/conversar` e `/limpar` permitem limpar estado, histórico e fatos da sessão. A função `chat` rejeita pedidos de arquivo reconhecidos e continuações reconhecidas após uma recusa registrada pela aplicação. As instruções do Python e do `Modelfile` reforçam a ausência de acesso e a regra de que afirmações anteriores do assistente não comprovam leitura.

O reconhecimento em linguagem natural é conservador, pode recusar perguntas legítimas sobre programação com arquivos e não cobre toda paráfrase possível. O modo explícito `/arquivo` possui comportamento definido; não se promete que o modelo deixe de inventar conteúdo em qualquer conversa livre ou no CLI isolado. A ferramenta futura precisará vincular conteúdo e citações a uma leitura real validada pelo Python, com pasta permitida. Nenhuma ferramenta foi habilitada nesta correção.

Verificação inicial em 16 de outubro de 2026: o diálogo original e a continuação “E como termina?” receberam três recusas fixas, sem conteúdo inventado. Após `/conversar`, uma chamada real ao modelo respondeu `4` para `2 + 2`; o processo encerrou sem erro. O registro histórico está em [regressao-leitura-20261016.json](avaliacoes/regressao-leitura-20261016.json).

O responsável observou depois que mensagens como `teste` ficavam presas no aviso de leitura. O estado foi ajustado para reconhecer continuações comuns e retomar automaticamente em outro assunto, preservando o contexto anterior. Na primeira rodada após esse ajuste, o modelo ainda repetiu limitações em resposta a `teste`, mesmo recebendo a mensagem pela API. A mensagem de sistema foi reduzida e passou a orientar explicitamente mudanças de assunto. Na rodada final, leitura e “E como termina?” receberam recusas; duas mensagens `teste` receberam confirmação normal, e `2 + 2` recebeu `4`, sem comandos intermediários, em 9,68 s no total. Evidência: [retomada-conversa-20261016.json](avaliacoes/retomada-conversa-20261016.json). `guara1` foi recriado com as instruções atualizadas. Os 20 testes de integração passaram, incluindo preservação de contexto e retorno automático; eles não substituem os 20 casos de avaliação do MVP. `checks.json` contém três regressões em PT-BR. A avaliação completa e as ferramentas seguem pendentes.

### Memória factual da sessão

O responsável encontrou outra falha: após leitura recusada, teste e saudação, o modelo inventou qual teria sido a primeira pergunta. O pedido recusado não estava registrado no histórico, e o filtro por palavras excluía pares legítimos que mencionassem arquivos. O contexto curto também não poderia preservar indefinidamente o início da conversa.

O filtro por palavras foi removido. Todos os turnos válidos, incluindo recusas e falhas de integração, entram no contexto curto; respostas locais carregam origem explícita, serializada como aviso ou fato da aplicação, sem representar resultado de ferramenta. `session.py` mantém separadamente a primeira mensagem válida e contadores de respostas do modelo, recusas, respostas locais e falhas. Consultas reconhecidas sobre a primeira mensagem e as ações da sessão recebem respostas extraídas desses registros pelo Python. A primeira mensagem permanece disponível após o descarte dos pares antigos; não é armazenada uma transcrição completa. Comandos de controle e entradas inválidas não contam; `/arquivo` registra a tentativa recusada. `/limpar` e `/conversar` redefinem também esses fatos.

Verificação em 16 de outubro de 2026: 26 testes passaram, incluindo preservação do início após dez turnos, origem dos avisos, manutenção de mensagens legítimas com referências a arquivos e reset. A sequência do responsável foi repetida pelo terminal, com Ollama real: leitura recusada, `teste`, `Olá`, resumo factual e primeira mensagem literal correta. Após `/limpar`, uma nova saudação passou a ser identificada como a primeira mensagem. O processo encerrou sem erro, em 13,34 s no total. Evidência revisada: [memoria-sessao-20261016.json](avaliacoes/memoria-sessao-20261016.json). `checks.json` contém quatro regressões em PT-BR; as demais tarefas e a avaliação completa continuam pendentes. As consultas reconhecidas são limitadas, e as demais respostas do modelo ainda exigem avaliação de conteúdo e idioma.

## 4.1. Interface de terminal estruturada

Etapa concluída em 17 de outubro de 2026, conforme confirmação do responsável. Incluída por solicitação do responsável para oferecer entrada fixa na parte inferior, respostas no corpo e identificação do modelo no canto inferior esquerdo. A implementação permanece neste repositório.

- [x] Separar o desenho da tela do núcleo de conversa, compartilhando memória, comandos e erros.
- [x] Implementar tela cheia com campo de mensagem fixo e área de conversa com rolagem.
- [x] Exibir `guara1 · Qwen3-1.7B` no rodapé esquerdo e estado de espera à direita.
- [x] Permitir envio por Enter, nova linha por Shift+Enter e edição de texto.
- [x] Manter a interface responsiva durante chamadas ao Ollama, limitando a um pedido por vez.
- [x] Permitir saída por Ctrl+C ou `/sair`, inclusive durante a espera.
- [x] Preservar modo simples com `--texto` e para entrada/saída redirecionada.
- [x] Verificar renderização em 80×24, 120×36 e 40×12 e executar uma chamada real na interface.
- [x] Conferir manualmente aparência, fonte, colagem e atalhos na janela de terminal usada pelo responsável (conclusão informada pelo responsável em 17 de outubro de 2026).

Implementação: `terminal_ui.py` usa prompt_toolkit 3.0.52, registrado em `requirements.txt` e instalado no `.venv` com Python 3.9.13. `app.py` oferece o núcleo `Conversation` usado pelas duas interfaces. A entrada cresce conforme o texto, até oito linhas ou o espaço disponível, com respiro vertical e marcador centralizado. PgUp/PgDn e roda do mouse rolam a conversa; Ctrl+End volta ao final. A área visual mantém até 40.000 caracteres em memória. O contexto do modelo e os fatos da sessão continuam separados dessa área visual. Respostas aparecem completas, sem streaming. O modelo exibido é o configurado; ainda não há seletor. A saída durante espera não garante cancelamento da geração no Ollama.

Verificação: testes reais de teclado e renderizador com entrada por pipe validaram posições do rodapé e campo, quebra de linha, envio, recusa de leitura, retomada, limpeza, rolagem e Ctrl+C durante uma espera simulada. A primeira verificação identificou que o campo crescia para quatro linhas; sua altura foi fixada em duas e os testes passaram. O script `.venv/Scripts/python.exe scripts/validar_cli.py --real` fez uma chamada ao Ollama, obteve `4` para `2 + 2` e recuperou a primeira mensagem pelo núcleo factual. A [evidência revisada](avaliacoes/cli-terminal-20261016.json) contém grades do renderizador; não são screenshots de uma janela Windows Terminal. A conclusão da conferência manual foi informada pelo responsável em 17 de outubro de 2026. Essa etapa não habilita ferramentas nem conclui os 20 casos do MVP.

### Ajustes visuais solicitados pelo responsável

Removido o fundo próprio da tela para preservar o fundo configurado no terminal. O destaque de fundo ficou restrito à caixa de entrada e às mensagens do usuário, com a mesma cor. Os nomes de remetente foram removidos das mensagens exibidas; a origem continua registrada internamente para os fatos da sessão. A caixa agora cresce com novas linhas e quebras automáticas, até oito linhas ou o espaço disponível. O marcador `>` foi separado da edição e centralizado verticalmente entre linhas de respiro.

Verificação: testes do renderizador confirmam fundo padrão fora das mensagens, cores iguais na entrada e mensagem enviada, ausência de rótulos, expansão e contração da caixa, posição do marcador e rodapé preservado. A captura com `.venv/Scripts/python.exe scripts/validar_cli.py --amostra` usa mensagens sintéticas e entrada de três linhas, sem executar o modelo; em 40×12 o campo respeita o espaço disponível. Evidência revisada: [cli-ajustes-visuais-20261016.json](avaliacoes/cli-ajustes-visuais-20261016.json). A conferência da aparência na janela real foi dada como concluída pelo responsável em 17 de outubro de 2026.

### Marcador nas mensagens e indicação de atividade

O marcador `>` também aparece no início das mensagens enviadas pelo usuário, mantendo o fundo destacado e sem nomes de remetente. Durante um pedido, uma linha acima da entrada mostra `Trabalhando…`, indicador animado e segundos decorridos. O redesenho ocorre a cada 120 ms, sem chamadas extras ao modelo ou alteração de `think: false`. O indicador desaparece após resposta ou erro. É possível editar um rascunho durante a espera; continua permitido apenas um pedido por vez. Em telas pequenas, a altura da entrada considera o espaço ocupado pela indicação de atividade.

Verificação: testes com espera simulada conferem o indicador no renderizador, mudança de quadro da animação, manutenção do rodapé, edição durante espera e remoção do indicador tanto no sucesso quanto na falha. O teste de mensagem enviada verifica o marcador sem introduzi-lo na mensagem original registrada pela sessão. A validação de saída por Ctrl+C durante espera permanece ativa. Nenhuma medição de inferência foi repetida para esses ajustes de apresentação.

### Shift+Enter para nova linha

Estado atual: o responsável confirmou falha no PowerShell integrado do VS Code, executando `guara`: Shift+Enter envia e Ctrl+J oculta o painel. A configuração inspecionada do Windows Terminal não se aplica a esse terminal. A configuração específica do VS Code ainda não foi aplicada, e o funcionamento físico nesse ambiente permanece pendente; os testes automatizados não substituem essa confirmação.

Compatibilidade com a configuração local do Windows Terminal: o atalho Shift+Enter envia ESC + CR, que a interface agora reconhece como nova linha. A reprodução automatizada confirma que a entrada permanece no editor sem chamar o modelo, a caixa cresce e Enter envia depois a mensagem completa com duas linhas. Essa sequência também pode ser produzida por Alt+Enter. O teste usa entrada por pipe; a confirmação com o teclado físico continua pendente.

Correção posterior: o prompt_toolkit podia selecionar o leitor VT no Windows e deixar de usar o adaptador de Shift+Enter. `guara/terminal/keys.py` agora seleciona o leitor de eventos nativos e desativa a entrada VT nesse caminho, preservando o modificador. Os 45 testes passaram, incluindo a seleção do leitor, eventos Windows sintéticos e inserção de nova linha na interface. A confirmação com o teclado no terminal do usuário permanece pendente.

Atalho alterado para Shift+Enter; Enter continua enviando a mensagem. `terminal_keys.py` preserva o modificador nos eventos nativos do Windows e reconhece as sequências CSI-u e modifyOtherKeys, convertendo-as no evento de nova linha usado pela interface. O adaptador é específico da versão 3.0.52 do prompt_toolkit e deve ser revalidado ao atualizar a dependência. Ctrl+J também insere nova linha quando o terminal não distingue Shift+Enter de Enter. Dicas e documentação foram atualizadas. Os 39 testes passaram, incluindo eventos Windows sintéticos, parser VT e inserção de múltiplas linhas sem envio antecipado.

### Nome exibido e sugestões de comandos

O rodapé passou a exibir `Guará-1 · Qwen3-1.7B`; o identificador usado no Ollama continua sendo `guara1`. Ao digitar `/` no início da entrada, uma caixa de sugestões mostra os quatro comandos disponíveis com suas descrições e filtra pelo prefixo. Setas selecionam, Tab completa, Esc fecha e Enter confirma a seleção ou executa o comando completo. O menu não oferece operações inexistentes nem dispara chamadas ao modelo ao completar. Testes do renderizador e teclado verificam abertura, filtragem, preenchimento, seleção, fechamento e manutenção do rodapé, incluindo terminal pequeno.

### Comando global no usuário Windows

O comando `guara` foi instalado para abrir a CLI a partir de qualquer pasta, sem ativar o ambiente. `scripts/instalar_comando.ps1` cria um lançador em `%LOCALAPPDATA%\Programs\OrbeIA\bin` com os caminhos do `.venv` e do ponto de entrada, e acrescenta essa pasta ao PATH do usuário sem substituir as entradas existentes. Não altera o PATH da máquina nem sobrescreve outro comando `guara`. O instalador oferece `-WhatIf` e pode ser executado novamente após mover o repositório.

Verificação em 16 de outubro de 2026: simulação com `-WhatIf`, instalação real autorizada e resolução do comando com o PATH persistido. A partir da pasta temporária do Windows, `guara --help` e `guara --texto` com `/sair` encerraram com código zero, sem ativar o `.venv` nem fazer inferência. Terminais já abertos precisam ser reiniciados para carregar a alteração de PATH.

### Organização do código em pacote

Os módulos Python foram retirados da raiz e organizados em `guara/`: `cli.py` e `__main__.py` selecionam a interface; `core/` contém conversa, integração HTTP, capacidades e memória; `terminal/` contém tela e teclado; `tools/` reserva o registro das ferramentas. Os scripts operacionais permanecem em `scripts/`, os testes em `tests/` e os documentos em `docs/`. Referências a nomes antigos nos registros históricos descrevem a organização usada naquelas execuções.

A entrada do pacote é `.venv/Scripts/python.exe -m guara`, executada na raiz. O comando global `guara` usa `scripts/iniciar_guara.py`, que localiza o pacote sem depender da pasta atual. O instalador e o lançador já instalado foram atualizados. Imports e alvos de substituição dos testes foram ajustados sem mudar contratos da conversa ou os parâmetros do modelo. O comando global foi validado a partir da pasta temporária do Windows com `--help` e `/sair` no modo simples; as evidências e benchmarks anteriores foram preservados.

## 5. Especificar e testar as duas ferramentas

- [ ] Definir as operações aceitas pela calculadora e seus argumentos.
- [ ] Prever divisão por zero e entradas inválidas, sem executar texto arbitrário como código.
- [ ] Escolher a pasta permitida para leitura.
- [ ] Criar arquivos de teste sem dados pessoais nessa pasta.
- [ ] Definir formatos aceitos, codificação e tamanho máximo dos arquivos.
- [ ] Garantir que caminhos resolvidos permaneçam dentro da pasta permitida.
- [ ] Definir os contratos das ferramentas e validar os argumentos no Python.
- [ ] Fazer uma prova mínima de chamada de ferramenta com Qwen3-1.7B.
- [ ] Confirmar o fluxo completo: solicitação pelo modelo, execução pelo Python, retorno do resultado ao modelo e resposta final.
- [ ] Limitar o número de chamadas por interação para evitar ciclos.

A prova de integração deve ocorrer cedo. O suporte a ferramentas não garante que o modelo pequeno selecione corretamente a função ou seus argumentos em todas as tarefas. A aplicação deve executar somente as funções cadastradas e validar cada chamada.

## 6. Preparar a avaliação antes de desenvolver

- [ ] Escrever cinco casos de conversa e instruções em português brasileiro.
- [ ] Escrever cinco problemas com respostas conhecidas.
- [ ] Escrever cinco exercícios pequenos de código.
- [ ] Escrever cinco tarefas com ferramentas.
- [ ] Registrar a resposta esperada ou o critério de aprovação de cada caso.
- [ ] Incluir nas tarefas com ferramentas uma tentativa de leitura fora da pasta permitida e argumentos inválidos.
- [ ] Preparar o registro de sucesso, falha e tempo aproximado.
- [ ] Definir como distinguir limitações do modelo de erros da integração.
- [ ] Documentar o critério de conclusão: iniciar o programa, manter contexto, executar as duas ferramentas e repetir a avaliação sem erros que impeçam o uso.

Conferir respostas de problemas, executar o código quando possível e verificar a operação real das ferramentas. Os 20 casos avaliam a utilidade pessoal do MVP; não demonstram superioridade geral sobre outros modelos.

## Ordem recomendada de execução

1. Criar o `.venv` e registrar as versões do ambiente.
2. Confirmar a variante do Qwen3 e repetir alguns testes com registro de tempo e memória.
3. Preparar o repositório e as instruções do Guará 1.
4. Implementar uma conversa mínima em Python.
5. Implementar e conferir a interface de terminal da seção 4.1, preservando o núcleo validado.
6. Validar uma chamada de ferramenta antes de ampliar a aplicação.
7. Completar o histórico e a segunda ferramenta.
8. Executar os 20 casos e documentar como iniciar o programa e suas limitações.

Qwen3-4B fica para comparação posterior, caso o desempenho permita. Interface gráfica, nuvem, banco dedicado, CI/CD e treinamento não são dependências deste MVP. LoRA/QLoRA só será avaliado após identificar uma necessidade concreta que instruções ou correções na aplicação não resolvam.

## Referências técnicas

- [Qwen3-1.7B no catálogo do Ollama](https://ollama.com/library/qwen3:1.7b).
- [Instalação e requisitos do Ollama no Windows](https://docs.ollama.com/windows).
- [Chamada de ferramentas no Ollama](https://docs.ollama.com/capabilities/tool-calling).

As referências foram consultadas durante a análise do plano. A documentação do Ollama informa pelo menos 4 GB de espaço para instalação, além do espaço dos modelos. Conferir os requisitos novamente se houver mudança de versão ou dificuldade de instalação.

### Marcador da entrada no topo

O marcador `>` permanece alinhado à primeira linha de texto quando a caixa cresce, preservando o respiro superior. Os 15 testes da interface passaram, incluindo a posição do marcador na entrada com três linhas.
