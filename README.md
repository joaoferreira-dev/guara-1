# OrbeIA — Guará 1

Guará 1 é um assistente pessoal do projeto OrbeIA, baseado no Qwen3 e configurado para conversar em português brasileiro e utilizar ferramentas locais.

O MVP será executado no Windows pelo terminal, com Ollama e um programa Python. As ferramentas previstas são uma calculadora e a leitura de texto em uma pasta permitida. A configuração do assistente não altera os pesos do modelo.

## Estado atual

O ambiente local, Qwen3-1.7B e a configuração `guara1` no Ollama foram validados. O programa Python já conversa pelo terminal, com histórico curto apenas na sessão e `think: false`. Calculadora, leitura de arquivos e os 20 casos de avaliação ainda estão pendentes.

## Preparar o ambiente

Ambiente verificado: Windows 11, Python 3.9.13, Git 2.49.0.windows.1 e Ollama 0.40.5. A referência foi medida em CPU, num Ryzen 5 7535U com 16 GB de RAM.

Na raiz do projeto, usando PowerShell:

```powershell
# Criar apenas se o ambiente ainda não existir.
py -m venv .venv

# Usar o Python do ambiente sem precisar ativá-lo.
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe app.py
```

Não há dependências Python externas. Com o Ollama ativo e `guara1` criado conforme abaixo, o último comando abre a conversa. Use `/limpar` para apagar o histórico da sessão e `/sair` para encerrar. EOF e Ctrl+C também encerram o programa. As mensagens não são salvas pela aplicação.

Pedidos de arquivo reconhecidos, como `leia o arquivo README.md`, recebem uma mensagem fixa do Python: nenhum arquivo foi lido e a leitura está indisponível. `/arquivo` entra explicitamente nesse fluxo. Continuações reconhecidas, como `E como termina?`, recebem a mesma orientação sem consultar o modelo. Ao mudar de assunto, por exemplo com `teste` ou uma pergunta de matemática, a conversa retoma automaticamente. Os pedidos recusados e suas respostas entram no histórico curto, identificados como avisos da aplicação, sem representar leitura de conteúdo. `/conversar` e `/limpar` começam uma conversa com histórico e fatos da sessão vazios.

A primeira mensagem válida da sessão e contadores de respostas do modelo, recusas e falhas ficam em memória, separados do contexto curto. Perguntas reconhecidas como `O que perguntei na primeira vez nessa conversa?` e `O que você já fez nessa conversa?` são respondidas pelo Python com esses registros. A primeira mensagem permanece disponível após sair do contexto do modelo. Comandos de controle, entradas vazias e entradas inválidas não contam como mensagens da sessão; `/arquivo` registra o pedido e sua recusa. Não há transcrição completa de todos os turnos antigos, e outras formulações podem ser encaminhadas ao modelo.

O reconhecimento de referências comuns a arquivos, documentos, pastas, extensões e caminhos é conservador. Pode bloquear perguntas de programação sobre arquivos e não cobre toda formulação possível em linguagem natural. O fluxo explícito `/arquivo` é previsível; não se afirma proteção universal contra conteúdo inventado em conversa livre. Para ler de fato, ainda será necessário implementar a ferramenta com pasta permitida, validação de caminho e resultados verificáveis.

Instalar o [Ollama para Windows](https://docs.ollama.com/windows), mantê-lo ativo e conferir a base:

```powershell
ollama --version
ollama list
ollama run qwen3:1.7b
```

Se `ollama` não for reconhecido após a instalação, abrir um novo terminal. O executável também pode ser chamado diretamente:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
```

Não é necessário instalar o pacote Python `ollama`: a integração usa a API HTTP local e a biblioteca padrão.

## Configuração inicial do assistente

O `Modelfile` parte de `qwen3:1.7b`, limita o contexto a 2.048 tokens e a geração a 256 tokens. As instruções iniciais definem identidade, português brasileiro e transparência sobre a execução de ferramentas.

Antes da primeira conversa, criar a configuração; para testar diretamente pelo Ollama:

```powershell
ollama create guara1 -f Modelfile
ollama run guara1 --think=false
```

Recriar `guara1` após editar o arquivo. O modo sem raciocínio explícito foi escolhido após a comparação local e a aprovação do responsável. O Python envia `think: false` explicitamente em cada pedido; ao usar o CLI, passar `--think=false`. A aplicação também envia sua própria mensagem de sistema em cada chamada, reforçando identidade, capacidades indisponíveis e exemplos de recusa; essas instruções e o `Modelfile` devem permanecer coerentes. O CLI isolado não possui o bloqueio de fluxo implementado pelo Python.

Limites iniciais: até 1.000 caracteres por entrada, três pares de conversa e 2.400 caracteres no histórico e no pedido enviado, descartando pares antigos completos. A resposta final é limitada a 4.000 caracteres, além de 256 tokens gerados. O contexto do modelo é de 2.048 tokens; os limites de caracteres não são uma contagem exata de tokens, e o Ollama pode truncar entradas que excedam o contexto. Respostas que atingem o limite de geração recebem um aviso.

O timeout de conexão e leitura é de 30 segundos; ele não garante um prazo absoluto para toda a operação nem cancela a geração no servidor. Falhas de conexão, modelo ausente e respostas inválidas exibem orientação e são registradas como falhas da aplicação no histórico curto. Não há repetição automática. Cada mensagem encaminhada ao modelo faz uma chamada, sem ferramentas; comandos, recusas de leitura e respostas locais sobre a sessão não consultam o modelo. O modelo fica carregado por até dois minutos de inatividade, conforme `keep_alive`.

Para verificar a integração sem executar o modelo:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

## Medições e avaliação

Para repetir as medições da base no Windows, com o Ollama ativo:

```powershell
.venv/Scripts/python.exe scripts/validar_qwen.py

# Comparar com raciocínio ativado, mantendo os demais parâmetros.
.venv/Scripts/python.exe scripts/validar_qwen.py --think
```

Cada execução salva um JSON novo em `resultados/benchmarks/`, ignorado pelo Git. A referência inicial permanece em [docs/benchmarks](docs/benchmarks/README.md). Os tempos medidos são de respostas completas; a primeira chamada inclui carregamento quando não houver modelo em memória.

O script não executa o código produzido pelo modelo. O `checks.json` contém quatro regressões em PT-BR; os 20 casos completos ainda estão pendentes. A [regressão de leitura](docs/avaliacoes/regressao-leitura-20261016.json) registra o diálogo que antes produzia uma citação inventada. A [retomada automática](docs/avaliacoes/retomada-conversa-20261016.json) registra a correção para continuar conversando sem exigir um comando. A [memória da sessão](docs/avaliacoes/memoria-sessao-20261016.json) registra a primeira mensagem correta, as ações efetivamente registradas e o reset. Esses resultados validam os casos registrados, sem demonstrar aderência universal do modelo isolado.

A [comparação com raciocínio ativado](docs/benchmarks/comparacao-think-20261016.md) foi executada com o mesmo limite de 256 tokens. Matemática e código atingiram esse limite durante o raciocínio e não entregaram resposta final. O responsável aprovou manter `think: false`; um orçamento maior e instruções para raciocínio em português ainda precisam de avaliação própria.

## Arquivos

| Caminho | Finalidade |
| --- | --- |
| `AGENTS.md` | Contexto e regras para trabalhar no repositório |
| `Modelfile` | Base e instruções iniciais do Guará 1 |
| `app.py` | Conversa pelo terminal e integração com Ollama |
| `capabilities.py` | Fluxo de indisponibilidade de arquivos e estado das continuações |
| `session.py` | Primeira mensagem e contadores da sessão, com respostas factuais locais |
| `tests/test_app.py` | Verificações de limites, histórico, comandos e falhas da integração |
| `tests/test_capabilities.py` | Referências reconhecidas e transições do fluxo de arquivos |
| `tests/test_session.py` | Fatos da sessão preservados após descarte do contexto curto |
| `tools.py` | Registro inicial de ferramentas, ainda vazio |
| `checks.json` | Estrutura dos casos de avaliação |
| `requirements.txt` | Registro das dependências Python |
| `scripts/validar_qwen.py` | Medição local da base |
| `docs/benchmarks/` | Medições selecionadas para versionamento |
| `docs/modelo-base.md` | Origem, identificação e licença do modelo |

## Versionamento

Versionar código, configuração, documentação e referências revisadas. O `.gitignore` exclui ambientes, pesos, credenciais, conversas e resultados temporários. Revisar `git status --short` antes de adicionar arquivos.

Configurar o modelo local de mensagem de commit:

```powershell
git config --local commit.template .gitmessage
```

Todo commit deve terminar com `Co-authored-by: codex <codex@openai.com>`. O template não substitui a inclusão desse trailer ao usar `git commit -m`.

O Git local foi inicializado em `main`. O remoto `origin` está configurado como `https://github.com/joaoferreira-dev/guara-1.git`. O primeiro push foi concluído em 16 de outubro de 2026, com `main` acompanhando `origin/main`. O template local de commit está ativo e `.github/CODEOWNERS` define `@joaoferreira-dev` como responsável por todos os arquivos. Não há CI/CD neste MVP.

## Documentação

- [Plano do MVP](docs/OrbeIA-Guara-1-plano-MVP.md).
- [Checklist de preparação e progresso](docs/OrbeIA-Guara-1-checklist-preparacao.md).
- [Origem e licença da base](docs/modelo-base.md).

O modelo Qwen3-1.7B usa Apache-2.0. A licença do código deste projeto ainda não foi definida; ela é uma decisão separada da licença do modelo.
