# Contexto do repositório

OrbeIA é o projeto; Guará 1 é seu assistente pessoal local. A descrição correta é: “Guará 1 é um assistente pessoal do projeto OrbeIA, baseado no Qwen3 e configurado para conversar em português brasileiro e utilizar ferramentas locais.” Não afirmar que o projeto treinou uma LLM própria: nesta fase, nome, instruções e ferramentas não alteram os pesos da base.

## Escopo e estado atual

- Fonte do escopo: `docs/OrbeIA-Guara-1-plano-MVP.md`.
- Progresso e evidências: `docs/OrbeIA-Guara-1-checklist-preparacao.md`.
- Windows 11, Python 3.9.13, AMD Ryzen 5 7535U, 16 GB de RAM e vídeo integrado. Planejar execução pela CPU e acompanhar a memória disponível.
- Executor: Ollama local em `http://localhost:11434`; base inicial `qwen3:1.7b`, Q4_K_M. Manter a origem e a identificação em `docs/modelo-base.md`.
- Ambiente `.venv`, validação inicial da base e configuração `guara1` no Ollama já existem. A conversa Python e o histórico curto em memória estão implementados; as duas ferramentas ainda estão pendentes. O responsável aprovou `think: false` após comparação local.
- O MVP terá terminal, conversa em PT-BR, histórico curto, calculadora e leitura de texto em uma pasta permitida. Não exige interface gráfica, servidor público, banco dedicado, contas, nuvem, CI/CD ou treinamento.
- A referência inicial usou `think: false`, contexto de 2.048 tokens e máximo de 256 tokens gerados. Espera de até 30 segundos é um critério provisório de avaliação, não um timeout de rede já implementado.

## Organização

- `README.md`: preparação, comandos e estado real do programa.
- `Modelfile`: base e instruções iniciais do assistente; após mudanças, recriar com `ollama create guara1 -f Modelfile`.
- `app.py`: conversa no terminal via API local, histórico apenas na sessão, comandos `/limpar`, `/conversar`, `/arquivo` e `/sair` e tratamento de erros. Envia mensagem de sistema explícita, que deve permanecer coerente com o `Modelfile`.
- `capabilities.py`: fluxo explícito de arquivos indisponíveis. Bloqueia continuações reconhecidas e retoma automaticamente ao mudar de assunto, sem apagar o histórico anterior; o reconhecimento por referências comuns é conservador e não oferece cobertura universal de linguagem natural.
- `session.py`: primeira mensagem e contadores da sessão, independentes do contexto curto. Consultas reconhecidas sobre o início e ações da sessão usam registros do Python; `/limpar` e `/conversar` redefinem esses fatos. Recusas e falhas entram no histórico com origem identificada; não excluir pares apenas por mencionar arquivos.
- `tests/test_app.py`: testes da integração com respostas simuladas, sem executar o modelo.
- `tools.py`: futuro registro de ferramentas permitidas; começa vazio.
- `checks.json`: estrutura dos 20 casos previstos, com quatro regressões em PT-BR; não representa avaliação completa.
- `requirements.txt`: dependências Python; atualmente apenas biblioteca padrão.
- `scripts/validar_qwen.py`: medição local no Windows; faz chamadas reais ao Ollama e não executa o código gerado.
- `docs/benchmarks/`: referências selecionadas, revisadas e versionadas.
- `docs/avaliacoes/`: evidências revisadas dos casos de comportamento, com pedidos sintéticos.
- `resultados/benchmarks/`: saídas locais com data e hora, ignoradas pelo Git.

## Desenvolvimento e verificação

- Escrever documentação, mensagens ao usuário e instruções do assistente em português brasileiro.
- Preservar compatibilidade com Python 3.9 enquanto essa for a versão do ambiente; não usar sintaxe ou APIs de versões posteriores sem atualizar explicitamente a configuração e a documentação.
- Preferir arquivos pequenos e biblioteca padrão. Adicionar dependências somente quando houver necessidade concreta e registrá-las em `requirements.txt`.
- Usar `.venv/Scripts/python.exe` diretamente; não é necessário ativar o ambiente nem mudar a política de execução do PowerShell.
- Comando atual: `.venv/Scripts/python.exe app.py`, com Ollama ativo e `guara1` criado. Envia `think: false`, contexto de 2.048 tokens e geração de até 256 tokens. O histórico guarda até três pares e 2.400 caracteres; a entrada aceita até 1.000 caracteres. O timeout de conexão/leitura é de 30 segundos, sem prazo absoluto para a operação inteira.
- Testes da integração: `.venv/Scripts/python.exe -m unittest discover -s tests -v`.
- Para medir a base: `.venv/Scripts/python.exe scripts/validar_qwen.py`, com Ollama ativo. Não repetir medições demoradas para alterações apenas documentais.
- Ao implementar comportamento, verificar casos relevantes e registrar falhas reais. Não marcar etapas como concluídas sem execução ou evidência correspondente.
- Os 20 casos previstos são cinco de PT-BR, cinco problemas, cinco de código e cinco com ferramentas. A medição inicial de quatro chamadas não os substitui.
- Atualizar README e checklist quando o comportamento ou o estado do projeto mudar. Preservar alterações feitas pelo responsável pelo projeto.

## Ferramentas e dados locais

- O Python executa as ferramentas; o modelo apenas solicita chamadas. Validar nome, argumentos e limites antes de executar.
- Executar somente funções cadastradas. Não usar `eval`, `exec` ou comandos de shell para interpretar entradas do modelo ou do usuário na aplicação.
- A calculadora terá operações definidas e tratamento de entradas inválidas e divisão por zero.
- Na leitura de texto, resolver o caminho e verificar que ele permanece dentro da pasta permitida, inclusive diante de `..`, caminhos absolutos e links. Definir codificação, formatos e limite de tamanho.
- Limitar contexto, histórico, tamanho de resposta e quantidade de chamadas por interação.
- Não versionar `.venv`, pesos, credenciais, `.env`, resultados temporários ou conversas pessoais. Usar exemplos sintéticos nos testes públicos.
- Preservar a referência inicial de benchmark. Novas execuções vão para `resultados/`; copiar para `docs/benchmarks/` somente medições escolhidas e revisadas.

## Git e GitHub

- Fluxo: editar, verificar localmente, revisar os arquivos, fazer commit e enviar ao GitHub. GitHub guarda o projeto; não executa a LLM.
- Não presumir URL, visibilidade ou publicação do repositório remoto. Consultar a configuração existente e o contexto da solicitação.
- A licença Apache-2.0 registrada é a do modelo Qwen3-1.7B; não atribuir automaticamente essa licença ao código do projeto.
- Para todo commit, incluir este trailer exato em sua própria linha final:

```text
Co-authored-by: codex <codex@openai.com>
```

O arquivo `.gitmessage` fornece um modelo de mensagem. Configuração local recomendada: `git config --local commit.template .gitmessage`. Mesmo com o template, verificar o trailer em commits feitos com `git commit -m` ou outras ferramentas.
