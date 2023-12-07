import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configurar o logging
logging.basicConfig(filename='registro.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para extrair dimensões de uma URL
def extrair_dimensoes(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lança uma exceção para códigos de status HTTP diferentes de 2xx

        soup = BeautifulSoup(response.content, 'html.parser')

        tabela_dimensoes = soup.select_one('.especificacoes-conteiner .table-striped')

        if tabela_dimensoes:
            dados_dimensoes = {}
            for row in tabela_dimensoes.find('tbody').find_all('tr'):
                columns = row.find_all('td')
                if len(columns) == 2:
                    chave, valor = columns[0].text.strip(), columns[1].text.strip()
                    dados_dimensoes[chave] = valor

            return dados_dimensoes
    except Exception as e:
        logging.error(f"Erro ao extrair dimensões para URL {url}: {str(e)}")
        return None

# Função para verificar se as dimensões são iguais, considerando "cm" e "mm"
def dimensoes_sao_iguais(dimensao1, dimensao2):
    dimensao1 = dimensao1.replace(' ', '').lower()
    dimensao2 = dimensao2.replace(' ', '').lower()

    if dimensao1 == dimensao2:
        return True

    # Remover as unidades e verificar se os valores são iguais
    try:
        valor1 = float(dimensao1[:-2])  # Remove as duas últimas letras ("cm" ou "mm") e converte para float
        valor2 = float(dimensao2[:-2])

        return valor1 == valor2
    except ValueError:
        return False

# Carregar planilha
planilha = pd.read_excel('identificacao/teste.xlsx')

# Iterar sobre as linhas da planilha
for indice, linha in planilha.iterrows():
    url_produto = linha['URL do Produto']
    dimensoes_produto = extrair_dimensoes(url_produto)

    if dimensoes_produto:
        logging.info(f"Comparando dimensões para o produto na linha {indice + 2}:\n"
                     f"Site: {dimensoes_produto}\n"
                     f"Planilha: {{'Peso': {linha['Peso']}, 'Altura': {linha['Altura']}, 'Largura': {linha['Largura']}, 'Profundidade': {linha['Comprimento']}}}")

        peso_igual = dimensoes_sao_iguais(dimensoes_produto.get('Peso', 'Não encontrado'), str(linha['Peso']))
        altura_igual = dimensoes_sao_iguais(dimensoes_produto.get('Altura', 'Não encontrado'), str(linha['Altura']))
        largura_igual = dimensoes_sao_iguais(dimensoes_produto.get('Largura', 'Não encontrado'), str(linha['Largura']))
        profundidade_igual = dimensoes_sao_iguais(dimensoes_produto.get('Profundidade', 'Não encontrado'), str(linha['Comprimento']))

        if peso_igual and altura_igual and largura_igual and profundidade_igual:
            logging.info("Dimensões iguais: Peso, Altura, Largura e Profundidade")
        else:
            logging.info("Dimensões diferentes: Peso, Altura, Largura ou Profundidade diferentes")

        logging.info("\n" + "-" * 30 + "\n")  # Adiciona uma linha em branco entre os registros

        print(f"Comparando dimensões para o produto na linha {indice + 2}:")
        print(f"Peso (Planilha): {linha['Peso']}, Peso (Site): {dimensoes_produto.get('Peso', 'Não encontrado')}")
        print(f"Altura (Planilha): {linha['Altura']}, Altura (Site): {dimensoes_produto.get('Altura', 'Não encontrado')}")
        print(f"Largura (Planilha): {linha['Largura']}, Largura (Site): {dimensoes_produto.get('Largura', 'Não encontrado')}")
        print(f"Profundidade (Planilha): {linha['Comprimento']}, Profundidade (Site): {dimensoes_produto.get('Profundidade', 'Não encontrado')}")
        print("------------------------------")
