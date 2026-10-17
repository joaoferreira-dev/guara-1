# OrbeIA — Guará 1

Guará 1 é um assistente pessoal do projeto OrbeIA, baseado no Qwen3 e configurado para conversar em português brasileiro e utilizar ferramentas locais.

O MVP será executado no Windows pelo terminal, com Ollama e um programa Python. A única ferramenta do MVP é a leitura de texto, limitada à pasta em que o terminal iniciou o Guará; caminhos externos exigem autorização explícita por leitura. A configuração do assistente não altera os pesos do modelo.

## Estado atual

O ambiente local, Qwen3-1.7B e a configuração `guara1` no Ollama foram validados. O programa Python conversa por uma interface de terminal em tela cheia, com entrada fixa na parte inferior, respostas no corpo e modelo no canto inferior esquerdo. O histórico permanece apenas na sessão e `think: false` está ativo. A leitura de texto e o fluxo de autorização externa estão implementados e validados com o Qwen3 real. A calculadora foi retirada do escopo por decisão do responsável. Os 20 casos completos de avaliação ainda estão pendentes.

## Preparar o ambiente

Ambiente verificado: Windows 11, Python 3.9.13, Git 2.49.0.windows.1 e Ollama 0.40.5. A referência foi medida em CPU, num Ryzen 5 7535U com 16 GB de RAM.

Na raiz do projeto, usando PowerShell:

```powershell
# Criar apenas se o ambiente ainda não existir.
py -m venv .venv

# Usar o Python do ambiente sem precisar ativá-lo.
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m guara
```

Com o Ollama ativo e `guara1` criado conforme abaixo, o último comando abre a conversa. A interface usa `prompt_toolkit==3.0.52`, instalado pelo comando de dependências acima e compatível com Python 3.9. A integração HTTP continua usando a biblioteca padrão. As mensagens não são salvas pela aplicação.

## Interface de terminal

O comando de uso diário é:

```powershell
guara
```

Ele já foi instalado no usuário deste computador e funciona de qualquer pasta, sem ativar o `.venv`. Feche e abra o terminal após a instalação para carregar o PATH atualizado. `guara --help` mostra a ajuda e `guara --texto` abre o modo simples.

Para instalar ou atualizar o comando em outro ambiente, execute uma vez na raiz do repositório:

```powershell
& ./scripts/instalar_comando.ps1
```

O instalador cria `guara.cmd` em `%LOCALAPPDATA%\Programs\OrbeIA\bin` e acrescenta essa pasta ao PATH do usuário, preservando as entradas existentes. Ele usa o Python do `.venv` e o `scripts/iniciar_guara.py` deste repositório. Se mover a pasta do projeto, execute o instalador novamente. Um comando `guara` preexistente de outra origem é preservado e impede a instalação.

Em um terminal interativo, `.venv/Scripts/python.exe -m guara` abre a tela cheia. O campo de mensagem cresce com novas linhas e quebras automáticas, até oito linhas de texto ou o espaço disponível no terminal, com uma linha de respiro acima e abaixo. O marcador `>` fica alinhado à primeira linha de texto da caixa e também aparece no início das mensagens enviadas pelo usuário. A conversa usa o fundo padrão do terminal; apenas a entrada e as mensagens enviadas pelo usuário recebem o mesmo fundo destacado. Mensagens e respostas aparecem sem rótulos de remetente, na área com rolagem. O rodapé mostra `Guará-1 · Qwen3-1.7B` à esquerda e o estado da interação à direita. Isso identifica o modelo configurado; a troca de modelos pela interface ainda não está implementada.

| Ação | Tecla ou comando |
| --- | --- |
| Enviar mensagem | Enter |
| Inserir nova linha | Shift+Enter (Ctrl+J como alternativa) |
| Editar mensagem | Setas, Home, End, Backspace e Delete |
| Rolar conversa | PgUp / PgDn ou roda do mouse |
| Voltar ao final da conversa | Ctrl+End |
| Mostrar comandos | Digitar `/` no início da entrada |
| Selecionar e completar comando | Setas ↑/↓ e Tab |
| Fechar sugestões | Esc |
| Limpar conversa e fatos da sessão | `/limpar` ou `/conversar` |
| Encerrar | `/sair`, Ctrl+C ou Ctrl+D com entrada vazia |

Durante a espera, aparece `Trabalhando…` com um indicador animado e segundos decorridos acima da entrada, além do estado no rodapé. O indicador desaparece ao concluir ou falhar. É possível editar a próxima mensagem, mas Enter só envia quando o pedido atual terminar. Ctrl+C e `/sair` encerram a interface mesmo durante a espera; a geração no Ollama não é necessariamente cancelada. A resposta aparece completa, sem streaming nesta etapa. A área visual mantém até 40.000 caracteres recentes; isso é separado do contexto curto do modelo. Ao encerrar a tela cheia, o terminal anterior é restaurado.

Para usar o formato simples anterior:

```powershell
.venv/Scripts/python.exe -m guara --texto
```

Entrada ou saída redirecionada usa automaticamente o modo simples. Ambos os modos compartilham o mesmo núcleo de conversa, memória e tratamento de erros. A [validação da CLI](docs/avaliacoes/cli-terminal-20261016.json) contém capturas do renderizador em três tamanhos e uma chamada real ao Ollama; a conferência manual na janela e fonte usadas no computador foi dada como concluída pelo responsável em 17 de outubro de 2026, encerrando a etapa 4 do checklist.

No Windows, o adaptador usa o leitor de eventos nativos para preservar o modificador de Shift+Enter, inclusive quando o console oferece entrada VT. Também reconhece sequências VT que informam o modificador e a sequência ESC + CR enviada pelo atalho Shift+Enter configurado no Windows Terminal. Alt+Enter também insere nova linha se o terminal enviar essa mesma sequência. Se o terminal enviar Shift+Enter como Enter comum, sem essa informação, use Ctrl+J para inserir a nova linha.

No terminal integrado do VS Code, Shift+Enter ainda foi reportado como envio de mensagem; a configuração específica e a validação física permanecem pendentes. Ctrl+J pode ser interceptado pelo editor para ocultar o painel.

O menu mostra `/limpar`, `/conversar`, `/arquivo`, `/permitir`, `/negar` e `/sair`, com descrições, e filtra pelo prefixo digitado (por exemplo, `/li`). Tab preenche a opção selecionada. Enter aceita uma opção selecionada ou completa um prefixo; com o comando completo confirmado, Enter o executa. O nome visual `Guará-1` corresponde à configuração `guara1` usada pela API do Ollama.

Peça `Leia notas.txt e resuma` ou use `/arquivo notas.txt`. `/arquivo` sem argumentos informa a pasta da sessão e os limites. O Python oferece somente `ler_arquivo(caminho)` ao modelo; valida a chamada e devolve o conteúdo real antes da resposta final. Não há escrita, exclusão, listagem de pastas ou execução de código. Sem chamada de leitura, pedidos reconhecidos de arquivo recebem um aviso, sem exibir um resumo inventado.

A pasta permitida é o diretório atual quando `guara` inicia, incluindo suas subpastas. O lançador global preserva esse diretório; a pasta do código do Guará não vira a pasta permitida automaticamente. Caminhos relativos partem da pasta da sessão, que permanece fixa até encerrar o programa. O modelo recebe esse diretório explicitamente em cada interação, inclusive no retorno da ferramenta, com orientação para preservar nomes e caminhos relativos: `leia README.md` deve solicitar `ler_arquivo` com `caminho: "README.md"`, sem inventar outra pasta. `..`, caminhos absolutos e links são resolvidos antes da verificação. Destinos externos mostram o caminho completo e um código: digite `/permitir CODIGO` para uma única leitura desse arquivo ou `/negar CODIGO` para recusar. Outra mensagem ou `/limpar` cancela o pedido. Não há concessão permanente nem autorização fornecida pelo modelo.

A leitura aceita UTF-8 (com ou sem BOM), até **4.096 bytes e 2.400 caracteres**, nos formatos `.txt`, `.md`, `.csv`, `.json`, `.log`, `.py`, `.yaml`, `.yml`, `.toml` e `.ini`. Arquivos maiores são recusados integralmente; caminhos de rede, dispositivos, fluxos alternativos do Windows, dados binários e hard links são recusados. O destino do arquivo aberto é conferido antes de ler os bytes. As permissões do Windows continuam se aplicando. O conteúdo é tratado como dado, com instrução para não seguir comandos embutidos nele.

A primeira mensagem válida, pedidos de autorização, contadores de respostas, recusas, falhas e leituras concluídas ficam em memória, separados do contexto curto. Perguntas reconhecidas como `Qual foi minha primeira mensagem?` e `O que você já fez nessa conversa?` são respondidas pelo Python. `/conversar` e `/limpar` redefinem o histórico, fatos e pedidos pendentes, mantendo a pasta inicial. Não há transcrição completa dos turnos antigos.

O reconhecimento de referências e continuações é conservador e não cobre toda a linguagem natural. A seleção do arquivo e a resposta final dependem do modelo pequeno e podem falhar; a validação do Python controla a execução e o acesso. A prova da etapa 5 não substitui os 20 casos da avaliação do MVP.

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

Recriar `guara1` após editar o arquivo. O modo sem raciocínio explícito foi escolhido após a comparação local e a aprovação do responsável. O Python envia `think: false` explicitamente em cada pedido; ao usar o CLI, passar `--think=false`. A aplicação também envia sua própria mensagem de sistema em cada chamada, reforçando identidade, contratos da leitura e exigência de resultados reais; essas instruções e o `Modelfile` devem permanecer coerentes. O CLI isolado do Ollama não executa as ferramentas do Python.

Limites iniciais: até 1.000 caracteres por entrada, três pares de conversa e 2.400 caracteres no histórico e no pedido enviado, descartando pares antigos completos. A resposta final é limitada a 4.000 caracteres, além de 256 tokens gerados. O contexto do modelo é de 2.048 tokens; os limites de caracteres não são uma contagem exata de tokens, e o Ollama pode truncar entradas que excedam o contexto. Respostas que atingem o limite de geração recebem um aviso.

O timeout de conexão e leitura é de 30 segundos; ele não garante um prazo absoluto para toda a operação nem cancela a geração no servidor. Falhas de conexão, modelo ausente e respostas inválidas exibem orientação e são registradas como falhas da aplicação no histórico curto. Não há repetição automática. Cada interação faz no máximo duas chamadas HTTP: uma para a solicitação e outra para a resposta após uma única leitura. A segunda não oferece ferramentas, e chamadas adicionais são recusadas. Pedidos externos pausam antes da leitura e da segunda chamada, até a autorização. Comandos de controle e respostas locais sobre a sessão não consultam o modelo. No retorno da ferramenta, o pedido atual, a chamada e o resultado substituem os turnos anteriores, limitando o contexto adicional. O modelo fica carregado por até dois minutos de inatividade, conforme `keep_alive`.

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

O script não executa o código produzido pelo modelo. O `checks.json` preserva quatro regressões históricas em PT-BR e define cinco casos de arquivos; os 20 casos completos ainda estão pendentes. A [prova de leitura e autorização](docs/avaliacoes/arquivos-20261017.json) registra três cenários reais com dados sintéticos. Para repeti-la: `.venv/Scripts/python.exe scripts/validar_arquivos.py` (Ollama ativo; saídas em `resultados/`). A [regressão de leitura](docs/avaliacoes/regressao-leitura-20261016.json) registra o diálogo que antes produzia uma citação inventada. A [retomada automática](docs/avaliacoes/retomada-conversa-20261016.json) registra a correção para continuar conversando sem exigir um comando. A [memória da sessão](docs/avaliacoes/memoria-sessao-20261016.json) registra a primeira mensagem correta, as ações efetivamente registradas e o reset. Esses resultados validam os casos registrados, sem demonstrar aderência universal do modelo isolado.

A [comparação com raciocínio ativado](docs/benchmarks/comparacao-think-20261016.md) foi executada com o mesmo limite de 256 tokens. Matemática e código atingiram esse limite durante o raciocínio e não entregaram resposta final. O responsável aprovou manter `think: false`; um orçamento maior e instruções para raciocínio em português ainda precisam de avaliação própria.

## Arquivos

```text
guara/
  __main__.py          # python -m guara
  cli.py               # argumentos e escolha da interface
  core/                # conversa, integração e memória
  terminal/            # tela e teclado
  tools/               # leitura de texto e registro permitido
scripts/               # instalação e validações locais
tests/                 # testes automatizados
docs/                  # plano, checklist e evidências
```

| Caminho | Finalidade |
| --- | --- |
| `AGENTS.md` | Contexto e regras para trabalhar no repositório |
| `Modelfile` | Base e instruções iniciais do Guará 1 |
| `guara/cli.py` e `guara/__main__.py` | Argumentos e entrada do pacote |
| `guara/core/conversation.py` | Conversa pelo terminal e integração com Ollama |
| `guara/terminal/interface.py` | Tela cheia, entrada fixa, área de conversa e rodapé com modelo |
| `guara/terminal/keys.py` | Compatibilidade de Shift+Enter em eventos Windows e sequências VT |
| `guara/core/capabilities.py` | Reconhecimento de referências e continuações para recusar respostas sem leitura |
| `guara/core/session.py` | Primeira mensagem e contadores da sessão, com respostas factuais locais |
| `tests/test_app.py` | Verificações de limites, histórico, comandos e falhas da integração |
| `tests/test_capabilities.py` | Referências reconhecidas e transições do fluxo de arquivos |
| `tests/test_session.py` | Fatos da sessão preservados após descarte do contexto curto |
| `tests/test_terminal_ui.py` | Renderização, teclado, envio, rolagem e saída durante espera |
| `guara/tools/__init__.py` | Contrato e validação da ferramenta ler_arquivo |
| `guara/tools/files.py` | Leitura limitada, verificação de caminhos e permissões por arquivo |
| `scripts/validar_arquivos.py` | Prova real com texto sintético e acesso externo autorizado ou negado |
| `checks.json` | Estrutura dos casos de avaliação |
| `requirements.txt` | Registro das dependências Python |
| `scripts/validar_qwen.py` | Medição local da base |
| `scripts/validar_cli.py` | Capturas do renderizador; `--real` inclui uma chamada ao Ollama |
| `scripts/instalar_comando.ps1` | Instala o comando `guara` no PATH do usuário Windows |
| `scripts/iniciar_guara.py` | Entrada usada pelo comando global, independente da pasta atual |
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
