# Medições de referência do Guará 1

Esta pasta guarda medições selecionadas e revisadas para comparação ao longo do projeto. Os arquivos daqui devem ser versionados.

- [Validação inicial de Qwen3-1.7B, em 16/10/2026](validacao-qwen-secao-2.json): pedidos sintéticos, respostas, configuração, tempos, memória e revisão dos resultados.
- [Resumo e limitações da medição](../OrbeIA-Guara-1-checklist-preparacao.md): seção 2 do checklist.

Para gerar uma nova medição no Windows, com o Ollama ativo, executar na raiz do projeto:

```powershell
py scripts/validar_qwen.py
```

O script usa apenas a biblioteca padrão do Python e salva um JSON com data e hora em `resultados/benchmarks/`. Essa pasta é ignorada pelo Git. Cada execução cria um arquivo novo e preserva as referências desta pasta.

Antes de versionar uma nova referência, revisar pedidos, respostas e metadados para remover informações pessoais ou credenciais. Conferir os resultados e copiar somente o JSON escolhido para esta pasta, com um nome que identifique a medição. Registrar a configuração e as condições de execução, inclusive se o modelo já estava carregado.

O script coleta as respostas e medições; não aprova automaticamente sua qualidade nem executa o código gerado. A revisão e os seis casos de código presentes na referência inicial foram realizados separadamente.

Esses registros são uma validação inicial local, com quatro chamadas. Não substituem os 20 casos de avaliação previstos para o MVP.
