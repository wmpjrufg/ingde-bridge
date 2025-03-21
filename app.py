import pandas as pd
import streamlit as st
import zipfile
import io
from math import sqrt
import base64

def gde(excel_data, fr):
    resultados = []
    sum_fr = 0
    for elemento in excel_data.columns.get_level_values(0).unique():
        fi_col = (elemento, 'Fi')
        fp_col = (elemento, 'Fp')
        if fi_col in excel_data.columns and fp_col in excel_data.columns:
            d_values = []
            for fi, fp in zip(excel_data[fi_col], excel_data[fp_col]):
                if fi <= 2.0:
                    d = 0.8 * fi * fp
                elif fi >= 3.0:
                    d = (12 * fi - 28) * fp
                else:
                    d = 0
                d_values.append(d)
            d_total = sum(d_values)
            d_max = max(d_values)
            gde = d_max * (1 + ((d_total - d_max) / d_total)) if d_total != 0 else 0
            gde_values = [gde]
            gde_max = max(gde_values)
            gde_total = sum(gde_values)
            gdf = gde_max * sqrt(1 + gde_total - gde_max) / gde_total if gde_total != 0 else 0
            fr_gdf = fr * gdf
            sum_fr += fr
            resultados.append({
                "Elemento": elemento,
                "∑D": d_total,
                "Dₘₐₓ": d_max,
                "Gdₑ": gde,
                "Fᵣ × Gdf": fr_gdf
            })
    result_df = pd.DataFrame(resultados)
    result_df.reset_index(drop=True, inplace=True)
    return result_df, sum_fr, fr_gdf

def image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode("utf-8")

st.title("Automação inspeção GDE")

st.markdown("""
Para gerar o relatório de inspeção automatizado via metodologia GDE, baixe a nossa planilha modelo ([acesse aqui](https://github.com/wmpjrufg/inspgde.git)) e preencha os dados da inspeção.

Após o preenchimento da inspeção, crie um arquivo `.zip` que contenha os seguintes documentos:

```
dados.zip
├── fotos.zip
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
└── planilha_inspecao.xlsx
```
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
                    if file.endswith("fotos.zip"):
                        encontrou_fotos = True
                        with zip_ref.open(file) as fz:
                            with zipfile.ZipFile(fz) as fotos_zip:
                                for img_name in fotos_zip.namelist():
                                    if img_name.lower().endswith(('.png','.jpg','.jpeg')):
                                        img_data = fotos_zip.read(img_name)
                                        img_b64 = image_to_base64(img_data)
                                        fotos_base64.append((img_name, img_b64))
                if encontrou_fotos:
                    st.success(f"✅ Família {i+1}: Arquivo 'fotos.zip' encontrado e processado com sucesso.")
                else:
                    st.warning(f"⚠️ Família {i+1}: Nenhum 'fotos.zip' encontrado.")

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
                            resultados_finais.append((f"Família_{i+1}_{file}", resultado))

                            html_output += f"<h2>Família {i+1} - {file}</h2>"
                            html_output += resultado.to_html(index=False, border=1)
                            descricao_familia = fr_descricao[fr]
                            html_output += f"<p><strong>Fator de Importância:</strong> \\( F_r = {fr} \\) – {descricao_familia}</p>"

                            html_output += """
                            <h3>Cálculo do G<sub>df</sub> (Grau de Deficiência Familiar):</h3>
                            <p><em>Fórmula:</em></p>
                            <p>\\[ G_{df} = G_{de,max} \\cdot \\sqrt{1 + \\frac{\\left( \\sum_{i=1}^{m} G_{de,i} \\right) - G_{de,max}}{\\sum_{i=1}^{m} G_{de,i}}} \\]</p>
                            """

                            gde_list = resultado["Gdₑ"].tolist()
                            gde_max = max(gde_list)
                            gde_sum = sum(gde_list)
                            gdf = gde_max * sqrt(1 + (gde_sum - gde_max)/gde_sum) if gde_sum else 0
                            fr_gdf = fr * gdf
                            html_output += f"""
                            <table class='calc-table'>
                            <tr><th colspan='2'>Cálculo de G<sub>df</sub></th></tr>
                            <tr><td>G<sub>de,max</sub></td><td>{gde_max:.4f}</td></tr>
                            <tr><td>&#8721; G<sub>de,i</sub></td><td>{gde_sum:.4f}</td></tr>
                            <tr><td>G<sub>df</sub></td><td>{gde_max:.4f} × √(1 + (({gde_sum:.4f} - {gde_max:.4f}) / {gde_sum:.4f})) = {gdf:.4f}</td></tr>
                            <tr><td>F<sub>r</sub> × G<sub>df</sub></td><td>{fr} × {gdf:.4f} = <b>{fr_gdf:.4f}</b></td></tr>
                            </table>
                            """
                            if fotos_base64:
                                html_output += "<h3>Fotos da inspeção:</h3><div class='image-gallery'>"
                                for img_name, img_b64 in sorted(fotos_base64):
                                    html_output += f"<div class='image-box'><img src='data:image/jpeg;base64,{img_b64}'><div><small>{img_name}</small></div></div>"
                                html_output += "</div>"

                if not encontrou_planilha:
                    st.error(f"❌ Família {i+1}: Nenhuma planilha .xlsx/.xls encontrada.")

    if resultados_finais:
        html_output += "<hr><h2>Determinação do GD</h2>"
        gd_final = sum_fr_gdf_total / sum_fr_total if sum_fr_total != 0 else 0
        if gd_final <= 15:
            nivel, acao = "Baixo", "Estado aceitável. Manutenção preventiva."
        elif gd_final <= 50:
            nivel, acao = "Médio", "Nova inspeção e plano de intervenção em longo prazo (até 2 anos)."
        elif gd_final <= 80:
            nivel, acao = "Alto", "Inspeção detalhada e intervenção em médio prazo (até 18 meses)."
        else:
            nivel, acao = "Sofrível", "Inspeção detalhada e intervenção em curto prazo."
        html_output += f"""<table class='calc-table'>
        <tr><th colspan='2'>Resumo Determinação GD</th></tr>
        <tr><td>∑(Fr × Gdf)</td><td>{sum_fr_gdf_total:.4f}</td></tr>
        <tr><td>∑ Fr</td><td>{sum_fr_total:.4f}</td></tr>
        <tr><td><b>GD</b></td><td><b>{gd_final:.4f}</b></td></tr>
        <tr><td>Nível de Deterioração</td><td>{nivel}</td></tr>
        <tr><td>Ação Recomend.</td><td>{acao}</td></tr>
        </table>"""
    html_output += "</body></html>"
    st.session_state.html_output = html_output

if st.session_state.html_output:
    st.download_button("Baixar Relatório Consolidado (.html)", st.session_state.html_output.encode("utf-8"), "relatorio_gda.html", mime="text/html")
