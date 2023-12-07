import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configurar o logging
logging.basicConfig(filename='registro.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para extrair dimensões de uma URL
def extrair_dimensoes(driver, url):
    try:
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.especificacoes-conteiner .table-striped')))
        
        # Desativar o carregamento de imagens para acelerar a execução
        driver.execute_script("var items = document.querySelectorAll('img'); for (var i = 0; i < items.length; i++) { items[i].style.display = 'none'; }")

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

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

# Carregar planilha
planilha = pd.read_excel('identificacao/teste.xlsx')

# Criar uma pool de drivers
driver_pool = [webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--headless')) for _ in range(5)]  # Use o Chrome como exemplo

# Iterar sobre as linhas da planilha
for indice, linha in planilha.iterrows():
    url_produto = linha['URL do Produto']
    dimensoes_produto = extrair_dimensoes(driver_pool[indice % len(driver_pool)], url_produto)

    if dimensoes_produto:
        logging.info(f"Comparando dimensões para o produto na linha {indice + 2}:\n"
                     f"Site: {dimensoes_produto}\n"
                     f"Planilha: {{'Peso': {linha['Peso']}, 'Altura': {linha['Altura']}, 'Largura': {linha['Largura']}, 'Profundidade': {linha['Comprimento']}}}")

        peso_igual = dimensoes_produto.get('Peso', 'Não encontrado') == str(linha['Peso'])
        altura_igual = dimensoes_produto.get('Altura', 'Não encontrado') == str(linha['Altura'])
        largura_igual = dimensoes_produto.get('Largura', 'Não encontrado') == str(linha['Largura'])
        profundidade_igual = dimensoes_produto.get('Profundidade', 'Não encontrado') == str(linha['Comprimento'])

        if peso_igual and altura_igual and largura_igual and profundidade_igual:
            logging.info("Dimensões iguais: Peso, Altura, Largura e Profundidade")
        else:
            logging.info("Dimensões diferentes: Peso, Altura, Largura ou Profundidade diferentes")

        print(f"Comparando dimensões para o produto na linha {indice + 2}:")
        print(f"Peso (Planilha): {linha['Peso']}, Peso (Site): {dimensoes_produto.get('Peso', 'Não encontrado')}")
        print(f"Altura (Planilha): {linha['Altura']}, Altura (Site): {dimensoes_produto.get('Altura', 'Não encontrado')}")
        print(f"Largura (Planilha): {linha['Largura']}, Largura (Site): {dimensoes_produto.get('Largura', 'Não encontrado')}")
        print(f"Profundidade (Planilha): {linha['Comprimento']}, Profundidade (Site): {dimensoes_produto.get('Profundidade', 'Não encontrado')}")
        print("------------------------------")

# Fechar os drivers ao final
for driver in driver_pool:
    driver.quit()
