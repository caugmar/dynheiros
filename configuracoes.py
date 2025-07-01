import yaml
import os

_CONFIG_FILE = "dinheiros.yaml"
with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
    _CONFS = yaml.safe_load(f)

data_de_emissao = _CONFS.get("data-de-emissao")

data_de_vencimento = _CONFS.get("data-de-vencimento")

mes_de_emissao = _CONFS.get("mes-de-emissao")

mes_de_vencimento_por_extenso = _CONFS.get("mes-de-vencimento-por-extenso")

data_de_vencimento_dos_recibos = _CONFS.get("data-de-vencimento-dos-recibos")

data_de_pagamento_dos_recibos = _CONFS.get("data-de-pagamento-dos-recibos")

def descricao_da_atualizacao(tipo):
    desc = _CONFS.get("descricao-da-atualizacao", {}).get(tipo)
    return desc.replace('~a', '{}')

def titulo_do_relatorio(tipo):
    titulo = _CONFS.get("titulo-do-relatorio", {}).get(tipo) 
    return titulo.replace('~a', '{}')

planilhas_para_email = _CONFS.get("planilhas-para-email")

libreoffice_python = _CONFS.get("libreoffice-python")

libreoffice_uno = _CONFS.get("libreoffice-uno")

libreoffice_csv = _CONFS.get("libreoffice-csv")

libreoffice_pdf = _CONFS.get("libreoffice-pdf")

planilha_de_dados = _CONFS.get("planilha-de-dados")

banco_de_dados = _CONFS.get("banco-de-dados")

caminho_das_planilhas = _CONFS.get("caminho-das-planilhas")

pdftk_para_planilhas = _CONFS.get("pdftk-para-planilhas")

caminho_dos_templates = _CONFS.get("caminho-dos-templates")
