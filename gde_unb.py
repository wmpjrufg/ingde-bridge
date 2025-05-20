import pandas as pd
import numpy as np
import os
import base64
from pathlib import Path
from typing import Dict, List, Tuple

def image_to_base64(image_input):
    """
    Converte uma imagem para base64, seja a partir de bytes ou de um caminho para arquivo.
    - Se receber `bytes`, codifica diretamente.
    - Se receber `str` ou `Path`, abre o arquivo e codifica.
    """
    if isinstance(image_input, (str, Path)):
        with open(image_input, "rb") as img_file:
            img_bytes = img_file.read()
    elif isinstance(image_input, bytes):
        img_bytes = image_input
    else:
        raise ValueError("Entrada inválida para image_to_base64: deve ser bytes ou caminho de arquivo (str ou Path).")
    
    return base64.b64encode(img_bytes).decode("utf-8")


def gerar_relatorio_html(resultados_familias: Dict[str, Dict[str, float]], g_d: float, nivel: str, recomendacao: str, tabelas_originais: Dict[str, pd.DataFrame], imagens_por_familia: Dict[str, list], nomes_arquivos: List[str], fr_lista: List[int], fr_descricao: Dict[int, str], elementos_por_familia: Dict[str, List[str]]) -> Tuple[str, pd.DataFrame, pd.DataFrame]:
    """
    Gera o relatório consolidado em formato HTML e dois DataFrames com os resultados da inspeção.

    Esta função monta um relatório em HTML com as tabelas originais, imagens, cálculos dos índices G_de e G_df, além de um resumo consolidado por família e pela estrutura como um todo. Também retorna dois DataFrames auxiliares para exibição no Streamlit.

    :param resultados_familias: Dicionário com os resultados numéricos de cada família (valores de F_r, G_df, F_r × G_df e resultados por elemento).
    :param g_d: Grau de Deterioração da Estrutura calculado.
    :param nivel: Nível qualitativo de deterioração da estrutura (ex: "Baixo", "Alto", etc.).
    :param recomendacao: Texto com a recomendação de ação baseada no nível de deterioração.
    :param tabelas_originais: Dicionário com os DataFrames originais das planilhas de inspeção por família.
    :param imagens_por_familia: Dicionário com listas de tuplas (nome_da_imagem, imagem_em_base64) por família.
    :param nomes_arquivos: Lista com os nomes dos arquivos submetidos por família.
    :param fr_lista: Lista dos fatores de importância F_r utilizados por família.
    :param fr_descricao: Dicionário com a descrição textual de cada fator F_r.
    :param elementos_por_familia: Dicionário com os nomes dos elementos estruturais presentes em cada família.

    :return: 
    
        - html (str): Relatório completo gerado em formato HTML.
        - df_resumo_familias_streamlit (pd.DataFrame): DataFrame com o resumo das famílias formatado para Streamlit (usando $...$ para LaTeX).
        - df_estrutura_streamlit (pd.DataFrame): DataFrame com os dados gerais da estrutura, também formatado para exibição no Streamlit.
    """

    html = """<html><head><meta charset='utf-8'><title>Relatório GDE</title>
    <style>
    body { font-family: Arial; margin: 30px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
    th { background-color: #f2f2f2; }
    .image-gallery { display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; margin-top: 20px; }
    .image-box { width: 300px; text-align: center; }
    .image-box img { width: 100%; border: 1px solid #ccc; border-radius: 5px; }
    </style>
    <script src='https://polyfill.io/v3/polyfill.min.js?features=es6'></script>
    <script id='MathJax-script' async src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script>
    </head><body>
    <h1>Relatório Consolidado GDE</h1>
    """

    resumo_familias_html = []
    resumo_familias_streamlit = []
    soma_fr = 0
    soma_fr_gdf = 0

    for i, (nome, dados) in enumerate(resultados_familias.items()):
        fr = dados["f_r"]
        fr_gdf = dados["f_r × g_df"]
        descricao = fr_descricao.get(fr, "")
        soma_fr += fr
        soma_fr_gdf += fr_gdf

        html += f"<hr><h2>Família {i+1} - {nome}</h2>"

        if nome in tabelas_originais:
            df_html = tabelas_originais[nome].fillna(0)
            html += "<h3>Tabela original da inspeção</h3>"
            html += df_html.to_html(index=False, border=1)

        imagens = imagens_por_familia.get(nome, [])
        if imagens:
            html += "<h3>Imagens da inspeção</h3><div class='image-gallery'>"
            for nome_img, base64_img in imagens:
                html += f"""
                <div class='image-box'>
                    <img src='data:image/jpeg;base64,{base64_img}' alt='{nome_img}' />
                    <div><small>{nome_img}</small></div>
                </div>
                """
            html += "</div>"

        resultados_elemento = dados.get("resultados_elemento", {})
        html += f"<h3>Resultados por peça \\(G_{{de}}\\)</h3>"
        html += """
        <table>
            <tr>
                <th>Elemento</th>
                <th>\(\sum D\)</th>
                <th>\(D_{max}\)</th>
                <th>\(G_{de}\)</th>
                <th>\(F_r \times G_{df}\)</th>
            </tr>
        """
        for el, resultado in resultados_elemento.items():
            html += f"""
            <tr>
                <td>{el}</td>
                <td>{resultado['sum_d']:.2f}</td>
                <td>{resultado['d_max']:.2f}</td>
                <td>{resultado['g_de']:.2f}</td>
                <td>{fr_gdf:.2f}</td>
            </tr>
            """
        html += "</table>"

        html += f"<p><strong>Fator de Importância:</strong> \\(F_r = {fr}\\) – {descricao}</p>"

        gde_sum = sum([v['g_de'] for v in resultados_elemento.values()])
        gde_max = max([v['g_de'] for v in resultados_elemento.values()], default=0)

        html += f"""
        <h3>Cálculo do \\(G_{{df}}\\) (Grau de Deficiência Familiar)</h3>
        \\[
        G_{{df}} = {gde_max:.4f} \\cdot \\sqrt{{1 + \\frac{{({gde_sum:.4f} - {gde_max:.4f})}}{{{gde_sum:.4f}}}}} = {dados['g_df']:.4f}
        \\]
        \\[
        F_r \\cdot G_{{df}} = {fr:.4f} \\cdot {dados['g_df']:.4f} = \\textbf{{{fr_gdf:.4f}}}
        \\]
        """

        resumo_familias_html.append({
            "Família / Arquivo": f"Família {i+1} – {nomes_arquivos[i]}",
            "Fator de Importância (\\(F_r\\))": fr,
            "\\(F_r \\times G_{df}\\)": fr_gdf
        })
        resumo_familias_streamlit.append({
            "Família / Arquivo": f"Família {i+1} – {nomes_arquivos[i]}",
            "Fator de Importância ($F_r$)": fr,
            "$F_r × G_df$": fr_gdf
        })

    df_resumo_familias_streamlit = pd.DataFrame(resumo_familias_streamlit)
    df_resumo_familias_html = pd.DataFrame(resumo_familias_html)

    html += "<hr><h2>Resumo dos Resultados por Família</h2>"
    html += df_resumo_familias_html.to_html(index=False, border=1)

    dados_estrutura_html = {
        "Descrição": [
            "\\(\\sum (F_r \\times G_{df})\\)",
            "\\(\\sum F_r\\)",
            "Grau de Deterioração da Estrutura (\\(G_d\\))",
            "Nível de Deterioração",
            "Ação Recomendada"
        ],
        "Valor": [
            f"{soma_fr_gdf:.10f}",
            f"{soma_fr}",
            f"{g_d:.10f}",
            nivel.strip(),
            recomendacao.strip()
        ]
    }
    dados_estrutura_streamlit = {
        "Descrição": [
            "$\\sum (F_r \\times G_{df})$",
            "$\\sum F_r$",
            "Grau de Deterioração da Estrutura ($G_d$)",
            "Nível de Deterioração",
            "Ação Recomendada"
        ],
        "Valor": [
            f"{soma_fr_gdf:.10f}",
            f"{soma_fr}",
            f"{g_d:.10f}",
            nivel.strip(),
            recomendacao.strip()
        ]
    }

    df_estrutura_html = pd.DataFrame(dados_estrutura_html)
    df_estrutura_streamlit = pd.DataFrame(dados_estrutura_streamlit)

    html += "<hr><h2>Grau de Deterioração da Estrutura</h2>"
    html += df_estrutura_html.to_html(index=False, border=1)
    html += "</body></html>"

    return html, df_resumo_familias_streamlit, df_estrutura_streamlit


def adequa_dataset(df_ajustado: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Adequa um conjunto de dados Excel para o formato com colunas simples e extrai os nomes dos elementos estruturais.

    :param df_ajustado: DataFrame com dados de danos e colunas Fi/Fp por elemento (multi-index).

    :return:
        - df_ajustado: DataFrame com colunas renomeadas (ex: "Fi - Pilar P01").
        - nome_elementos: Lista dos nomes dos elementos estruturais.
    """
    elementos_brutos = df_ajustado.columns.get_level_values(0)
    nome_elementos = sorted(set(e for e in elementos_brutos if e != 'Danos'))

    df_ajustado.columns = [
        f"{sub} - {main}" if main != 'Danos' else 'Danos'
        for main, sub in df_ajustado.columns
    ]

    return df_ajustado, nome_elementos


def avalia_elemento(df_ajustado: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Avalia os elementos estruturais com base nos dados de danos e colunas Fi/Fp.

    :param df_ajustado: DataFrame com danos e colunas Fi/Fp por elemento.

    :return: Dicionário onde cada chave é um elemento e o valor é outro dicionário com:
        - 'sum_d': Soma total dos valores d.
        - 'd_max': Valor máximo de d encontrado.
        - 'g_de' : Grau de deterioração estrutural (G_de).
    """
    resultados = {}
    colunas = [col for col in df_ajustado.columns if col != "Danos"]
    elementos = sorted(set(col.split(" - ")[1] for col in colunas))

    for elemento in elementos:
        registros = []

        for _, row in df_ajustado.iterrows():
            dano = str(row["Danos"]).strip()
            if dano.lower() in ["danos", ""] or pd.isna(dano):
                continue

            try:
                fi = float(row[f"Fi - {elemento}"])
                fp = float(row[f"Fp - {elemento}"])
            except (KeyError, ValueError, TypeError):
                fi, fp = 0, 0

            if fi <= 2.0:
                d = 0.8 * fi * fp
            elif fi >= 3.0:
                d = (12 * fi - 28) * fp
            else:
                d = 0

            registros.append(d)

        sum_d = sum(registros)
        d_max = max(registros) if registros else 0
        g_de = d_max * (1 + ((sum_d - d_max) / sum_d)) if sum_d else 0

        resultados[elemento] = {
            'sum_d': sum_d,
            'd_max': d_max,
            'g_de': g_de
        }

    return resultados


def avalia_familia(df_ajustado: pd.DataFrame, nome_arquivo: str, f_r: float = 1.0) -> Dict[str, Dict[str, float]]:
    """
    Avalia a família de elementos estruturais com base nos resultados dos elementos. 

    :param df_ajustado: DataFrame com os dados ajustados.
    :param nome_arquivo: Nome do arquivo (sem caminho e sem extensão).
    :param f_r: Fator de redução (default é 1.0).

    :return: Dicionário com os resultados:
            - gde_max: Valor máximo de g_de encontrado.
            - g_df: Grau de deterioração da família.
            - f_r: Fator de redução.
            - f_r × g_df: Produto do fator de redução pelo grau de deterioração da família.
    """
    resultados_elemento = avalia_elemento(df_ajustado)
    gde_list = [dados['g_de'] for dados in resultados_elemento.values() if dados['g_de'] > 0]

    if not gde_list:
        return {
            nome_arquivo: {
                'gde_max': 0.0,
                'g_df': 0.0,
                'f_r': f_r,
                'f_r × g_df': 0.0,
                'resultados_elemento': resultados_elemento  # ainda útil se quiser ver 0s
            }
        }

    gde_max = max(gde_list)
    gde_sum = sum(gde_list)

    g_df = gde_max * np.sqrt(1 + (gde_sum - gde_max) / gde_sum) if gde_sum else 0
    fr_gdf = f_r * g_df

    return {
        nome_arquivo: {
            'gde_max': gde_max,
            'g_df': float(g_df),
            'f_r': f_r,
            'f_r × g_df': float(fr_gdf),
            'resultados_elemento': resultados_elemento  # <-- resultado por peça
        }
    }

def avaliar_estrutura(resultados_familias: Dict[str, Dict[str, float]]) -> Tuple[float, str]:
    """
    Calcula o grau de deterioração global da estrutura (G_d) e retorna também a classificação e
    recomendação com base no valor de G_d.

    Tabela de níveis:
        -  0–15: Baixo
        - 16–50: Médio
        - 51–80: Alto
        - 81–100: Sofrível

    :param resultados_familias: Dicionário com resultados de cada família.

    :return:
        - g_d (float): Grau de deterioração global.
        - nivel (str): Nível de deterioração.
        - recomendacao (str): Recomendação de ação.
    """
    numerador = 0.0
    denominador = 0.0

    for _, dados in resultados_familias.items():
        fr = dados.get('f_r', 0)
        gdf = dados.get('g_df', 0)
        numerador += fr * gdf
        denominador += fr

    g_d = numerador / denominador if denominador else 0.0

    if g_d <= 15:
        nivel = "Baixo"
        recomendacao = "Estado aceitável. Manutenção preventiva."
    elif g_d <= 50:
        nivel = "Médio"
        recomendacao = "Nova inspeção e plano de intervenção em longo prazo (até 2 anos)."
    elif g_d <= 80:
        nivel = "Alto"
        recomendacao = "Inspeção detalhada e intervenção em médio prazo (até 18 meses)."
    else:
        nivel = "Sofrível"
        recomendacao = "Inspeção detalhada e intervenção em curto prazo."

    return g_d, nivel, recomendacao