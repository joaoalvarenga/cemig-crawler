import pickle
import subprocess
import os
import numpy as np
import re
import pandas as pd


def get_pdf_filename(dir):
    files = [fn for fn in os.listdir(dir) if fn.endswith(".pdf")]
    if len(files) > 0:
        return files[0]


def get_modalidade(i, lines):
    data = '###'.join(lines[i:]).split('######')[1:4]
    return {
        'Classe': data[0].replace('###', ' '),
        'Subclasse': data[1].replace('###', ' '),
        'Modalidade Tarifária': data[2].replace('###', ' ')
    }


def get_consumo(i, lines):
    consumo = '###'.join(lines[i:]).split('######')[1].split('###')
    if consumo[0] == 'MÉDIA kWh/Dia':
        consumo = '###'.join(lines[i:]).split('######')[2].split('###')

    if consumo[0] == 'Dias':
        consumo = '###'.join(lines[i:]).split('######')[4].split('###')
    consumo = [float(c.replace('.', '').replace(',', '.')) for c in consumo]
    return np.mean(consumo)


PATTERN_TOTAL = re.compile(r'R\$\d+')

accounts = pickle.load(open('instalacoes.pkl', 'rb'))

output = []
for acc in accounts:
    path = f"cemig/{acc['contato']}_{acc['pn']}/"
    pdf_filename = get_pdf_filename(path)
    if pdf_filename is None:
        print(f"Empty {acc}")
        continue
    subprocess.call(["pdftotext", f"{path}/{pdf_filename}", f"{path}/conta.txt"])
    with open(f'{path}/conta.txt', 'r') as f:
        lines = [l.strip() for l in f]

    info = {
        'Endereço': acc['endereco'],
        'CNPJ': acc['cpf'],
        'Cliente': acc['cliente'],
        'Instalação': acc['in'],
        'Energia Injetada': 'Não',
        'PN': acc['pn'],
        'Contrato': acc['contato'],
        'En comp. kWh ISENTA': 'Não',
    }
    for i, l in enumerate(lines):
        if PATTERN_TOTAL.match(l.strip()):
            info['Total a pagar'] = float(l.strip().replace('R$', '').replace('.', '').replace(',', '.'))
        if l == 'Modalidade Tarifária':
            info = {**info, **get_modalidade(i, lines)}
        if l == 'CONSUMO kWh':
            info = {**info, 'Consumo Médio': get_consumo(i, lines)}
        if l.lower().find('energia injetada') > -1:
            info['Energia Injetada'] = 'Sim'
        if l.strip().find('En comp. kWh ISENTA') > -1:
            info['En comp. kWh ISENTA'] = 'Sim'
    output.append(info)

df = pd.DataFrame.from_dict(output)
df.to_excel('contas.xlsx')
