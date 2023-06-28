import streamlit as st
import pandas as pd
import base64
import re
import locale

# Configuração da formatação de moeda
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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

    # Verifica as variações de nomes das colunas de código e valor
    coluna_codigo = [
        col for col in df_selecionado.columns if 'codigo' in col.lower()][0]
    coluna_valor = [
        col for col in df_selecionado.columns if 'valor' in col.lower()][0]

    # Atualiza as colunas "código" e "ch" da tabela base
    df_base['código'] = df_selecionado[coluna_codigo].apply(
        lambda x: re.sub(r'Código:', '', str(x)) if pd.notnull(x) else '')
    df_base['ch'] = df_selecionado[coluna_valor].apply(
        lambda x: format_currency(x) if pd.notnull(x) else '')

    # Cria uma cópia da tabela base com as colunas atualizadas
    df_final = df_base.copy()

    # Codifica o DataFrame tratado em CSV para download
    csv = df_final.to_csv(sep=';', quoting=1, index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="arquivo_tratado.csv">Baixar arquivo tratado</a>'

    st.markdown(href, unsafe_allow_html=True)
    st.write('Tabela tratada gerada com sucesso!')

# Função para formatar o valor da coluna "ch"


def format_currency(value):
    if pd.notnull(value):
        value = str(value)
        if value.startswith('RS '):
            value = value[3:]
        value = re.sub(r'[^0-9,.]', '', value)
        try:
            value = locale.currency(float(value), grouping=True, symbol=False)
        except ValueError:
            pass
    return value


# Interface Streamlit
st.title('Tratamento de Tabela')

# Solicita o caminho do arquivo Excel
caminho_arquivo = st.file_uploader(
    'Selecione o arquivo Excel', type=['xls', 'xlsx'])

if caminho_arquivo is not None:
    # Trata a tabela
    tratar_tabela(caminho_arquivo)
