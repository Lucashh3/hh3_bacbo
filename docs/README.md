# Documentação do BacBo Bot

## Visão Geral
Sistema de automação para apostas no jogo Bac Bo em cassinos online, utilizando pyautogui para interação com a interface.

## Módulos Principais

### `src/core/`
- `bot_core.py`: Lógica principal do bot
- `api_client.py`: Comunicação com API de resultados
- `estrategias.py`: Gerenciamento de estratégias

### `src/config/`
- `config_manager.py`: Carrega configurações do JSON
- `coordenadas.py`: Gerencia posições dos elementos na tela

## Configuração

1. Edite `src/config/config_apostas.json`:
```json
{
  "aposta_base": 20,
  "aposta_empate": 5,
  "gale_multiplicadores": [2.0, 3.5],
  "max_gales": 2
}
```

2. Configure as coordenadas em `src/config/coordenadas_bacbo.json`

## Execução
```bash
python src/main.py
```

## Testes
```bash
python -m unittest discover tests/