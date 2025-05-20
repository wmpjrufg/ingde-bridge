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
        <p><a href="https://orcid.org/0000-0003-0215-8701" target="_blank">Prof. Humberto Salazar Amorim Varum</a></p>
        <p><a href="https://orcid.org/0000-0003-0964-880X" target="_blank">Prof. Wellington Andrade da Silva</a></p>
        <p><a href="" target="_blank">Eng. Marcus Vinicius Nascimento</a></p>
        <p><a href="" target="_blank">Eng. Pedro Henrique Gomes</a></p>
        <p><a href="http://orcid.org/0009-0008-4084-2137" target="_blank">Discente Luiz Henrique Ferreira Rezio</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
st.write("")

# Como usar
st.subheader("Tutorial")
st.markdown(rf"""
<p align="justify">
Para gerar o relatório de inspeção automatizado via metodologia GDE/UnB, baixe o conjunto de planilhas e preencha os dados da inspeção no modelo.
</p>
            
<table>
    <thead>
        <tr>
            <th>Descrição</th>
            <th>Link para <i>download</i></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Bloco de fundação</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/bloco_fundacao_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Cortina e ala</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/cortina_ala_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Fundação</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/fundacao_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Guarda-corpo e barreiras</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/guarda_corpo_barreira_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Junta de dilatação</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/junta_dilatacao_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Laje</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/laje_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Pilar</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/pilar_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Pista de rolamento</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/pista_rolamento_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
        <tr>
            <td>Viga</td>
            <td><a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/viga_modelo.xlsx" target="_blank"><i>download</i></a></td>
        </tr>
    </tbody>
</table>

<p align="justify">
Após o preenchimento da inspeção com os seus dados, crie um arquivo <code>.zip</code> que contenha os seguintes documentos:
</p>

<pre><code>dados_inspecao.zip
├── fotos
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
└── planilha_inspecao.xlsx</code></pre>
            
<ul>
    <li><p align="justify"><strong>fotos</strong>: Pasta que contenha as imagens em formato <code>.png</code>, <code>.jpg</code> ou <code>.jpeg</code> da inspeção realizada.</p></li>
    <li><p align="justify"><strong>planilha_inspecao.xlsx</strong>: Planilha modelo preenchida com os dados da inspeção relativa ao elemento avaliado. O nome do arquivo não deve conter espaços ou caracteres especiais.</p></li>
</ul>
            
<p align="justify">
O usuário pode criar vários arquivos <code>.zip</code> com diferentes famílias de elementos, desde que cada arquivo <code>.zip</code> contenha a mesma estrutura para apenas uma família de elementos.
</p>
""", unsafe_allow_html=True)

st.write("")

st.subheader("Instruções de uso")
st.markdown(rf""" 
<p align="justify">
Para realizar a inspeção GDE/UnB, siga os passos abaixo:
<ol>
    <li><p align="justify">Faça o <a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/" target="_blank"><i>download</i></a> do arquivo modelo de inspeção e preencha os dados necessários. Para o correto preenchimento faça também o <a href="https://github.com/wmpjrufg/inspgde/raw/refs/heads/main/modelos/fatores_intensidade.pdf" target="_blank"><i>download</i></a> do manual de utilização do GDE/UnB para verificação dos Fatores de Intensidade (<i>F<sub>i</sub></i>) e Fatores de Ponderação (<i>F<sub>p</sub></i>).</p></li>
    <li><p align="justify">Crie uma pasta chamada "fotos" e adicione as imagens da inspeção;</p></li>
    <li><p align="justify">Compacte a pasta "fotos" e a planilha de inspeção em um arquivo <code>.zip</code> único;</p></li>
    <li><p align="justify">Repita esse processo até que todas as famílias de elementos tenham sido contempladas;</p></li>
    <li><p align="justify">Selecione o número de famílias de elementos que deseja inspecionar;</p></li>
    <li><p align="justify">Faça o upload do arquivo <code>.zip</code> e selecione o grupo familiar correspondente a cada arquivo <code>.zip</code>;</p></li>
    <li><p align="justify">Clique no botão "Calcular" para gerar o relatório;</p></li>
    <li><p align="justify">Após o processamento resultado resumido é apresentado em tela e você também poderá baixar o relatório detalhado em formato <code>.html</code>.</p></li>
</ol> 
""", unsafe_allow_html=True)

st.write("")


# Configurações do Streamlit
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
    fr = st.selectbox(f"Grupo familiar ($F_r$) da Família {i+1}:", options=list(fr_descricao.keys()),
                      format_func=lambda x: f"{x} - {fr_descricao[x]}", key=f"fr_{i}")
    uploaded_zips.append(uploaded_zip)
    fr_selecionados.append(fr)

if st.button("Calcular"):
    resultados_familias = {}
    tabelas_originais = {}
    imagens_por_familia = {}
    nomes_arquivos = []
    elementos_por_familia = {}

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
                    nome_zip = os.path.splitext(uploaded_zip.name)[0]
                    nome_planilha = os.path.splitext(os.path.basename(planilha_nome))[0]
                    nome_arquivo = f"{nome_zip}_{nome_planilha}"
                    df_ajustado, nome_elementos = adequa_dataset(df_raw)

                    resultado_familia = avalia_familia(df_ajustado, nome_arquivo, f_r=fr)
                    resultados_familias.update(resultado_familia)
                    tabelas_originais[nome_arquivo] = df_raw
                    imagens_por_familia[nome_arquivo] = fotos_base64
                    elementos_por_familia[nome_arquivo] = nome_elementos

                    nomes_arquivos.append(uploaded_zip.name)

                    st.success(f"Família {i+1} ({nome_arquivo}) processada com sucesso.")
                    st.write(f"{len(fotos_base64)} imagem(ns) carregadas.")

    if resultados_familias:
        g_d, nivel, recomendacao = avaliar_estrutura(resultados_familias)
        html_output, df_resumo_familias, df_grau_estrutura = gerar_relatorio_html(
            resultados_familias, g_d, nivel, recomendacao, tabelas_originais,
            imagens_por_familia, nomes_arquivos, fr_selecionados,
            fr_descricao, elementos_por_familia
        )

        # Salvar estado da sessão
        st.session_state["html_output"] = html_output
        st.session_state["df_resumo_familias"] = df_resumo_familias
        st.session_state["df_grau_estrutura"] = df_grau_estrutura

if "html_output" in st.session_state:
    st.subheader("Resumo dos Resultados por Família")
    st.table(st.session_state["df_resumo_familias"])

    st.subheader("Grau de Deterioração da Estrutura")
    st.table(st.session_state["df_grau_estrutura"])

    st.download_button(
        "⬇️ Baixar relatório HTML",
        st.session_state["html_output"].encode("utf-8"),
        file_name="relatorio_gde.html",
        mime="text/html"
    )
