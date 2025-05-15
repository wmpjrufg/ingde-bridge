import pandas as pd
import streamlit as st
import numpy as np
import zipfile
import base64

from pathlib import Path
from math import sqrt


def calcular_gde_por_peca(dfs_por_peca):
    resultados_gde = {}

    for peca, df in dfs_por_peca.items():
        d_values = df['d'].values

        if len(d_values) == 0 or d_values.sum() == 0:
            resultados_gde[peca] = {
                'gde': 0,
                'gde_max': 0,
                'gde_total': 0,
                'gdf': 0
            }
            continue

        d_total = d_values.sum()
        d_max = d_values.max()

        # Cálculo do GDE (apenas um valor por peça)
        gde = d_max * (1 + ((d_total - d_max) / d_total))

        # Como só há um GDE por peça, os valores são simples:
        gde_max = gde
        gde_total = gde
        gdf = gde_max * np.sqrt(1 + (gde_total - gde_max) / gde_total) if gde_total else 0

        resultados_gde[peca] = {
            'gde': gde,
            'gde_max': gde_max,
            'gde_total': gde_total,
            'gdf': gdf
        }

    return resultados_gde


def gde(df_raw, fr):
    df = df_raw.fillna(0).copy()
    col_dano = df.columns[0]

    # Corrigir extração dos nomes das peças, excluindo a coluna "Danos"
    pecas = [p for p in df.columns.levels[0] if str(p).lower() != "danos"]

    registros = []

    for i in range(len(df)):
        dano = str(df.iloc[i, 0]).strip()
        if dano.lower() == 'danos' or dano == '':
            continue

        for peca in pecas:
            try:
                fi_raw = df[(peca, 'Fi')].iloc[i]
                fp_raw = df[(peca, 'Fp')].iloc[i]
                fi = float(fi_raw) if pd.notna(fi_raw) else 0
                fp = float(fp_raw) if pd.notna(fp_raw) else 0
            except (KeyError, ValueError, TypeError):
                fi, fp = 0, 0

            if fi <= 2.0:
                d = 0.8 * fi * fp
            elif fi >= 3.0:
                d = (12 * fi - 28) * fp
            else:
                d = 0

            registros.append({
                'peça': str(peca).strip(),
                'dano': dano,
                'fi': fi,
                'fp': fp,
                'd': d
            })

    df_resultado = pd.DataFrame(registros)

    # Agrupar por peça e calcular GDEs
    dfs_por_peca = {
        peca: df_resultado[df_resultado['peça'] == peca].reset_index(drop=True)
        for peca in df_resultado['peça'].unique()
    }

    gde_por_peca = calcular_gde_por_peca(dfs_por_peca)

    # Criar DataFrame para exibir na tabela final
    resultado_familia = []
    gde_list = []
    for peca, valores in gde_por_peca.items():
        gde_list.append(valores['gde'])
        resultado_familia.append({
            "Elemento": peca,
            r"$$\sum D$$": valores['gde_total'],
            "$$D_{max}$$": valores['gde_max'],
            "$$G_{de}$$": valores['gde'],
            "$$F_r × G_{df}$$": fr * valores['gdf']
        })

    gde_max = max(gde_list) if gde_list else 0
    gde_sum = sum(gde_list) if gde_list else 0
    gdf = gde_max * np.sqrt(1 + (gde_sum - gde_max) / gde_sum) if gde_sum else 0
    fr_gdf = fr * gdf

    df_tabela = pd.DataFrame(resultado_familia)

    return df_tabela, fr, fr_gdf


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


# Inicializa a página Streamlit 
st.title("Automação inspeção GDE/UnB a OAEs")
img_base64 = image_to_base64("assets/images/GDE-logo.png")
img_html = f'<img src="data:image/png;base64,{img_base64}" width="150"/>'

# Texto de entrada
st.markdown(rf""" 
<table>
  <tr>
    <td style="width:70%;">
      <p align="justify">
        A ferramenta inGDE-Bridge é um <i>software</i> para automatização da inspeção de pontes com o metdologia GDE/UnB. 
        O <i>software</i> foi desenvovlido pelo grupo de pesquisa liderado pelo professor Wanderlei Malaquias Pereira Junior 
        da Faculdade  de Engenharia da Universidade Federal de Catalão. A plataforma foi construída usando a linguagem Python e o <i>framework</i> Streamlit. 
      </p>
    </td>
    <td style="width:100%; text-align: center;">{img_html}</td>  
  </tr>
</table>  
""", unsafe_allow_html=True)

# E-mail de contato
st.markdown(
    """
    <style>
    .suggestions-box1 {
        border: 2px solid #00008B;
        background-color: #ADD8E6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    ::-webkit-scrollbar {
     width: 18px;
    }

    /* Estiliza o fundo da barra de rolagem */
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    /* Estiliza o "thumb" da barra de rolagem */
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }

    /* Muda a cor quando hover */
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    
    <div class="suggestions-box1">
        <h4>Sugestões</h4>
        <p>Se você tiver alguma sugestão ou quiser relatar erros relacionados ao funcionamento do algoritmo, 
        envie um e-mail para <a href="mailto:wanderlei_junior@ufcat.edu.br">wanderlei_junior@ufcat.edu.br</a>. 
        Ficaremos felizes em aprimorar a ferramenta.</p>
    </div>
    """,
    unsafe_allow_html=True)
st.write("")

# Equipe
st.markdown(
    """    
    <style>
    .suggestions-box {
        border: 2px solid #FFA500;
        background-color: #FFF3CD;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    .suggestions-box p {
        margin: 5px 0;
    }
    .suggestions-box a {
        text-decoration: none;
        color: #007BFF;
        font-weight: bold;
    }
    </style>

    <div class="suggestions-box">
        <h4>Equipe</h4>
        <p><a href="http://lattes.cnpq.br/2268506213083114" target="_blank">Prof. Wanderlei Malaquias Pereira Junior</a></p>
        <p><a href="https://orcid.org/0000-0003-0215-8701" target="_blank">Prof. Hunmberto Salazar Varum</a></p>
        <p><a href="https://orcid.org/0000-0003-0964-880X" target="_blank">Prof. Wellington Andrade da Silva</a></p>
        <p><a href="" target="_blank">Eng. Marcus Vinicius Nascimento</a></p>
        <p><a href="" target="_blank">Eng. Pedro Henrique Gomes</a></p>
        <p><a href="http://orcid.org/0009-0008-4084-2137" target="_blank">Discente Luiz Henrique Ferreira Rezio</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
st.write("")

st.subheader("Como usar")
st.markdown("""
Para gerar o relatório de inspeção automatizado via metodologia GDE, baixe o conjunto de planilhas modelo ([acesse aqui](https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/)) e preencha os dados da inspeção.

Após o preenchimento da inspeção com os seus dados, crie um arquivo `.zip` que contenha os seguintes documentos:

```
dados_inspecao.zip
├── fotos
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
└── planilha_inspecao.xlsx
```

- fotos: Pasta que contenha as imagens em formato `.png`, `.jpg` ou `.jpeg` da inspeção realizada.
- planilha_inspecao.xlsx: Planilha modelo preenchida com os dados da inspeção relativo ao elemento avaliado. O nome do arquivo não deve conter espaços ou caracteres especiais.
""")

fr_descricao = {
    1: "Barreiras, guarda-corpo, guarda rodas, pista de rolamento",
    2: "Juntas de dilatação",
    3: "Transversinas, cortinas, alas",
    4: "Lajes, fundações, vigas secundárias, aparelhos de apoio",
    5: "Vigas e pilares principais",
}

if "html_output" not in st.session_state:
    st.session_state.html_output = None

num_familias = st.number_input("Para quantas famílias de elementos você deseja gerar o relatório?", min_value=1, step=1)

uploaded_zips = []
fr_selecionados = []

for i in range(num_familias):
    st.markdown(f"### Família {i+1}")
    uploaded_zip = st.file_uploader(f"Faça upload do arquivo .zip para a Família {i+1}", type=["zip"], key=f"zip_{i}")
    fr = st.selectbox(f"Selecione o grupo familiar para a Família {i+1}", options=list(fr_descricao.keys()), format_func=lambda x: f"{fr_descricao[x]}", key=f"fr_{i}")
    uploaded_zips.append(uploaded_zip)
    fr_selecionados.append(fr)

if st.button("Calcular"):
    st.session_state["calculado"] = True 
    resultados_finais = []
    sum_fr_total = 0
    sum_fr_gdf_total = 0

    html_output = """<html>
    <head>
        <meta charset='utf-8'><title>Relatório GDE</title>
        <style>
        body { font-family: Arial; margin: 30px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
        .calc-table { width: 60%; margin: 10px 0 30px; border: 1px solid #ccc; }
        .calc-table td { text-align: left; padding: 6px; }
        .image-gallery { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 20px; }
        .image-box { width: 300px; text-align: center; }
        .image-box img { width: 100%; border: 1px solid #ccc; border-radius: 5px; }
        </style>
        <script src='https://polyfill.io/v3/polyfill.min.js?features=es6'></script>
        <script id='MathJax-script' async src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script>
    </head><body><h1>Relatório Consolidado GDE</h1>
    """

    for i in range(num_familias):
        uploaded_zip = uploaded_zips[i]
        fr = fr_selecionados[i]
        if uploaded_zip:
            processou_valido = False
            with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
                fotos_base64 = []
                encontrou_fotos = False
                encontrou_planilha = False
                for file in zip_ref.namelist():
                    if file.startswith("fotos/") and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        encontrou_fotos = True
                        img_data = zip_ref.read(file)
                        img_b64 = image_to_base64(img_data)
                        fotos_base64.append((file.split("/")[-1], img_b64))
                if encontrou_fotos:
                    st.success(f"✅ Família {i+1}: Imagens na pasta 'fotos' encontradas e processadas com sucesso.")
                else:
                    st.warning(f"⚠️ Família {i+1}: Nenhuma imagem encontrada na pasta 'fotos'.")

                for file in zip_ref.namelist():
                    if file.endswith(('.xlsx','.xls')):
                        encontrou_planilha = True
                        processou_valido = True
                        st.success(f"✅ Família {i+1}: Planilha encontrada e processada com sucesso.")
                        with zip_ref.open(file) as f:
                            df = pd.read_excel(f, header=[0,1])
                            resultado, sum_fr, fr_gdf = gde(df, fr)

                        if processou_valido:
                            sum_fr_total += sum_fr
                            sum_fr_gdf_total += fr_gdf
                            resultados_finais.append({
                                "nome_arquivo": uploaded_zip.name,
                                "fr": fr,
                                "fr_gdf": fr_gdf,
                                "resultado": resultado
                            })

                            html_output += f"<br><hr><h2>Família {i+1} - {file}</h2>"

                            # Substituir NaNs por 0
                            df_html = df.fillna(0).copy()

                            # Separar colunas e valores
                            colunas = df_html.columns.tolist()
                            valores = df_html.values.tolist()

                            # Gerar cabeçalho com rowspan (para "Dano") e colspan (para as peças)
                            cabecalho_1 = "<tr><th rowspan='2'>Dano</th>"
                            cabecalho_2 = ""

                            for col in colunas[1:]:
                                if isinstance(col, tuple):
                                    nome_peca, tipo = col
                                else:
                                    nome_peca, tipo = col, ""

                                if tipo.lower() == "fi":
                                    cabecalho_1 += f"<th colspan='2'>{nome_peca}</th>"

                            cabecalho_1 += "</tr>\n<tr>"

                            # Construir segundo nível de cabeçalho (Fi, Fp)
                            for col in colunas[1:]:
                                if isinstance(col, tuple):
                                    _, tipo = col
                                else:
                                    tipo = col
                                cabecalho_2 += f"<th>{tipo}</th>"

                            cabecalho_2 += "</tr>"

                            corpo = ""
                            for row in valores:
                                corpo += "<tr>"
                                for val in row:
                                    corpo += f"<td>{val}</td>"
                                corpo += "</tr>\n"

                            html_output += """
                            <h3>Tabela original da inspeção</h3>
                            <table border="1" cellspacing="0" cellpadding="6">
                            """
                            html_output += cabecalho_1 + cabecalho_2 + corpo + "</table>"

                            html_output += """
                            <br><hr>
                            <h3>Resultados por peça (G<sub>de</sub>)</h3>
                            """
                            html_output += resultado.to_html(index=False, border=1, escape=False)

                            descricao_familia = fr_descricao[fr]
                            html_output += f"<p><strong>Fator de Importância:</strong> \\( F_r = {fr} \\) – {descricao_familia}</p>"

                            # html_output += """
                            # <h3>Cálculo do G<sub>df</sub> (Grau de Deficiência Familiar):</h3>
                            # <p><em>Fórmula:</em></p>
                            # <p>\\[ G_{df} = G_{de,max} \\cdot \\sqrt{1 + \\frac{\\left( \\sum_{i=1}^{m} G_{de,i} \\right) - G_{de,max}}{\\sum_{i=1}^{m} G_{de,i}}} \\]</p>
                            # """

                            html_output += """
                            <br>
                            <h3>Cálculo do G<sub>df</sub> (Grau de Deficiência Familiar):</h3>
                            """
                            gde_list = resultado["$$G_{de}$$"].tolist()
                            gde_max = max(gde_list)
                            gde_sum = sum(gde_list)
                            gdf = gde_max * sqrt(1 + (gde_sum - gde_max) / gde_sum) if gde_sum else 0
                            fr_gdf = fr * gdf

                            # Fórmula com os valores injetados
                            latex_formula = f"""
                            \\[
                            G_{{df}} = {gde_max:.4f} \\cdot \\sqrt{{1 + \\frac{{({gde_sum:.4f} - {gde_max:.4f})}}{{{gde_sum:.4f}}}}} = {gdf:.4f}
                            \\]
                            <br>
                            \\[
                            F_{{r}} \\cdot G_{{df}} = {fr:.4f} \\cdot {gdf:.4f} = \\mathbf{{{fr_gdf:.4f}}}
                            \\]
                            """

                            html_output += latex_formula

                            if fotos_base64:
                                html_output += "<hr><h3>Fotos da inspeção:</h3><div class='image-gallery'>"
                                for img_name, img_b64 in sorted(fotos_base64):
                                    html_output += f"<div class='image-box'><img src='data:image/jpeg;base64,{img_b64}'><div><small>{img_name}</small></div></div>"
                                html_output += "</div>"

                if not encontrou_planilha:
                    st.error(f"❌ Família {i+1}: Nenhuma planilha .xlsx/.xls encontrada.")


    if resultados_finais:
        resumo_familias = []
        for i, dados in enumerate(resultados_finais):
            nome_arquivo = dados["nome_arquivo"]
            fr = dados["fr"]
            fr_gdf = dados["fr_gdf"]
            resumo_familias.append({
                "Família / Arquivo": f"Família {i+1} – {nome_arquivo}",
                "Fator de Importância (F_r)": fr,
                "F_r × G_df": fr_gdf
            })

        df_resumo_familias = pd.DataFrame(resumo_familias)

        # Grau de deterioração final
        gd_final = sum_fr_gdf_total / sum_fr_total if sum_fr_total != 0 else 0
        if gd_final <= 15:
            nivel = "Baixo"
            acao = "Estado aceitável. Manutenção preventiva."
        elif gd_final <= 50:
            nivel = "Médio"
            acao = "Nova inspeção e plano de intervenção em longo prazo (até 2 anos)."
        elif gd_final <= 80:
            nivel = "Alto"
            acao = "Inspeção detalhada e intervenção em médio prazo (até 18 meses)."
        else:
            nivel = "Sofrível"
            acao = "Inspeção detalhada e intervenção em curto prazo."

        dados_estrutura = {
            "∑(F_r × G_df)": sum_fr_gdf_total,
            "∑ F_r": sum_fr_total,
            "Grau de Deterioração da Estrutura (G_d)": gd_final,
            "Nível de Deterioração": nivel,
            "Ação Recomendada": acao
        }

        df_grau_estrutura = pd.DataFrame([(k, str(v)) for k, v in dados_estrutura.items()], columns=["Descrição", "Valor"])

        st.session_state["df_resumo_familias"] = df_resumo_familias
        st.session_state["df_grau_estrutura"] = df_grau_estrutura

        html_output += """
        <hr>
        <h2>Resumo dos Resultados por Família</h2>
        """ + st.session_state["df_resumo_familias"].to_html(index=False, border=1, escape=False)

        html_output += """
        <hr>
        <h2>Grau de Deterioração da Estrutura</h2>
        """ + st.session_state["df_grau_estrutura"].to_html(index=False, border=1, escape=False)

        html_output += "</body></html>"
        st.session_state["html_output"] = html_output

        html_output += "</body></html>"
        st.session_state["html_output"] = html_output

if st.session_state.get("calculado", False):

    if "df_resumo_familias" in st.session_state:
        st.subheader("Resumo dos Resultados por Família")
        st.dataframe(st.session_state["df_resumo_familias"], use_container_width=True)

    if "df_grau_estrutura" in st.session_state:
        st.subheader("Grau de Deterioração da Estrutura")
        st.dataframe(st.session_state["df_grau_estrutura"], use_container_width=True)

    if "html_output" in st.session_state and st.session_state.html_output:
        st.download_button(
            "Baixar relatório detalhado (.html)",
            st.session_state["html_output"].encode("utf-8"),
            file_name="relatorio_gda.html",
            mime="text/html"
        )
