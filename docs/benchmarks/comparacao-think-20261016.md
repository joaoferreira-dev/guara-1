# Comparação de Qwen3-1.7B com e sem raciocínio

Rodada com raciocínio executada em 16 de outubro de 2026, entre 19:07 e 19:09 (America/Sao_Paulo). Referências revisadas: [sem raciocínio](validacao-qwen-secao-2.json) e [com raciocínio](validacao-qwen-think-20261016.json).

## Condições

Os quatro pedidos e o script de medição foram mantidos. A única alteração na configuração enviada à API foi `think: true`: contexto de 2.048 tokens, `num_predict: 256`, temperatura 0 e seed 42. Mesmo Python 3.9.13, Ollama 0.40.5 e digest `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`. Nas duas rodadas, nenhum modelo estava carregado no início; as chamadas seguintes reutilizaram o modelo. A API informou `size_vram: 0` em todas as chamadas da nova rodada, compatível com CPU.

A continuidade usa o pedido e a resposta de conversa da própria rodada, conforme o procedimento original. Portanto, seu histórico não é textualmente idêntico entre os modos. Nenhuma instrução adicional foi incluída para pedir raciocínio em português. Os tempos são até a resposta HTTP completa, incluindo raciocínio, sem streaming.

## Resultados

| Tarefa | Sem raciocínio | Com raciocínio | Resultado com raciocínio |
| --- | ---: | ---: | --- |
| Conversa em PT-BR | 7,76 s | 14,26 s | Resposta em português; três frases, excedendo as duas pedidas; erro de grafia em “projets” |
| Continuidade | 2,77 s | 13,51 s | Resposta correta: Python |
| Desconto e frete | 11,76 s | 17,26 s | Sem resposta final; limite de 256 tokens atingido |
| Função `soma_pares` | 4,31 s | 17,55 s | Sem resposta final ou código; limite de 256 tokens atingido |
| Total das quatro chamadas | 26,60 s | 62,58 s | Aproximadamente 2,35 vezes o tempo da referência |

O texto de raciocínio foi predominantemente em inglês nas quatro chamadas, com citações do pedido em português. As respostas finais presentes estavam em português ou consistiam no nome Python. Esta rodada não testa se uma instrução específica consegue mudar o idioma do raciocínio.

O limite de geração inclui os tokens de raciocínio: matemática e código geraram 256 tokens cada, com `done_reason: length` e `message.content` vazio. Conversa e continuidade geraram 162 e 183 tokens, respectivamente, e terminaram com `stop`. No total foram 857 tokens gerados com raciocínio, contra 248 sem raciocínio. Nenhum código foi executado nesta rodada, pois o modelo não entregou código final. As recomendações externas da conversa não foram verificadas.

## Memória e limites da comparação

| Medida do sistema | Sem raciocínio | Com raciocínio |
| --- | ---: | ---: |
| RAM total em uso antes da primeira chamada | 12,40 GiB | 11,82 GiB |
| Pico amostrado de RAM total em uso | 14,04 GiB | 13,34 GiB |
| RAM disponível no pico amostrado | 0,74 GiB | 1,44 GiB |

As medições incluem outros processos do Windows e não isolam o consumo do Ollama. A carga inicial foi diferente; o pico menor da nova rodada não demonstra que raciocínio economize memória. A amostragem a cada aproximadamente 250 ms pode perder picos curtos. O modelo foi descarregado após a coleta.

Houve uma rodada por modo, em horários diferentes, sem controle dos demais aplicativos. Todas as chamadas com raciocínio terminaram em menos de 30 segundos, mas duas não entregaram resposta final; isso impede tratá-las como sucesso no critério de resposta curta completa. As quatro tarefas não substituem os 20 casos do MVP.

## Decisão sugerida

Manter `think: false` como configuração inicial do MVP com orçamento de 256 tokens. Nesta amostra, ativar raciocínio aumentou a espera, descumpriu o formato da conversa e impediu a entrega de matemática e código. Isso não determina a qualidade do modo com um orçamento maior.

Se houver interesse em um modo opcional de raciocínio, medir separadamente um orçamento de geração maior e incluir uma instrução específica de idioma. Essa seria outra configuração, com nova avaliação de qualidade, tempo e memória; ainda não foi testada. Após avaliar estes resultados, o responsável aprovou manter `think: false` como configuração do MVP.

## Reprodução

```powershell
# Sem raciocínio (padrão anterior preservado).
.venv/Scripts/python.exe scripts/validar_qwen.py

# Com raciocínio; demais parâmetros iguais aos da referência.
.venv/Scripts/python.exe scripts/validar_qwen.py --think
```

Cada execução salva um JSON novo em `resultados/benchmarks/`. Conferir os modelos carregados antes de interpretar a primeira chamada como partida a frio. As referências revisadas em `docs/benchmarks/` não são sobrescritas pelo script.
