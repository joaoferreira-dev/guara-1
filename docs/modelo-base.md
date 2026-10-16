# Origem e identificação da base

Guará 1 usa uma base pronta da família Qwen3. A etapa atual configura instruções, nome e integração local, sem treinamento ou modificação de pesos pelo projeto OrbeIA.

## Referência instalada

Dados verificados localmente em 16 de outubro de 2026:

| Campo | Valor |
| --- | --- |
| Modelo de origem | Qwen/Qwen3-1.7B |
| Distribuição utilizada | Catálogo do Ollama, tag `qwen3:1.7b` |
| Executor verificado | Ollama 0.40.5 |
| Quantização | Q4_K_M |
| Formato | GGUF |
| Identificador curto | `8f68893c685c` |
| Digest completo | `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7` |
| Tamanho do arquivo local | 1.359.293.444 bytes |
| Parâmetros nos metadados do executor | `2.0B`; a tag oficial permanece `1.7b` |

O `Modelfile` usa a tag `qwen3:1.7b`. Tags podem mudar; para comparar resultados, conferir o digest instalado e registrar alterações. As métricas da referência inicial se aplicam ao digest acima e à configuração registrada no [checklist](OrbeIA-Guara-1-checklist-preparacao.md).

## Licença e atribuição

O modelo de origem Qwen3-1.7B é disponibilizado sob **Apache License 2.0**, conforme o [arquivo LICENSE publicado pelo Qwen](https://huggingface.co/Qwen/Qwen3-1.7B/blob/main/LICENSE). A distribuição consultada no [catálogo do Ollama](https://ollama.com/library/qwen3:1.7b) também identifica essa licença. Referências verificadas em 16 de outubro de 2026.

Os pesos não são incluídos neste repositório. A atribuição da base deve permanecer na documentação e na descrição do assistente. Se futuramente houver redistribuição de pesos ou adaptadores, revisar os termos e avisos correspondentes à distribuição escolhida.

A licença do código próprio do projeto ainda não foi definida. Não confundir a licença da base com uma licença atribuída automaticamente ao programa.

## Limites desta etapa

Não houve fine-tuning, LoRA, QLoRA ou treinamento do zero. A variante 4B só será considerada após medir qualidade, velocidade e memória. A configuração chamada `guara1` é derivada do `Modelfile`; sua criação e teste com `--think=false` foram validados em 16 de outubro de 2026. O Python envia `think: false` explicitamente, conforme decisão do responsável após a comparação local.
