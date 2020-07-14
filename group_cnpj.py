import os
import pickle
import shutil

accounts = pickle.load(open('instalacoes.pkl', 'rb'))


def get_pdf_filename(dir):
    files = [fn for fn in os.listdir(dir) if fn.endswith(".pdf")]
    if len(files) > 0:
        return files[0]


output = []
for acc in accounts:
    path = f"cnpjs/{acc['cpf']}"
    try:
        os.mkdir(path)
    except:
        pass
    path_original = f"cemig/{acc['contato']}_{acc['pn']}"
    pdf_filename = get_pdf_filename(path_original)
    if pdf_filename is None:
        continue
    pdf_filepath = f"{path_original}/{pdf_filename}"
    shutil.copy(pdf_filepath, path)
