# 🔍 Log Searcher

Ferramenta com interface gráfica para buscar palavras ou números em arquivos `.log` e `.txt`.

## Requisitos

- Python 3.8+
- Tkinter (incluso na maioria das instalações do Python)

## Como usar

```bash
python log_searcher.py
```

## Gerar o executável
```
python -m PyInstaller --onefile --windowed --icon=log_searcher.ico --add-data "log_searcher.ico;." log_searcher.py
```

## Funcionalidades

| Recurso | Descrição |
|---|---|
| Busca por texto/número | Encontra qualquer palavra, número ou trecho |
| Maiúsc./minúsc. | Opção de busca case-sensitive |
| Palavra inteira | Encontra só a palavra exata (não substrings) |
| Regex | Suporte a expressões regulares completas |
| Subpastas | Busca recursiva em subdiretórios |
| Extensões configuráveis | Padrão `.log,.txt` — personalizável |
| Exportar .txt | Salva os resultados formatados |
| Exportar .csv | Salva os resultados em planilha |
| Abrir arquivo | Duplo clique abre o arquivo no editor padrão |

## Exemplos de uso

### Busca simples
Digite `ERROR` no campo de busca para encontrar todas as linhas com a palavra "error" (sem distinção de maiúsculas).

### Busca por número
Digite `404` para encontrar todos os logs com esse código HTTP.

### Regex — múltiplos termos
Ative "Expressão regular" e digite:
```
ERROR|WARN|CRITICAL
```

### Regex — código HTTP 5xx
```
HTTP/\d+\.\d+ 5\d{2}
```

### Regex — IP address
```
\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b
```

### Regex — data e hora
```
\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}
```

## Extensões aceitas

No campo **Extensões**, você pode adicionar qualquer extensão separada por vírgula:
```
.log,.txt,.out,.err,.trace
```
