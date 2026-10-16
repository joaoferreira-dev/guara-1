# OrbeIA — Guará 1

Guará 1 é um assistente pessoal do projeto OrbeIA, baseado no Qwen3 e configurado para conversar em português brasileiro e utilizar ferramentas locais.

O MVP será executado no Windows pelo terminal, com Ollama e um programa Python. As ferramentas previstas são uma calculadora e a leitura de texto em uma pasta permitida. A configuração do assistente não altera os pesos do modelo.

## Estado atual

O ambiente local e a execução de Qwen3-1.7B foram validados. Este repositório contém a estrutura inicial do programa, um `Modelfile` inicial e as medições de referência. A conversa Python, o histórico e as ferramentas ainda não estão implementados. A criação e o teste do nome `guara1` no Ollama serão validados na etapa 4 do checklist.

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

Atualmente não há dependências Python externas. O último comando informa o estado da estrutura inicial; ele ainda não abre uma conversa.

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

Não é necessário instalar o pacote Python `ollama`: a integração inicial está planejada pela API HTTP local, usando a biblioteca padrão.

## Configuração inicial do assistente

O `Modelfile` parte de `qwen3:1.7b`, limita o contexto a 2.048 tokens e a geração a 256 tokens. As instruções iniciais definem identidade, português brasileiro e transparência sobre a execução de ferramentas.

Na etapa de validação dessa configuração, executar:

```powershell
ollama create guara1 -f Modelfile
ollama run guara1
```

Recriar `guara1` após editar o arquivo. A escolha do modo de raciocínio será tratada na integração; a medição inicial chamou a API com `think: false` explicitamente.

## Medições e avaliação

Para repetir as medições da base no Windows, com o Ollama ativo:

```powershell
.venv/Scripts/python.exe scripts/validar_qwen.py
```

Cada execução salva um JSON novo em `resultados/benchmarks/`, ignorado pelo Git. A referência inicial permanece em [docs/benchmarks](docs/benchmarks/README.md). Os tempos medidos são de respostas completas; a primeira chamada inclui carregamento quando não houver modelo em memória.

O script não executa o código produzido pelo modelo. O `checks.json` reserva a organização dos 20 casos de avaliação previstos, ainda sem casos escritos. Falhas de instrução, desempenho e integração devem ser documentadas.

## Arquivos

| Caminho | Finalidade |
| --- | --- |
| `AGENTS.md` | Contexto e regras para trabalhar no repositório |
| `Modelfile` | Base e instruções iniciais do Guará 1 |
| `app.py` | Ponto de entrada inicial, ainda sem conversa |
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

O Git local foi inicializado em `main`. O remoto `origin` está configurado como `https://github.com/joaoferreira-dev/guara-1.git`. A conexão e o envio ainda precisam ser validados com uma credencial válida. Não há CI/CD neste MVP.

## Documentação

- [Plano do MVP](docs/OrbeIA-Guara-1-plano-MVP.md).
- [Checklist de preparação e progresso](docs/OrbeIA-Guara-1-checklist-preparacao.md).
- [Origem e licença da base](docs/modelo-base.md).

O modelo Qwen3-1.7B usa Apache-2.0. A licença do código deste projeto ainda não foi definida; ela é uma decisão separada da licença do modelo.
