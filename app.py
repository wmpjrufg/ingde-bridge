import streamlit as st
import zipfile
import pandas as pd
from io import BytesIO
import os
from gde_unb import (
    adequa_dataset,
    avalia_elemento,
    avalia_familia,
    avaliar_estrutura,
    gerar_relatorio_html,
    image_to_base64
)

st.set_page_config(page_title="Inspeção GDE/UnB", layout="wide")
st.title("Automatização da Inspeção GDE/UnB")

st.markdown("""
<p align="justify">
<<<<<<< HEAD
Envie arquivos .zip contendo <strong>uma planilha</strong> e a pasta <code>fotos</code> com imagens da inspeção.
Cada arquivo deve representar uma família de elementos estruturais.</p>
=======
Após o preenchimento da inspeção com os seus dados, crie um arquivo <code>.zip</code> que contenha os seguintes documentos:
</p>

<pre><code>dados_inspecao.zip
├── fotos
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
└── planilha_inspecao_com_nome_familia.xlsx</code></pre>
            
<ul>
    <li><p align="justify"><strong>fotos</strong>: Pasta que contenha as imagens em formato <code>.png</code>, <code>.jpg</code> ou <code>.jpeg</code> da inspeção realizada.</p></li>
    <li><p align="justify"><strong>planilha_inspecao.xlsx</strong>: Planilha modelo preenchida com os dados da inspeção relativa ao elemento avaliado. O nome do arquivo não deve conter espaços ou caracteres especiais. Recomenda-se aqui a colocação do nome da planilha como o próprio nome da família.</p></li>
</ul>
            
<p align="justify">
O usuário pode criar vários arquivos <code>.zip</code> com diferentes famílias de elementos, desde que cada arquivo <code>.zip</code> contenha a mesma estrutura para apenas uma família de elementos.
</p>
>>>>>>> 2132ab64555f1d60b738a94e184b87b7569d4c7a
""", unsafe_allow_html=True)

fr_descricao = {
    1: "Barreiras, guarda-corpo, guarda rodas, pista de rolamento",
    2: "Juntas de dilatação",
    3: "Transversinas, cortinas, alas",
    4: "Lajes, fundações, vigas secundárias, aparelhos de apoio",
    5: "Vigas e pilares principais",
}

num_familias = st.number_input("Quantas famílias deseja processar?", min_value=1, step=1)

uploaded_zips = []
fr_selecionados = []

for i in range(num_familias):
    st.markdown(f"### Família {i+1}")
    uploaded_zip = st.file_uploader(f"Upload .zip da Família {i+1}", type="zip", key=f"zip_{i}")
    fr = st.selectbox(f"Grupo familiar (F_r) da Família {i+1}", options=list(fr_descricao.keys()),
                      format_func=lambda x: f"F_r = {x} - {fr_descricao[x]}", key=f"fr_{i}")
    uploaded_zips.append(uploaded_zip)
    fr_selecionados.append(fr)

if st.button("Calcular"):
    resultados_familias = {}
    tabelas_originais = {}
    imagens_por_familia = {}

    for i, (uploaded_zip, fr) in enumerate(zip(uploaded_zips, fr_selecionados)):
        if uploaded_zip:
            with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                planilha_nome = next((f for f in zip_ref.namelist() if f.endswith(('.xlsx', '.xls'))), None)
                if not planilha_nome:
                    st.error(f"Família {i+1}: Nenhuma planilha encontrada no .zip")
                    continue

                fotos_base64 = []
                for file in zip_ref.namelist():
                    if file.startswith("fotos/") and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_data = zip_ref.read(file)
                        img_b64 = image_to_base64(img_data)
                        fotos_base64.append((file.split("/")[-1], img_b64))

                with zip_ref.open(planilha_nome) as f:
                    df_raw = pd.read_excel(f, header=[0, 1])
                    df_ajustado, _, nome_arquivo = adequa_dataset(df_raw)

                    resultado_familia = avalia_familia(df_ajustado, nome_arquivo, f_r=fr)
                    resultados_familias.update(resultado_familia)
                    tabelas_originais[nome_arquivo] = df_raw
                    imagens_por_familia[nome_arquivo] = fotos_base64

                    st.success(f"Família {i+1} ({nome_arquivo}) processada com sucesso.")
                    st.write(f"{len(fotos_base64)} imagem(ns) carregadas.")

    if resultados_familias:
        g_d, mensagem = avaliar_estrutura(resultados_familias)
        html_output = gerar_relatorio_html(resultados_familias, g_d, mensagem, tabelas_originais, imagens_por_familia, fr_selecionados, fr_descricao)

        st.subheader("Resumo da Avaliação da Estrutura")
        st.markdown(mensagem)
        st.download_button(
            label="⬇️ Baixar relatório HTML",
            data=html_output,
            file_name="relatorio_gde.html",
            mime="text/html"
        )
    else:
        st.warning("Nenhuma família foi processada com sucesso.")
