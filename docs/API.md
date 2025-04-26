# Documentação da API

## `APIClient`

### Métodos

#### `obter_resultados() -> List[str]`
Obtém os últimos resultados do Bac Bo da API

**Retorno:**
- Lista de strings com os resultados ('A', 'V' ou 'E')

**Exemplo:**
```python
client = APIClient("http://api.example.com")
resultados = client.obter_resultados()
# ['A', 'V', 'E', 'A']
```

## `EstrategiaManager`

### Métodos

#### `encontrar_estrategia(resultados: List[str]) -> Optional[Dict]`
Encontra estratégia correspondente aos resultados

**Parâmetros:**
- `resultados`: Lista de resultados para análise

**Retorno:**
- Dicionário com estratégia ou None se não encontrado

**Exemplo:**
```python
manager = EstrategiaManager()
estrategia = manager.encontrar_estrategia(['A', 'A', 'V'])
# {'padrao': ['A', 'A', 'V'], 'entrada': 'V', 'nome': 'Padrão 1'}