import subprocess
import os
import time
import socket
from configuracoes import (libreoffice_python, libreoffice_uno,
                           caminho_das_planilhas, descricao_da_atualizacao,
                           mes_de_emissao, data_de_emissao)
from banco_de_dados import (obter_documentos_por_data,
                            obter_itens_de_cobranca_por_id_do_documento)
import carregar_dados

def _inserir_linha(caminho, data, descricao, valor):
    subprocess.run([libreoffice_python, "inserir-linha.py",
                    caminho, data, descricao, str(valor)])

def _gerar_descricao(doc, mes):
    tipo = doc.modelo
    numero = doc.numero_da_nota
    tmpl_descricao = descricao_da_atualizacao(tipo)
    if tipo == "AVISO":
        return tmpl_descricao.format(mes)
    else:
        return tmpl_descricao.format(numero, mes)

def _atualizar(caminho, data, descricao, valor):
    if os.path.exists(caminho):
        _inserir_linha(caminho, data, descricao, valor)

def _dados_da_planilha(doc):
    empresa = carregar_dados.obter_empresa_por_nome(doc.nome)
    planilha = empresa.planilha
    inicial = planilha[0].lower()
    caminho_parcial = os.path.join(caminho_das_planilhas, inicial, planilha)
    caminho_absoluto = os.path.abspath(caminho_parcial)
    return planilha, caminho_absoluto

def _dados_a_inserir(doc):
    descricao = _gerar_descricao(doc, mes_de_emissao)
    itens = obter_itens_de_cobranca_por_id_do_documento(doc.id)
    valor = sum(item.valor for item in itens)
    return descricao, valor

def porta_aberta(host, port, timeout=1):
    try:
        with socket.create_connection((host, port), timeout) as sock:
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def aguardar_porta(processo):
    while not porta_aberta('127.0.0.1', '2002'):
        print(f"Aguardando LibreOffice...")
        time.sleep(0.5)

def atualizar_todas_as_planilhas(data_de_emissao):
    print("Iniciando processo do LibreOffice UNO...")
    carregar_dados.carregar_dados()
    processo = subprocess.Popen(['libreoffice', '--headless', '--nologo', '--calc', 
                                 '--accept=socket,host=localhost,port=2002;urp;'])
    aguardar_porta(processo)
    documentos = obter_documentos_por_data(data_de_emissao)
    for doc in documentos:
        planilha, caminho = _dados_da_planilha(doc)
        descricao, valor = _dados_a_inserir(doc)
        print(f"Atualizando {planilha} - {caminho}")
        _atualizar(caminho, data_de_emissao, descricao, valor)
    print("Encerrando LibreOffice...")
    subprocess.run([libreoffice_python, 'encerrar-libreoffice.py'])

def demo():
    atualizar_todas_as_planilhas(data_de_emissao)
