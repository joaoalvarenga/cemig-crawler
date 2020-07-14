from multiprocessing import Pool
from selenium import webdriver

import argparse
import pickle
import time
import os


def get_instalations(browser):
    """
    Downloads instalations
    :param browser:
    :return:
    """
    output = []
    for el in browser.find_elements_by_css_selector(".selInstalacao"):
        output.append(
            {
                'contato': el.get_attribute("data-contrato"),
                'contacontato': el.get_attribute("data-contacontrato"),
                'cpf': el.get_attribute("data-cpf"),
                'pn': el.get_attribute("data-pn"),
                'cliente': el.get_attribute("data-cliente"),
                'endereco': el.get_attribute("data-endereco"),
                'in': el.get_attribute("data-in"),
            }
        )
    pickle.dump(output, open('instalacoes.pkl', 'wb'))


def run(acc):
    path = f"cemig/{acc['contato']}_{acc['pn']}"
    try:
        os.mkdir(path)
    except:
        pass
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
    with open(COOKIES_PATH, 'rb') as f:
        cookies = pickle.load(f)

    browser.get('https://atende.cemig.com.br')
    browser.delete_all_cookies()
    for c in cookies:
        browser.add_cookie(c)

    browser.get('https://atende.cemig.com.br/AssociarInstalacao/Index/')
    time.sleep(1)
    browser.find_element_by_css_selector("#instalacaoSelecionada").click()
    browser.find_element_by_xpath(f"//a[@data-contrato=\"{acc['contato']}\"][@data-pn=\"{acc['pn']}\"]").click()
    browser.delete_all_cookies()
    time.sleep(30)
    browser.get("https://atende.cemig.com.br/SegundaVia")
    time.sleep(20)
    download_link = get_download_link(browser, acc)
    if download_link is None:
        browser.close()
        return

    download_link.click()
    time.sleep(30)
    browser.close()


def get_download_link(browser, acc):
    try:
        return browser.find_element_by_xpath('//*[@id="tblGrid"]/tbody/tr[1]/td[5]/div/a')
    except:
        print(f"Sem conta {acc['contato']}_{acc['pn']} {acc['cpf']} {acc['endereco']}")
        return None


def main():
    global CHROMEDRIVER_PATH, COOKIES_PATH

    parser = argparse.ArgumentParser()
    parser.add_argument("--chromedriver", help="Chromdriver absolute path")
    parser.add_argument("--cookies", help="Cemig cookies after login")
    args = parser.parse_args()
    CHROMEDRIVER_PATH = args.chromedriver
    COOKIES_PATH = args.cookies

    accounts = pickle.load(open("instalacoes.pkl", 'rb'))
    with Pool() as p:
        p.map(run, accounts)


if __name__ == '__main__':
    main()
