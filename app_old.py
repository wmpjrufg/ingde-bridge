import pandas as pd
import streamlit as st
from math import sqrt

def gde(excel_data, fr):
    """
    Processa a planilha Excel para calcular o somatório de D para cada elemento,
    incluindo d_max, gde e gdf para cada elemento em cada planilha.

    Parâmetros:
        excel_data (pd.DataFrame): DataFrame contendo os dados da planilha Excel.
        fr (int): O fator F_r selecionado pelo usuário para o cálculo.

    Retorno:
        pd.DataFrame: DataFrame contendo os elementos, o somatório de D (sum(D)),
                      o d_max, o gde e o gdf para cada elemento, incluindo o nome da planilha.
    """

    resultados = []
    sum_fr = 0
    print('---'*50)
    # Iterar sobre os elementos e verificar se as colunas ('Fi', 'Fp') estão presentes
    for elemento in excel_data.columns.get_level_values(0).unique():
        fi_col = (elemento, 'Fi')
        fp_col = (elemento, 'Fp')

        # Verificar se as colunas ('Fi', 'Fp') existem para o elemento
        if fi_col in excel_data.columns and fp_col in excel_data.columns:
            # Calcular D para cada linha
            d_values = []
            for fi, fp in zip(excel_data[fi_col], excel_data[fp_col]):
                if fi <= 2.0:
                    d = 0.8 * fi * fp  # Equação 3.1
                elif fi >= 3.0:
                    d = (12 * fi - 28) * fp  # Equação 3.2

                d_values.append(d)

            # Somatório de D para o elemento
            d_total = sum(d_values)
            d_max = max(d_values)

            # Calcular gde para o elemento
            gde = d_max * (1 + ((d_total - d_max) / d_total))
            gde_values = [gde]
            gde_max = max(gde_values)
            gde_total = sum(gde_values)
            gdf = gde_max * sqrt(1 + gde_total - gde_max) / gde_total
            fr_gdf = fr * gdf

            sum_fr += fr
            print(f'elemento: {elemento}, sum_fr: {sum_fr}')
            print(f'gde: {gde}, gde_values: {gde_values}, gde_max: {gde_max}, gde_total: {gde_total}, gdf: {gdf}, fr: {fr}')

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

# Título da aplicação
st.title("GDA")

# Descrição do fator F_r
fr_descricao = {
    1: "Barreiras, guarda-corpo, guarda rodas, pista de rolamento",
    2: "Juntas de dilatação",
    3: "Transversinas, cortinas, alas",
    4: "Lajes, fundações, vigas secundárias, aparelhos de apoio",
    5: "Vigas e pilares principais",
}

# Upload dos arquivos Excel
uploaded_files = st.file_uploader(
    "Carregue um ou mais arquivos Excel",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# Dicionário para armazenar os fatores \( F_r \) escolhidos
fr_selecionados = {}
planilhas = {}

if uploaded_files:
    # Loop para cada arquivo carregado
    for file in uploaded_files:
        file_name = file.name
        try:
            # Carregar o arquivo Excel
            df = pd.read_excel(file, header=[0, 1])
            planilhas[file_name] = df
            
            # Selectbox para selecionar o fator \( F_r \)
            fr = st.selectbox(
                f"Selecione o grupo familiar para {file_name}",
                options=list(fr_descricao.keys()),
                format_func=lambda x: f"{fr_descricao[x]}"
            )
            fr_selecionados[file_name] = fr

        except Exception as e:
            st.error(f"Erro ao processar {file_name}: {e}")

    # Botão para aplicar o cálculo
    if st.button("Calcular"):
        resultados_finais = []  # Inicializar a lista de resultados
        sum_fr_total = 0
        sum_fr_gdf = 0

        st.title("Resultados")
        for file_name, df in planilhas.items():
            fr = fr_selecionados[file_name]
            st.subheader(f"{file_name}")

            # Aplicar a função GDA
            resultado, sum_fr, fr_gdf = gde(df, fr)
            st.table(resultado)
            sum_fr_total += sum_fr
            sum_fr_gdf += fr_gdf
            # Adicionar o resultado à lista para permitir o download
            resultados_finais.append((file_name, resultado))
        st.write('---'*50)
        st.write(f'Somatório total dos $F_r$: {sum_fr_total}')
        st.write(f'Somatório total dos $F_r * gdf$: {sum_fr_gdf}')
        st.write(f'GD: {sum_fr_gdf/sum_fr_total}')
        # Permitir download dos resultados
        with st.expander("Baixar todos os resultados"):
            for file_name, resultado in resultados_finais:
                csv = resultado.to_csv(index=False)
                st.download_button(
                    label=f"Baixar resultado de {file_name}",
                    data=csv,
                    file_name=f"resultado_{file_name}.csv",
                    mime="text/csv"
                )

