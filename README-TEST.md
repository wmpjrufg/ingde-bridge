# ✅ Execução de Testes Unitários – `gde_test.py`

Este repositório contém testes automatizados para validar o correto funcionamento das funções responsáveis por avaliar a gravidade de danos estruturais em elementos (como pilares).

## Arquivo de Teste

O teste principal está localizado em:

```

.\test\gde\_test.py

````

Este arquivo utiliza o framework de testes do Python (`unittest`) para verificar se os cálculos realizados pela função `avalia_familia` estão corretos.

---

## Como Executar os Testes

Para rodar o teste unitário, abra o terminal na raiz do projeto e execute:

```bash
python .\test\gde_test.py
````

Esse comando irá:

* Carregar o arquivo de teste `gde_test.py`;
* Executar todos os métodos que começam com `test_`;
* Exibir os resultados dos testes no terminal (✓ para testes que passaram, F ou E para falhas ou erros).

---

## Pré-requisitos

* Python 3.7 ou superior instalado.
* Bibliotecas necessárias instaladas:

  * `pandas`
  * `numpy`

Você pode instalar os pacotes com:

```bash
pip install pandas numpy
```
