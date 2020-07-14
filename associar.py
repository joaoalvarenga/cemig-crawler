from selenium import webdriver
import pickle
import time
import argparse
import pandas as pd


def load_browser(chrome_driver_path, login_cookies_path):
    browser = webdriver.Chrome(executable_path=chrome_driver_path)
    with open(login_cookies_path, 'rb') as f:
        cookies = pickle.load(f)
    browser.get('https://atende.cemig.com.br')
    browser.delete_all_cookies()
    for c in cookies:
        browser.add_cookie(c)
    browser.get('https://atende.cemig.com.br/AssociarInstalacao/Index/')
    return browser


CNPJ_XPATH = '#CPFCNPJ'
CLIENTE_XPATH = '#NumeroCliente'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromedriver", help="Chromdriver absolute path")
    parser.add_argument("--cookies", help="Cemig cookies after login")
    parser.add_argument("--accounts", help="Accounts sheets")
    args = parser.parse_args()
    browser = load_browser(args.chromedriver, args.cookies)
    df = pd.read_excel(args.accounts)
    tab_idx = 1
    for i, r in df.iterrows():
        cnpj = r['CNPJ']
        cliente = r['Cliente']
        print(f'{cnpj} {cliente}')
        cnpj_input = browser.find_element_by_css_selector(CNPJ_XPATH)
        cnpj_input.send_keys(cnpj)

        cliente_input = browser.find_element_by_css_selector(CLIENTE_XPATH)
        cliente_input.send_keys(cliente)
        browser.execute_script("window.open('https://atende.cemig.com.br/AssociarInstalacao/Index/','_blank');")
        browser.switch_to.window(browser.window_handles[tab_idx])
        tab_idx += 1
        time.sleep(1)
