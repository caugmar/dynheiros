import csv
import os
import subprocess
from banco_de_dados import Empresa, Lancamento
from configuracoes import libreoffice_csv, planilha_de_dados

def salvar_para_csv():
    comando = f"{libreoffice_csv} {planilha_de_dados}"
    try:
        subprocess.run(comando, shell=True, capture_output=True, text=True, check=True)
        print("Arquivos CSV gerados com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar CSVs: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Erro: 'libreoffice' não encontrado. Certifique-se de que está instalado e no seu PATH.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao salvar para CSV: {e}")

def excluir_csv():
    arquivos_para_excluir = ["dados-Empresas.csv", "dados-Lançamentos.csv"]
    for arquivo in arquivos_para_excluir:
        if os.path.exists(arquivo):
            os.remove(arquivo)
            print(f"Arquivo {arquivo} excluído.")
        else:
            print(f"Arquivo {arquivo} não encontrado para exclusão.")

def como_numero(valor):
    return float(valor.replace(",", "."))

def ler_csv(arquivo, transformador):
    if not os.path.exists(arquivo):
        print(f"Erro: Arquivo CSV não encontrado: {arquivo}")
        return []
    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)  # Pula o cabeçalho
        return [transformador(row) for row in reader]

def carregar_dados():
    global empresas, lancamentos, tipos
    salvar_para_csv()
    empresas = ler_csv("dados-Empresas.csv", lambda reg: Empresa(*reg))
    lancamentos = ler_csv("dados-Lançamentos.csv", 
                          lambda reg: Lancamento(reg[0], reg[1], como_numero(reg[2]), 
                                                 reg[3], como_numero(reg[4])))
    tipos = sorted(list(set(lancamento.modelo for lancamento in lancamentos)))
    excluir_csv()

def obter_empresa_por_codigo(codigo):
    for emp in empresas:
        if emp.codigo == codigo:
            return emp
    return None

def obter_empresa_por_nome(nome):
    for emp in empresas:
        if emp.nome == nome:
            return emp
    return None

def obter_lancamentos_por_tipo_e_codigo(tipo, codigo):
    return [
        lanc for lanc in lancamentos
        if lanc.modelo == tipo and lanc.nome == codigo
    ]

def empresas_ativas(tipo):
    return list(set(lancamento.nome for lancamento in lancamentos 
                    if lancamento.modelo == tipo))
