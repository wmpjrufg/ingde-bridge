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