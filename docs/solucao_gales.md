# Solução para Implementação de Gales

## Problema Identificado
A sequência de gales atual está configurada com multiplicadores [2.0, 3.5] quando deveria ser [2.0, 4.0] conforme requisito.

## Análise
1. A lógica de gales está corretamente implementada em `bot_core.py`
2. O cálculo dos valores está sendo feito no método `_calcular_valor_gale()`
3. Os multiplicadores são obtidos do arquivo `config_apostas.json`

## Solução Proposta
1. Modificar o arquivo `src/config/config_apostas.json` para:
```json
{
    "aposta_base": 10,
    "aposta_empate": 5,
    "gale_multiplicadores": [2.0, 4.0],
    "max_gales": 2,
    "stop_loss": 3,
    "saldo_inicial": 1000
}
```

2. Não são necessárias alterações no código, apenas na configuração

## Próximos Passos
1. Mudar para o modo Code para implementar a alteração
2. Testar a nova configuração