# OrbeIA — Guará 1: checklist de preparação do MVP

Atualizado em 16 de outubro de 2026.

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

## 3. Preparar o repositório

Estrutura local preparada em 16 de outubro de 2026. O Git foi inicializado na branch `main`; a conexão remota e o envio ainda não foram validados.

- [ ] Verificar a conexão deste repositório com o GitHub e se o envio funciona.
- [x] Preparar `.gitignore` para excluir `.venv`, `.env`, credenciais, pesos dos modelos e históricos pessoais.
- [x] Preparar os arquivos previstos: `README.md`, `Modelfile`, `app.py`, `tools.py`, `checks.json` e `requirements.txt`.
- [x] Registrar a origem Qwen3, a versão utilizada e sua licença em [modelo-base.md](modelo-base.md).
- [x] Documentar a regra de incluir em cada commit o trailer exigido, em sua própria linha final: `Co-authored-by: codex <codex@openai.com>`.
- [x] Criar `AGENTS.md` com contexto, escopo, organização, comandos, critérios de verificação e regras de versionamento.
- [x] Preparar `.gitmessage` com o trailer obrigatório.
- [ ] Ativar o template local com `git config --local commit.template .gitmessage`.

Verificações locais: o ponto de entrada `app.py` executou no `.venv`; `git check-ignore` confirmou a exclusão de ambiente, `.env`, credenciais, pesos, resultados e histórico. `app.py` apenas informa o estado inicial; o registro de ferramentas está vazio e os 20 casos ainda serão escritos. O `Modelfile` contém instruções iniciais, mas a criação e o teste de `guara1` permanecem na seção 4.

O remoto `origin` foi configurado em 16 de outubro de 2026 com a URL informada pelo responsável: `https://github.com/joaoferreira-dev/guara-1.git`. As URLs de busca e envio foram conferidas com `git remote -v`; a conexão e o envio ainda não foram validados. Na verificação anterior, o GitHub CLI encontrou a conta local, mas reportou sua credencial como inválida. A tentativa anterior de configurar o template foi impedida por falta de permissão de escrita em `.git/config`. Nenhum commit ou envio foi realizado. O arquivo `.gitmessage` está pronto para ativação.

O fluxo previsto é editar no ThinkPad, testar localmente, fazer commit e enviar ao GitHub. CI/CD não é requisito desta etapa.

## 4. Fechar as decisões mínimas da aplicação

Estes parâmetros precisam ser escolhidos antes ou no início da implementação.

- [ ] Escrever as instruções do Guará 1: identidade, português brasileiro, estilo de resposta e comportamento diante de incerteza.
- [ ] Definir limites iniciais de contexto, histórico e tamanho das respostas.
- [ ] Escolher como tratar o modo de raciocínio do Qwen e medir seu impacto na velocidade.
- [ ] Decidir se o histórico ficará apenas na sessão ou também em arquivo local.
- [ ] Definir comandos simples para sair e limpar a conversa.
- [ ] Definir o comportamento quando o Ollama estiver indisponível ou a chamada demorar demais.
- [ ] Preparar o `Modelfile` com a base escolhida e as instruções do assistente.
- [ ] Validar a criação com `ollama create guara1 -f Modelfile`.
- [ ] Testar a configuração com `ollama run guara1`.

Após editar o `Modelfile`, recriar a configuração no Ollama. Personalizar instruções e nome não modifica os pesos da base.

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
5. Validar uma chamada de ferramenta antes de ampliar a aplicação.
6. Completar o histórico e a segunda ferramenta.
7. Executar os 20 casos e documentar como iniciar o programa e suas limitações.

Qwen3-4B fica para comparação posterior, caso o desempenho permita. Interface gráfica, nuvem, banco dedicado, CI/CD e treinamento não são dependências deste MVP. LoRA/QLoRA só será avaliado após identificar uma necessidade concreta que instruções ou correções na aplicação não resolvam.

## Referências técnicas

- [Qwen3-1.7B no catálogo do Ollama](https://ollama.com/library/qwen3:1.7b).
- [Instalação e requisitos do Ollama no Windows](https://docs.ollama.com/windows).
- [Chamada de ferramentas no Ollama](https://docs.ollama.com/capabilities/tool-calling).

As referências foram consultadas durante a análise do plano. A documentação do Ollama informa pelo menos 4 GB de espaço para instalação, além do espaço dos modelos. Conferir os requisitos novamente se houver mudança de versão ou dificuldade de instalação.
