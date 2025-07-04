#!/usr/bin/env python3

import argparse
import os
import shutil
import glob
from configuracoes import data_de_emissao, data_de_vencimento, libreoffice_pdf
from configuracoes import caminho_das_planilhas, pdftk_para_planilhas
from gerar_documentos import gerar_documentos
from emitir_notas import emitir_documentos
from gerar_relatorios import emitir_relatorios, emitir_recibos
from atualizar_planilhas import atualizar_todas_as_planilhas
from enviar_emails import gerar_pdfs_e_enviar_emails

def arg(parser, short, long, helpmsg):
    parser.add_argument(short, long, action="store_true", help=helpmsg)

def obter_argumentos():
    parser = argparse.ArgumentParser(
        prog="pynheiros",
        description="Ferramenta para gerenciamento de cobranças."
    )
    arg(parser, "-g", "--gerar", "Gera os documentos de cobrança.")
    arg(parser, "-e", "--emitir", "Emite os documentos de cobrança.")
    arg(parser, "-r", "--relatorios", "Emite os relatórios de cobrança.")
    arg(parser, "-b", "--recibos", "Emite os recibos de aluguel.")
    arg(parser, "-a", "--atualizar-planilhas", "Atualiza as planilhas de cobrança.")
    arg(parser, "-i", "--imprimir-planilhas", "Gera PDF das planilhas para impressão.")
    arg(parser, "-m", "--email-planilhas", "Envia planilhas por email.")
    arg(parser, "-s", "--sincronizar-planilhas", "Sincroniza planilhas com o servidor.")
    arg(parser, "-x", "--excluir", "Exclui os artefatos gerados pela cobrança mensal.")
    args = parser.parse_args()
    return args

def sincronizar_planilhas():
    print("Sincronizando planilhas com o servidor...")
    os.system("mount /media/guto/dados")
    os.system("unison -auto -batch -ui text \"Atualizar Planilhas\"")
    os.system("sync")
    os.system("umount /media/guto/dados")
    print("Sincronizadas.")

def imprimir_planilhas():
    print("Gerando PDF das planilhas para impressão...")
    os.makedirs("fichas", exist_ok=True)
    letras = [chr(i) for i in range(ord('a'), ord('z'))]
    for letra in letras:
        os.system(f"{libreoffice_pdf()} {caminho_das_planilhas()}{letra}/*.ods")
    os.system(pdftk_para_planilhas)
    print("Gerado.")

def excluir_artefatos():
    print("Excluindo artefatos gerados...")
    shutil.rmtree("compiled/", ignore_errors=True)
    shutil.rmtree("fichas/", ignore_errors=True)
    files_to_delete = ["aviso.txt", "lbm.txt", "minister.txt", "notas.txt", "notas.ps"]
    for f in files_to_delete:
        if os.path.exists(f):
            os.remove(f)
    for pattern in ["*.html", "*.pdf", "*.bak", "*~"]:
        for file in glob.glob(pattern):
            os.remove(file)
    print("Excluídos.")

def gerar_documentos_de_cobranca():
    print("Gerando documentos no banco de dados...")
    gerar_documentos(data_de_emissao, data_de_vencimento)
    print("Gerados.")

def emitir_documentos_de_cobranca():
    print("Emitindo notas fiscais em PDF...")
    emitir_documentos(data_de_emissao)
    print("Emitidas.")

def gerar_relatorios_de_cobranca():
    print("Emitindo relatórios em PDF...")
    emitir_relatorios(data_de_emissao)
    print("Emitidos.")

def gerar_recibos_de_aluguel():
    print("Emitindo recibos de aluguel em PDF...")
    emitir_recibos()
    print("Emitidos.")

def atualizar_planilhas_dos_clientes():
    print("Atualizando as planilhas dos clientes com a nova cobrança...")
    atualizar_todas_as_planilhas(data_de_emissao)
    print("Atualizadas.")

def main():
    args = obter_argumentos()
    if args.gerar: gerar_documentos_de_cobranca()
    if args.emitir: emitir_documentos_de_cobranca()
    if args.relatorios: gerar_relatorios_de_cobranca()
    if args.recibos: gerar_recibos_de_aluguel()
    if args.atualizar_planilhas: atualizar_planilhas_dos_clientes()
    if args.imprimir_planilhas: imprimir_planilhas()
    if args.email_planilhas: gerar_pdfs_e_enviar_emails()
    if args.sincronizar_planilhas: sincronizar_planilhas()
    if args.excluir: excluir_artefatos()

if __name__ == "__main__":
    main()
