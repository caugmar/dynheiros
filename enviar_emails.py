import os
import subprocess
import shutil
import yagmail

from configuracoes import (
    planilhas_para_email, caminho_das_planilhas,
    libreoffice_pdf, mes_de_emissao,)

def _caminho_completo(arquivo):
    diretorio = caminho_das_planilhas
    first_char = arquivo.lower()[0]
    return os.path.join(diretorio, first_char, arquivo)

def _gerar_pdf_da_planilha(caminho):
    print(f"Gerando PDF para {caminho}...")
    subprocess.run(f'{libreoffice_pdf} "{caminho}"', shell=True, check=True)

def gerar_pdfs():
    envios = planilhas_para_email
    planilhas = [e["planilha"] for e in envios]
    caminhos_completos = [_caminho_completo(p) for p in planilhas]
    for caminho in caminhos_completos:
        _gerar_pdf_da_planilha(caminho)

def _obter_arquivo_pdf(planilha):
    return os.path.join("fichas", planilha.replace(".ods", ".pdf"))

def _planilha_para_pdf(alvo):
    new_alvo = alvo.copy()
    new_alvo["planilha"] = _obter_arquivo_pdf(alvo["planilha"])
    return new_alvo

def _enviar_email_com_anexo(email, mes_de_emissao_val, anexo):
    titulo = 'Ficha de Situação - Escritório Minister - ' + mes_de_emissao_val
    contents = """
    <p>Segue anexa a planilha com sua situação atual.<br/>
    Atenciosamente,</p>
    <p>Minister Serviços Contábeis Ltda.</p>
    """
    try:
        yag = yagmail.SMTP('escritoriominister@gmail.com', 'ryzmfzsnppmgkpmx')
        yag.useralias = "Minister Serviços Contábeis Ltda."
        yag.send(to=email, subject=titulo, contents=contents, attachments=anexo)
        print(f"Email enviado com sucesso para {email} com anexo {anexo}")
    except Exception as e:
        print(f"Falha ao enviar email para {email}. Erro: {e}")

def _enviar_email(alvo):
    email = alvo["email"]
    planilha = alvo["planilha"]
    _enviar_email_com_anexo(email, mes_de_emissao, planilha)

def enviar_emails():
    alvos = [_planilha_para_pdf(e) for e in planilhas_para_email]
    for alvo in alvos:
        _enviar_email(alvo)

def gerar_pdfs_e_enviar_emails():
    try:
        if os.path.exists("fichas/"):
            shutil.rmtree("fichas/")
        os.makedirs("fichas/", exist_ok=True)
        print("Gerando os PDFs...")
        gerar_pdfs()
        print("Enviando os e-mails...")
        enviar_emails()
        print("Feito.")
    except Exception as e:
        print(f"An error occurred: {e}")
