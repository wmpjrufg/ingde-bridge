import sys
import os
import unittest
import pandas as pd
import numpy as np
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gde_unb import adequa_dataset, avalia_elemento, avalia_familia, avaliar_estrutura, image_to_base64, gerar_relatorio_html


class TestGDE(unittest.TestCase):

    def test_adequa_dataset(self):
        columns = pd.MultiIndex.from_tuples([
            ('Danos', ''),
            ('Pilar P01', 'Fi'), ('Pilar P01', 'Fp'),
            ('Pilar P02', 'Fi'), ('Pilar P02', 'Fp'),
            ('Pilar P03', 'Fi'), ('Pilar P03', 'Fp'),
            ('Pilar P04', 'Fi'), ('Pilar P04', 'Fp'),
        ])
        data = [
            ["Desagregação", np.nan, np.nan, np.nan, np.nan, 1.0, 3.0, 1.0, 3.0],
            ["Falha de Concretagem", 1.0, 3.0, 1.0, 3.0, np.nan, np.nan, np.nan, np.nan],
        ]
        df = pd.DataFrame(data, columns=columns)

        df_ajustado, nome_elementos = adequa_dataset(df.copy())

        self.assertIsInstance(df_ajustado, pd.DataFrame)
        self.assertIsInstance(nome_elementos, list)
        self.assertSetEqual(set(nome_elementos), {'Pilar P01', 'Pilar P02', 'Pilar P03', 'Pilar P04'})
        self.assertIn('Fi - Pilar P01', df_ajustado.columns)
        self.assertIn('Fp - Pilar P04', df_ajustado.columns)
        self.assertIn('Danos', df_ajustado.columns)

    def test_avalia_elemento(self):
        columns = pd.MultiIndex.from_tuples([
            ('Danos', ''),
            ('Pilar P01', 'Fi'), ('Pilar P01', 'Fp'),
            ('Pilar P02', 'Fi'), ('Pilar P02', 'Fp'),
            ('Pilar P03', 'Fi'), ('Pilar P03', 'Fp'),
            ('Pilar P04', 'Fi'), ('Pilar P04', 'Fp'),
        ])
        data = [
            ["Desagregação", np.nan, np.nan, np.nan, np.nan, 1.0, 3.0, 1.0, 3.0],
            ["Falha de Concretagem", 1.0, 3.0, 1.0, 3.0, np.nan, np.nan, np.nan, np.nan],
        ]
        df = pd.DataFrame(data, columns=columns)
        df_ajustado, _ = adequa_dataset(df.copy())
        resultados = avalia_elemento(df_ajustado)

        self.assertSetEqual(set(resultados.keys()), {'Pilar P01', 'Pilar P02', 'Pilar P03', 'Pilar P04'})

        for nome_elemento, valores in resultados.items():
            self.assertIsInstance(valores, dict)
            self.assertAlmostEqual(valores['sum_d'], 2.4, places=2)
            self.assertAlmostEqual(valores['d_max'], 2.4, places=2)
            self.assertAlmostEqual(valores['g_de'], 2.4, places=2)
            self.assertEqual(valores['sum_d'], valores['d_max'])

    def test_avalia_familia(self):
        columns = pd.MultiIndex.from_tuples([
            ('Danos', ''),
            ('Pilar P01', 'Fi'), ('Pilar P01', 'Fp'),
            ('Pilar P02', 'Fi'), ('Pilar P02', 'Fp'),
            ('Pilar P03', 'Fi'), ('Pilar P03', 'Fp'),
            ('Pilar P04', 'Fi'), ('Pilar P04', 'Fp'),
        ])
        data = [
            ["Desagregação", np.nan, np.nan, np.nan, np.nan, 1.0, 3.0, 1.0, 3.0],
            ["Falha de Concretagem", 1.0, 3.0, 1.0, 3.0, np.nan, np.nan, np.nan, np.nan],
        ]
        df = pd.DataFrame(data, columns=columns)
        df_ajustado, _ = adequa_dataset(df.copy())
        resultado = avalia_familia(df_ajustado, nome_arquivo='estrutura_teste', f_r=5.0)

        self.assertIsInstance(resultado, dict)
        familia_result = resultado['estrutura_teste']
        self.assertIn('gde_max', familia_result)
        self.assertIn('g_df', familia_result)
        self.assertIn('f_r', familia_result)
        self.assertIn('f_r × g_df', familia_result)
        self.assertIn('resultados_elemento', familia_result)

        self.assertAlmostEqual(familia_result['gde_max'], 2.4, places=2)
        self.assertAlmostEqual(familia_result['g_df'], 3.2, places=1)
        self.assertEqual(familia_result['f_r'], 5.0)
        self.assertAlmostEqual(familia_result['f_r × g_df'], 16.0, delta=0.2)

        for valores in familia_result['resultados_elemento'].values():
            self.assertAlmostEqual(valores['g_de'], 2.4, places=2)

    def test_avaliar_estrutura(self):
        resultados_familias = {
            'estrutura_teste': {
                'g_df': 3.2,
                'f_r': 5.0
            }
        }

        g_d, nivel, recomendacao = avaliar_estrutura(resultados_familias)

        self.assertIsInstance(g_d, float)
        self.assertAlmostEqual(g_d, 3.2, places=2)
        self.assertEqual(nivel, "Baixo")
        self.assertIn("manutenção preventiva", recomendacao.lower())

    def test_image_to_base64_with_bytes(self):
        jpeg_header = b'\xff\xd8\xff\xe0'
        encoded = image_to_base64(jpeg_header)
        self.assertIsInstance(encoded, str)
        self.assertTrue(len(encoded) > 0)

    def test_gerar_relatorio_html(self):
        resultados_familias = {
            "Pilares": {
                "f_r": 1.0,
                "g_df": 10.0,
                "f_r × g_df": 10.0,
                "resultados_elemento": {
                    "P01": {"sum_d": 5.0, "d_max": 3.0, "g_de": 4.0},
                    "P02": {"sum_d": 6.0, "d_max": 4.0, "g_de": 6.0}
                }
            }
        }

        tabelas_originais = {
            "Pilares": pd.DataFrame({
                "Elemento": ["P01", "P02"],
                "Dano": [2, 3]
            })
        }

        imagens_por_familia = {
            "Pilares": [("foto1.jpg", "base64string1"), ("foto2.jpg", "base64string2")]
        }

        nomes_arquivos = ["relatorio1.xlsx"]
        fr_lista = [1]
        fr_descricao = {1: "Importância normal"}
        elementos_por_familia = {"Pilares": ["P01", "P02"]}

        html, df_resumo, df_total = gerar_relatorio_html(
            resultados_familias=resultados_familias,
            g_d=3.2,
            nivel="Moderado",
            recomendacao="Monitorar periodicamente.",
            tabelas_originais=tabelas_originais,
            imagens_por_familia=imagens_por_familia,
            nomes_arquivos=nomes_arquivos,
            fr_lista=fr_lista,
            fr_descricao=fr_descricao,
            elementos_por_familia=elementos_por_familia
        )

        self.assertIsInstance(html, str)
        self.assertIn("<html", html.lower())
        self.assertIn("Pilares", html)
        self.assertIn("relatorio1.xlsx", html)
        self.assertIn("Monitorar", html)
        self.assertFalse(df_resumo.empty)
        self.assertFalse(df_total.empty)



if __name__ == '__main__':
    unittest.main()
