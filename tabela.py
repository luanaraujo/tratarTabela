import streamlit as st
import pandas as pd

# Caminho do arquivo CSV da tabela base
caminho_tabela_base = 'teste/base.csv'

# Carrega a tabela base em um DataFrame
df_base = pd.read_csv(caminho_tabela_base, sep=';', quoting=1)

# Função para selecionar as colunas desejadas


def selecionar_colunas(df):
    colunas_selecionadas = st.multiselect(
        'Selecione as colunas desejadas', list(df.columns))
    return colunas_selecionadas

# Função para tratar a tabela


def tratar_tabela(caminho_arquivo):
    # Carrega o arquivo Excel em um DataFrame
    df = pd.read_excel(caminho_arquivo)

    # Seleciona as colunas desejadas
    colunas_selecionadas = selecionar_colunas(df)
    df_selecionado = df[colunas_selecionadas]

    # Mescla com a tabela base
    df_final = pd.concat([df_base, df_selecionado], axis=1)

    # Solicita o caminho para salvar o arquivo tratado
    caminho_salvar = st.text_input(
        'Digite o caminho para salvar o arquivo tratado', value='arquivo_tratado.csv')

    # Salva o DataFrame tratado como um arquivo CSV
    df_final.to_csv(caminho_salvar, sep=';', quoting=1, index=False)

    st.write('Tabela tratada e salva com sucesso!')


# Interface Streamlit
st.title('Tratamento de Tabela')

# Solicita o caminho do arquivo Excel
caminho_arquivo = st.file_uploader(
    'Selecione o arquivo Excel', type=['xls', 'xlsx'])

if caminho_arquivo is not None:
    # Trata a tabela
    tratar_tabela(caminho_arquivo)
