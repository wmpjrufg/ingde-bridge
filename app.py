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
                "sum(d)": d_total,
                "d_max": d_max,
                "gde": gde,
                "gdf": fr_gdf
            })

    result_df = pd.DataFrame(resultados)
    result_df.reset_index(drop=True, inplace=True)
    return result_df, sum_fr, fr_gdf

def image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode("utf-8")

# Streamlit App
st.title("GDA - Relatório Consolidado por Famílias de Elementos")

fr_descricao = {
    1: "Barreiras, guarda-corpo, guarda rodas, pista de rolamento",
    2: "Juntas de dilatação",
    3: "Transversinas, cortinas, alas",
    4: "Lajes, fundações, vigas secundárias, aparelhos de apoio",
    5: "Vigas e pilares principais",
}

if "html_output" not in st.session_state:
    st.session_state.html_output = None

# Número de famílias
num_familias = st.number_input("Para quantas famílias de elementos você deseja gerar o relatório?", min_value=1, step=1)

uploaded_zips = []
fr_selecionados = []

for i in range(num_familias):
    st.markdown(f"### Família {i+1}")
    uploaded_zip = st.file_uploader(f"Faça upload do arquivo .zip para a Família {i+1}", type=["zip"], key=f"zip_{i}")
    fr = st.selectbox(
        f"Selecione o grupo familiar para a Família {i+1}",
        options=list(fr_descricao.keys()),
        format_func=lambda x: f"{fr_descricao[x]}",
        key=f"fr_{i}"
    )
    uploaded_zips.append(uploaded_zip)
    fr_selecionados.append(fr)

if st.button("Calcular"):
    resultados_finais = []
    sum_fr_total = 0
    sum_fr_gdf_total = 0

    html_output = "<html><head><meta charset='utf-8'><title>Relatório GDA</title></head><body>"
    html_output += "<h1>Relatório Consolidado GDA</h1>"

    for i in range(num_familias):
        uploaded_zip = uploaded_zips[i]
        fr = fr_selecionados[i]

        if uploaded_zip:
            with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
                fotos_base64 = []

                # Primeiro, localizar fotos.zip e processar as imagens
                for file in zip_ref.namelist():
                    if file.endswith("fotos.zip"):
                        with zip_ref.open(file) as fz:
                            with zipfile.ZipFile(fz) as fotos_zip:
                                for img_name in fotos_zip.namelist():
                                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                        img_data = fotos_zip.read(img_name)
                                        img_b64 = image_to_base64(img_data)
                                        fotos_base64.append((img_name, img_b64))

                # Agora processar os arquivos Excel
                for file in zip_ref.namelist():
                    if file.endswith(('.xlsx', '.xls')):
                        with zip_ref.open(file) as f:
                            df = pd.read_excel(f, header=[0, 1])
                            resultado, sum_fr, fr_gdf = gde(df, fr)

                            sum_fr_total += sum_fr
                            sum_fr_gdf_total += fr_gdf
                            resultados_finais.append((f"Família_{i+1}_{file}", resultado))

                            html_output += f"<h2>Família {i+1} - {file}</h2>"
                            html_output += resultado.to_html(index=False, border=1)

                            # Adicionar fotos da inspeção ao HTML
                            if fotos_base64:
                                html_output += "<h3>Fotos da inspeção:</h3><div style='display:flex; flex-wrap:wrap;'>"
                                for img_name, img_b64 in fotos_base64:
                                    html_output += f"""
                                        <div style="margin:10px; text-align:center;">
                                            <img src="data:image/jpeg;base64,{img_b64}" width="300"/><br>
                                            <small>{img_name}</small>
                                        </div>
                                    """
                                html_output += "</div>"

    if resultados_finais:
        # gd = sum_fr_gdf_total / sum_fr_total if sum_fr_total != 0 else 0
        # html_output += f"<hr><h3>Somatório total dos F_r: {sum_fr_total}</h3>"
        # html_output += f"<h3>Somatório total dos F_r * gdf: {sum_fr_gdf_total:.4f}</h3>"
        # html_output += f"<h3>GD: {gd:.4f}</h3>"
        html_output += "</body></html>"

        st.session_state.html_output = html_output

# Mostrar botão de download se relatório foi gerado
if st.session_state.html_output:
    st.markdown("### 📄 Download do Relatório Consolidado")
    st.download_button(
        label="Baixar Relatório Consolidado (.html)",
        data=st.session_state.html_output.encode("utf-8"),
        file_name="relatorio_gda.html",
        mime="text/html"
    )
