import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import pytest

from gde_unb import adequa_dataset, avalia_elemento, avalia_familia, avaliar_estrutura, image_to_base64, gerar_relatorio_html


@pytest.fixture
def sample_dataframe():
    # MultiIndex das colunas
    columns = pd.MultiIndex.from_tuples([
        ('Danos', ''),
        ('Pilar P01', 'Fi'), ('Pilar P01', 'Fp'),
        ('Pilar P02', 'Fi'), ('Pilar P02', 'Fp'),
        ('Pilar P03', 'Fi'), ('Pilar P03', 'Fp'),
        ('Pilar P04', 'Fi'), ('Pilar P04', 'Fp'),
    ])

    data = [
        ["Carbonatação",         np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Cobrimento Deficiente", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Contaminação por Cloretos", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Corrosão de armaduras", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Danos por impacto",     np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Desagregação",          np.nan, np.nan, np.nan, np.nan, 1.0,    3.0,    1.0,    3.0],
        ["Deslocamento",          np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Desvio de Geometria",   np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Eflorescência",         np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Falha de Concretagem",  1.0,    3.0,    1.0,    3.0,    np.nan, np.nan, np.nan, np.nan],
        ["Fissuras",              np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Manchas",               np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Recalque",              np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Sinais de Esmagamento", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ["Umidade na base",       np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    ]

    df = pd.DataFrame(data, columns=columns)
    return df


def test_adequa_dataset(sample_dataframe):
    df_ajustado, nome_elementos = adequa_dataset(sample_dataframe.copy())

    assert isinstance(df_ajustado, pd.DataFrame)
    assert isinstance(nome_elementos, list)
    assert set(nome_elementos) == {'Pilar P01', 'Pilar P02', 'Pilar P03', 'Pilar P04'}
    assert 'Fi - Pilar P01' in df_ajustado.columns
    assert 'Fp - Pilar P04' in df_ajustado.columns
    assert 'Danos' in df_ajustado.columns


def test_avalia_elemento(sample_dataframe):
    df_ajustado, _ = adequa_dataset(sample_dataframe.copy())
    resultados = avalia_elemento(df_ajustado)

    elementos_esperados = {'Pilar P01', 'Pilar P02', 'Pilar P03', 'Pilar P04'}
    assert set(resultados.keys()) == elementos_esperados

    for nome_elemento, valores in resultados.items():
        assert isinstance(valores, dict)
        assert round(valores['sum_d'], 2) == 2.4, f"{nome_elemento}: sum_d incorreto"
        assert round(valores['d_max'], 2) == 2.4, f"{nome_elemento}: d_max incorreto"
        assert round(valores['g_de'], 2) == 2.4, f"{nome_elemento}: g_de incorreto"

    for nome_elemento in resultados:
        sum_d = resultados[nome_elemento]['sum_d']
        d_max = resultados[nome_elemento]['d_max']
        assert sum_d == d_max, f"{nome_elemento} deveria conter apenas um dano válido"


def test_avalia_familia(sample_dataframe):
    df_ajustado, _ = adequa_dataset(sample_dataframe.copy())
    resultado = avalia_familia(df_ajustado, nome_arquivo='estrutura_teste', f_r=5.0)

    assert isinstance(resultado, dict)
    familia_result = resultado['estrutura_teste']

    assert 'gde_max' in familia_result
    assert 'g_df' in familia_result
    assert 'f_r' in familia_result
    assert 'f_r × g_df' in familia_result
    assert 'resultados_elemento' in familia_result

    assert familia_result['gde_max'] == pytest.approx(2.4, abs=0.01), "gde_max incorreto"
    assert familia_result['g_df'] == pytest.approx(3.2, abs=0.05), "g_df incorreto"
    assert familia_result['f_r'] == 5.0, "f_r incorreto"
    assert familia_result['f_r × g_df'] == pytest.approx(15.9, abs=0.1), "f_r × g_df incorreto"

    for nome_elemento, valores in familia_result["resultados_elemento"].items():
        assert valores['g_de'] == pytest.approx(2.4, abs=0.01), f"{nome_elemento}: g_de incorreto"


def test_avaliar_estrutura():
    resultados_familias = {
        'estrutura_teste': {
            'g_df': 3.2,
            'f_r': 5.0
        }
    }

    g_d, nivel, recomendacao = avaliar_estrutura(resultados_familias)

    assert isinstance(g_d, float)
    assert g_d == pytest.approx(3.2, abs=0.01)
    assert nivel == "Baixo"
    assert "manutenção preventiva" in recomendacao.lower()


def test_image_to_base64_with_bytes():
    jpeg_header = b'\xff\xd8\xff\xe0'  # mock de imagem JPEG
    encoded = image_to_base64(jpeg_header)
    assert isinstance(encoded, str)
    assert len(encoded) > 0


def test_gerar_relatorio_html():
    resultados_familias = {
        "Pilares": {
            "f_r": 1.0,
            "g_df": 10.0,
            "f_r × g_df": 10.0,
            "resultados_elemento": {
                "P01": {"sum_d": 5.0, "d_max": 3.0, "g_de": 4.0},
                "P02": {"sum_d": 6.0, "d_max": 2.0, "g_de": 6.0}
            }
        }
    }

    tabelas_originais = {
        "Pilares": pd.DataFrame({"Coluna A": [1, 2], "Coluna B": [3, 4]})
    }

    imagens_por_familia = {
        "Pilares": [("img1.jpg", image_to_base64(b'\xff\xd8\xff\xe0'))]
    }

    nomes_arquivos = ["planilha_pilares.xlsx"]
    fr_lista = [1]
    fr_descricao = {1: "Principal"}
    elementos_por_familia = {"Pilares": ["P01", "P02"]}

    html, df_familia, df_estrutura = gerar_relatorio_html(
        resultados_familias=resultados_familias,
        g_d=10.0,
        nivel="Baixo",
        recomendacao="Manutenção preventiva",
        tabelas_originais=tabelas_originais,
        imagens_por_familia=imagens_por_familia,
        nomes_arquivos=nomes_arquivos,
        fr_lista=fr_lista,
        fr_descricao=fr_descricao,
        elementos_por_familia=elementos_por_familia
    )

    assert isinstance(html, str)
    assert "<html>" in html
    assert "Pilares" in html
    assert isinstance(df_familia, pd.DataFrame)
    assert isinstance(df_estrutura, pd.DataFrame)