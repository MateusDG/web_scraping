import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configurar o logging para o registro principal
logging.basicConfig(filename='registro.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Criar um logger separado para o relatório final
relatorio_logger = logging.getLogger('relatorio')
relatorio_logger.setLevel(logging.INFO)
relatorio_handler = logging.FileHandler('relatorio_final.log')
relatorio_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
relatorio_logger.addHandler(relatorio_handler)

# Criar uma sessão HTTP reutilizável
session = requests.Session()

# Função para extrair dimensões de uma URL
def extrair_dimensoes(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = session.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        tabela_dimensoes = soup.select_one('.especificacoes-conteiner .table-striped')

        if tabela_dimensoes:
            dados_dimensoes = {}
            for row in tabela_dimensoes.find('tbody').find_all('tr'):
                columns = row.find_all('td')
                if len(columns) == 2:
                    chave, valor = columns[0].text.strip(), columns[1].text.strip()

                    # Converter mm para cm
                    if 'mm' in valor:
                        valor = float(valor.replace('mm', '')) / 10
                    dados_dimensoes[chave] = valor

            return dados_dimensoes
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f"Erro ao extrair dimensões para URL {url}: {str(e)}")
        return None

# Função para verificar se as dimensões são iguais, considerando "cm" e "mm"
def dimensoes_sao_iguais(dimensao1, dimensao2):
    dimensao1 = str(dimensao1).replace(' ', '').lower().replace('cm', '').replace('mm', '').replace('kg', '')
    dimensao2 = str(dimensao2).replace(' ', '').lower().replace('cm', '').replace('mm', '').replace('kg', '')

    if dimensao1 == dimensao2:
        return True

    # Remover as unidades e verificar se os valores são iguais
    try:
        valor1 = float(dimensao1[:-2]) if dimensao1.endswith(('cm', 'mm')) else float(dimensao1)
        valor2 = float(dimensao2[:-2]) if dimensao2.endswith(('cm', 'mm')) else float(dimensao2)

        return valor1 == valor2
    except ValueError:
        return False

# Função para comparar dimensões
def comparar_dimensoes(nome_dimensao, dimensao_site, dimensao_planilha):
    igual = dimensoes_sao_iguais(dimensao_site, str(dimensao_planilha))
    logging.info(f"{nome_dimensao} {'igual' if igual else 'diferente'}: {dimensao_site} (Site) vs {dimensao_planilha} (Planilha)")
    return igual

# Carregar planilha
planilha = pd.read_excel('identificacao/teste.xlsx')

# ...

# Listas para armazenar resultados
iguais = []
diferentes = []
nao_comparadas = []

# Iterar sobre as linhas da planilha
for indice, linha in planilha.iterrows():
    url_produto = linha['URL do Produto']
    dimensoes_produto = extrair_dimensoes(url_produto)

    if dimensoes_produto:
        logging.info(f"Comparando dimensões para o produto na linha {indice + 2}:\n"
                     f"Site: {dimensoes_produto}\n"
                     f"Planilha: {{'Peso': {linha['Peso']}, 'Altura': {linha['Altura']}, 'Largura': {linha['Largura']}, 'Profundidade': {linha['Comprimento']}}}")

        peso_igual = comparar_dimensoes('Peso', dimensoes_produto.get('Peso', 'Não encontrado'), linha['Peso'])
        altura_igual = comparar_dimensoes('Altura', dimensoes_produto.get('Altura', 'Não encontrado'), linha['Altura'])
        largura_igual = comparar_dimensoes('Largura', dimensoes_produto.get('Largura', 'Não encontrado'), linha['Largura'])
        profundidade_igual = comparar_dimensoes('Profundidade', dimensoes_produto.get('Profundidade', 'Não encontrado'), linha['Comprimento'])

        if peso_igual and altura_igual and largura_igual and profundidade_igual:
            iguais.append(indice + 2)
            logging.info("Dimensões iguais: Peso, Altura, Largura e Profundidade")
        else:
            diferentes.append(indice + 2)
            logging.info("Dimensões diferentes: Peso, Altura, Largura ou Profundidade diferentes")

        logging.info("\n" + "-" * 30 + "\n")  # Adiciona uma linha em branco entre os registros

        print(f"Comparando dimensões para o produto na linha {indice + 2}:")
        print(f"Peso (Planilha): {linha['Peso']}, Peso (Site): {dimensoes_produto.get('Peso', 'Não encontrado')}")
        print(f"Altura (Planilha): {linha['Altura']}, Altura (Site): {dimensoes_produto.get('Altura', 'Não encontrado')}")
        print(f"Largura (Planilha): {linha['Largura']}, Largura (Site): {dimensoes_produto.get('Largura', 'Não encontrado')}")
        print(f"Profundidade (Planilha): {linha['Comprimento']}, Profundidade (Site): {dimensoes_produto.get('Profundidade', 'Não encontrado')}")
        print("------------------------------")
    else:
        nao_comparadas.append(indice + 2)
        logging.error(f"Não foi possível extrair dimensões para a URL na linha {indice + 2}")

# ...

# Gerar relatório no arquivo de log final
relatorio_logger.info("\n\n*** Relatório Final ***")
relatorio_logger.info(f"Número de comparações iguais: {len(iguais)}")
relatorio_logger.info(f"Número de comparações diferentes: {len(diferentes)}")
relatorio_logger.info(f"Número de linhas não comparadas: {len(nao_comparadas)}")

if iguais:
    relatorio_logger.info("\nLinhas com comparações iguais: " + str(iguais))

if diferentes:
    relatorio_logger.info("\nLinhas com comparações diferentes: " + str(diferentes))

if nao_comparadas:
    relatorio_logger.info("\nLinhas não comparadas: " + str(nao_comparadas))
