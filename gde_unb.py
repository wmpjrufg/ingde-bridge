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


def gerar_relatorio_html(
    resultados_familias: Dict[str, Dict[str, float]],
    g_d: float,
    mensagem: str,
    tabelas_originais: Dict[str, pd.DataFrame],
    imagens_por_familia: Dict[str, list],
    fr_lista: List[int],
    fr_descricao: Dict[int, str]
) -> str:
    """
    Gera HTML detalhado com:
    - Tabela original da inspeção
    - Resultados por peça (G_de)
    - Cálculo do G_df com fórmulas em LaTeX
    - Galeria de imagens centralizadas
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

    for i, (nome, dados) in enumerate(resultados_familias.items()):
        fr = dados["f_r"]
        descricao = fr_descricao.get(fr, "")
        gde_max = dados["gde_max"]
        gdf = dados["g_df"]
        fr_gdf = dados["f_r × g_df"]

        html += f"<hr><h2>Família - {nome}</h2>"

        # Tabela original
        if nome in tabelas_originais:
            df_html = tabelas_originais[nome].fillna(0)
            html += "<h3>Tabela original da inspeção</h3>"
            html += df_html.to_html(index=False, border=1)

        # Galeria de imagens
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

        # Resultados numéricos e fórmula de G_df
        html += """
        <h3>Resultados por peça ($G_{de}$)</h3>
        <table>
            <tr><th>Elemento</th><th>$$\\sum D$$</th><th>$$D_{max}$$</th><th>$$G_{de}$$</th><th>$$F_r \\times G_{df}$$</th></tr>
        """
        for j in range(2):  # assumindo dois elementos por família
            html += f"<tr><td>Peça {j+1}</td><td>{gde_max:.1f}</td><td>{gde_max:.1f}</td><td>{gde_max:.1f}</td><td>{fr_gdf:.1f}</td></tr>"
        html += "</table>"

        html += f"<p><strong>Fator de Importância:</strong> $F_r = {fr}$ – {descricao}</p>"

        gde_sum = gde_max * 2
        formula = f"""
        <h3>Cálculo do $G_{{df}}$ (Grau de Deficiência Familiar):</h3>
        \\[
        G_{{df}} = {gde_max:.4f} \\cdot \\sqrt{{1 + \\frac{{({gde_sum:.4f} - {gde_max:.4f})}}{{{gde_sum:.4f}}}}} = {gdf:.4f}
        \\]
        \\[
        F_r \\cdot G_{{df}} = {fr:.4f} \\cdot {gdf:.4f} = \\mathbf{{{fr_gdf:.4f}}}
        \\]
        """
        html += formula

    html += f"""
    <hr><h2>Resumo Final da Estrutura</h2>
    <p><strong>Grau de Deterioração da Estrutura ($G_d$):</strong> {g_d:.2f}</p>
    <p><strong>Classificação e Ação Recomendada:</strong><br>{mensagem}</p>
    </body></html>
    """

    return html


def adequa_dataset(df_ajustado: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], str]:
    """
    Adequa um conjunto de dados Excel para o formato com colunas simples e extrai os nomes dos elementos estruturais.

    :param df_ajustado: DataFrame com dados de danos e colunas Fi/Fp por elemento.

    :return:
        - df_ajustado: DataFrame com colunas renomeadas (ex: "Fi - Elemento 1").
        - nome_elementos: Lista dos nomes dos elementos estruturais.
        - nome_arquivo: Nome do arquivo (sem caminho e sem extensão).
    """
    elementos_brutos = df_ajustado.columns.get_level_values(0)
    nome_elementos = sorted(set(e for e in elementos_brutos if e != 'Danos'))
    df_ajustado.columns = [
        f"{sub} - {main}" if main != 'Danos' else 'Danos'
        for main, sub in df_ajustado.columns
    ]
    nome_arquivo = "arquivo_sem_nome"  # você pode passar o nome por fora
    return df_ajustado, nome_elementos, nome_arquivo


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


def avalia_familia(df_ajustado: pd.DataFrame, nome_arquivo: str, f_r: float = 1.0) -> Dict[str, float]:
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
                'f_r × g_df': 0.0
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
            'f_r × g_df': float(fr_gdf)
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
        - mensagem (str): Nível e ação recomendada.
    """
    numerador = 0.0
    denominador = 0.0

    for familia, dados in resultados_familias.items():
        fr = dados.get('f_r', 0)
        gdf = dados.get('g_df', 0)

        numerador += fr * gdf
        denominador += fr

    g_d = numerador / denominador if denominador else 0.0

    # Classificação baseada na tabela
    if g_d <= 15:
        nivel = "Baixo"
        recomendacao = "Estado aceitável. Manutenção preventiva."
    elif g_d <= 50:
        nivel = "Médio"
        recomendacao = "Definir prazo/natureza para nova inspeção. Planejar intervenção em longo prazo (máximo 2 anos)."
    elif g_d <= 80:
        nivel = "Alto"
        recomendacao = "Definir prazo/natureza para inspeção especializada detalhada. Planejar intervenção em médio prazo (máximo 18 meses)."
    else:
        nivel = "Sofrível"
        recomendacao = "Definir prazo/natureza para inspeção especializada detalhada. Planejar intervenção em curto prazo."

    mensagem = f"Nível de Deterioração: {nivel} (G_d = {g_d:.2f})\nAção recomendada: {recomendacao}"

    return g_d, mensagem