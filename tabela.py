import streamlit as st
import pandas as pd
import base64
import re
import locale

# Interface Streamlit
st.set_page_config(page_title='Tratador de Tabelas',
                   page_icon='img/icone.ico')

# Importa o arquivo CSS


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Chama a função para aplicar o estilo
local_css('style.css')

# código JavaScript para controlar o clique do botão de download
st.markdown(
    """
    <script>
    const downloadButton = document.getElementById('download-button');
    downloadButton.addEventListener('click', function() {
        downloadButton.classList.add('btn-clicked');
    });
    </script>
    """,
    unsafe_allow_html=True
)

# Configuração da formatação de moeda
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Caminho do arquivo CSV da tabela base
caminho_tabela_base = 'teste/base.csv'

# Carrega a tabela base em um DataFrame
df_base = pd.read_csv(caminho_tabela_base, sep=';', quoting=1)

# Função para tratar a tabela


def tratar_tabela(caminho_arquivo):

    if caminho_arquivo is None:
        st.warning('Nenhum arquivo selecionado.')
        return

    # Carrega o arquivo Excel em um DataFrame
    xls = pd.ExcelFile(caminho_arquivo)

    # Lista todas as abas da planilha
    abas = xls.sheet_names

    # Cria um DataFrame vazio para armazenar os dados tratados
    df_final = pd.DataFrame()

    for aba in abas:
        # Lê a aba atual em um DataFrame
        df = pd.read_excel(caminho_arquivo, sheet_name=aba)

        # Verifica se o DataFrame está vazio
        if df.empty:
            st.warning(f'A aba "{aba}" do arquivo selecionado está vazia.')
            continue

        # Seleciona as colunas desejadas
        colunas = list(df.columns)
        colunas_selecionadas = st.multiselect(
            f'Selecione as colunas desejadas para a aba "{aba}"', colunas, format_func=lambda x: x, default=[])

        # Verifica se alguma coluna foi selecionada
        if len(colunas_selecionadas) == 0:
            st.warning(f'Nenhuma coluna selecionada para a aba "{aba}".')
            continue

        # Verifica as variações de nomes das colunas de código e valor
        coluna_codigo = None
        coluna_valor = None
        for col in colunas_selecionadas:
            if 'codigo' in col.lower():
                coluna_codigo = col
            elif 'valor' in col.lower():
                coluna_valor = col

        # Verifica se as colunas de código e valor foram encontradas
        if coluna_codigo is None or coluna_valor is None:
            st.warning(
                f'Colunas de código ou valor não encontradas para a aba "{aba}".')
            continue

        # Filtra as linhas que não estão vazias nas colunas selecionadas
        df = df.dropna(subset=[coluna_codigo, coluna_valor])

        # Atualiza as colunas "código" e "ch" da tabela base
        df_base['código'] = df[coluna_codigo].apply(
            lambda x: re.sub(r'\D', '', str(x)) if pd.notnull(x) else '')
        df_base['ch'] = df[coluna_valor].apply(
            lambda x: format_currency(x) if pd.notnull(x) else '')

        # Cria uma cópia da tabela base com as colunas atualizadas
        df_tratado = df_base.copy()

        # Adiciona os dados tratados à tabela final
        df_final = pd.concat([df_final, df_tratado])

    # Verifica se a tabela final está vazia
    if df_final.empty:
        st.warning('A tabela tratada está vazia.')
        return

    # Codifica o DataFrame tratado em CSV para download
    csv = df_final.to_csv(sep=';', quoting=1, index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="arquivo_tratado.csv" class="btn-download clicked">Baixar Tabela Tratada</a>'

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


st.image('img/tabela.png', width=250)

# Solicita o caminho do arquivo Excel
caminho_arquivo = st.file_uploader(
    'Selecione o arquivo Excel', type=['xls', 'xlsx'])

# Trata a tabela
tratar_tabela(caminho_arquivo)
