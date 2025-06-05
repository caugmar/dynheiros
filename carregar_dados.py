import csv
import os
import subprocess
from typing import List, Optional

# Requer classes definidas no arquivo "banco-de-dados.rkt" (agora assumido como "banco_de_dados.py")
# ou redefini-las aqui, conforme a solução anterior.
# Para este exemplo, vou redefinir Empresa e Lancamento para garantir que estejam disponíveis.

# --- Simulação de classes do "banco_de_dados.py" ou diretamente aqui ---
class Empresa:
    def __init__(self, codigo, nome, logradouro, numero, complemento,
                 bairro, cidade, estado, cep, cnpj, inscricao_estadual,
                 inscricao_municipal, telefone, email, planilha):
        self.codigo = codigo
        self.nome = nome
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        self.cnpj = cnpj
        self.inscricao_estadual = inscricao_estadual
        self.inscricao_municipal = inscricao_municipal
        self.telefone = telefone
        self.email = email
        self.planilha = planilha

    def __repr__(self):
        return f"Empresa(codigo='{self.codigo}', nome='{self.nome}')"

class Lancamento:
    def __init__(self, modelo, nome, qtd, descricao, valor):
        self.modelo = modelo
        self.nome = nome
        self.qtd = qtd
        self.descricao = descricao
        self.valor = valor

    def __repr__(self):
        return f"Lancamento(modelo='{self.modelo}', nome='{self.nome}', descricao='{self.descricao}')"

# --- Simulação de configurações de "configuracoes.rkt" ---
# Em um cenário real, você teria um arquivo de configuração adequado (ex: .ini, .json, .env)
# ou definiria essas variáveis em um módulo separado.
def libreoffice_csv() -> str:
    """Retorna o comando para exportar CSV via LibreOffice."""
    # Este comando assume que 'libreoffice' está no PATH e que você está em um ambiente Linux/macOS.
    # Pode precisar de ajustes para Windows ou se o LibreOffice não estiver no PATH.
    return "libreoffice --headless --convert-to csv "

def planilha_de_dados() -> str:
    """Retorna o caminho para a planilha de dados mestre."""
    # Substitua pelo caminho real da sua planilha.
    return "caminho/para/sua/planilha_dados_mestre.ods"


# --- Funções do Código Racket ---

def salvar_para_csv():
    """
    Salva os dados da planilha mestre em arquivos CSV usando LibreOffice.
    Silencia a saída do comando.
    """
    comando = f"{libreoffice_csv()} {planilha_de_dados()}"
    try:
        # A flag `capture_output=True` redireciona stdout/stderr para Pipe.
        # `text=True` decodifica como texto.
        # `check=True` levanta um CalledProcessError se o comando retornar um código de saída diferente de zero.
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
    """Exclui os arquivos CSV temporários gerados."""
    arquivos_para_excluir = ["dados-Empresas.csv", "dados-Lançamentos.csv"]
    for arquivo in arquivos_para_excluir:
        if os.path.exists(arquivo):
            os.remove(arquivo)
            print(f"Arquivo {arquivo} excluído.")
        else:
            print(f"Arquivo {arquivo} não encontrado para exclusão.")

def como_numero(valor: str) -> float:
    """Converte uma string numérica (com vírgula como separador decimal) para float."""
    return float(valor.replace(",", "."))

def ler_csv(arquivo: str, transformador) -> list:
    """
    Lê um arquivo CSV, aplica uma função transformadora a cada linha
    (exceto o cabeçalho) e retorna uma lista de objetos transformados.
    """
    if not os.path.exists(arquivo):
        print(f"Erro: Arquivo CSV não encontrado: {arquivo}")
        return []
        
    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)  # Pula o cabeçalho
        return [transformador(row) for row in reader]

# --- Execução Inicial (equivalente a (salvar-para-csv) em Racket) ---
# Em um ambiente de produção, você pode querer controlar quando esta função é chamada,
# talvez apenas uma vez na inicialização ou através de um processo agendado.
# salvar_para_csv() # Comentado para evitar erros se LibreOffice não estiver configurado.
                  # Descomente e garanta que `libreoffice_csv` e `planilha_de_dados`
                  # apontam para um LibreOffice funcional e um arquivo .ods real.

# --- Carregamento de Dados ---
# Estes serão populados após a geração dos CSVs.
# Por simplicidade e para permitir o teste sem LibreOffice,
# vou simular os dados aqui caso os CSVs não existam.

# Exemplo de como você criaria os dados se os CSVs fossem gerados:
# empresas = ler_csv("dados-Empresas.csv", lambda reg: Empresa(*reg))
# lancamentos = ler_csv("dados-Lançamentos.csv",
#                      lambda reg: Lancamento(reg[0], reg[1], como_numero(reg[2]), reg[3], como_numero(reg[4])))

# **Dados de Exemplo para Teste sem LibreOffice**
# Se você tiver a planilha e o LibreOffice configurados, pode descomentar `salvar_para_csv()`
# e as linhas acima `empresas = ...` e `lancamentos = ...`
# e remover/comentar os dados de exemplo abaixo.
empresas: List[Empresa] = [
    Empresa("ABC", "Empresa Alpha", "Rua A", "1", "", "Bairro X", "Cidade Y", "Estado Z", "12345-678", "11111111000111", "", "", "tel1", "email1", "plan1"),
    Empresa("DEF", "Empresa Beta", "Rua B", "2", "", "Bairro W", "Cidade V", "Estado U", "98765-432", "22222222000122", "", "", "tel2", "email2", "plan2")
]
lancamentos: List[Lancamento] = [
    Lancamento("NF", "ABC", 10.0, "Serviço de Consultoria", 1500.00),
    Lancamento("NF", "DEF", 5.0, "Material de Escritório", 250.50),
    Lancamento("REC", "ABC", 1.0, "Aluguel Mensal", 3000.00),
    Lancamento("NF", "ABC", 2.0, "Desenvolvimento Web", 5000.75)
]

# --- Geração de Tipos Únicos ---
# Usa um set para obter valores únicos e depois converte para lista e ordena.
tipos: List[str] = sorted(list(set(lancamento.modelo for lancamento in lancamentos)))

# --- Exclusão de CSV (equivalente a (excluir-csv) em Racket) ---
# Em um cenário real, você pode querer controlar quando esta função é chamada.
# excluir_csv() # Comentado para permitir que os dados de exemplo sejam usados.
                # Descomente se os CSVs forem gerados e você quiser limpá-los.

# --- Funções de Busca ---

def obter_empresa_por_codigo(codigo: str) -> Optional[Empresa]:
    """Retorna o objeto Empresa cujo código corresponde, ou None se não for encontrado."""
    for emp in empresas:
        if emp.codigo == codigo:
            return emp
    return None

def obter_empresa_por_nome(nome: str) -> Optional[Empresa]:
    """Retorna o objeto Empresa cujo nome corresponde, ou None se não for encontrado."""
    for emp in empresas:
        if emp.nome == nome:
            return emp
    return None

def obter_lancamentos_por_tipo_e_codigo(tipo: str, codigo: str) -> List[Lancamento]:
    """
    Retorna uma lista de objetos Lancamento que correspondem ao tipo
    e ao código da empresa (nome do lançamento).
    """
    return [
        lanc for lanc in lancamentos
        if lanc.modelo == tipo and lanc.nome == codigo
    ]

def empresas_ativas(tipo: str) -> List[str]:
    """
    Retorna uma lista de nomes de empresas que possuem lançamentos
    de um determinado tipo.
    """
    # Usa um set para garantir nomes únicos e depois converte para lista
    return list(set(lancamento.nome for lancamento in lancamentos if lancamento.modelo == tipo))

# --- Exemplo de Uso ---
if __name__ == "__main__":
    print("--- Simulação de Geração e Carregamento (assumindo dados de exemplo) ---")
    # Para testar a geração real de CSVs, descomente `salvar_para_csv()` acima
    # e configure as variáveis `libreoffice_csv()` e `planilha_de_dados()`.

    print(f"\nTipos de Lançamento disponíveis: {tipos}")

    print("\n--- Testando obter_empresa_por_codigo ---")
    emp_abc = obter_empresa_por_codigo("ABC")
    if emp_abc:
        print(f"Empresa com código 'ABC': {emp_abc.nome}")
    else:
        print("Empresa 'ABC' não encontrada.")

    print("\n--- Testando obter_empresa_por_nome ---")
    emp_beta = obter_empresa_por_nome("Empresa Beta")
    if emp_beta:
        print(f"Empresa com nome 'Empresa Beta': {emp_beta.codigo}")
    else:
        print("Empresa 'Empresa Beta' não encontrada.")

    print("\n--- Testando obter_lancamentos_por_tipo_e_codigo ---")
    lancamentos_abc_nf = obter_lancamentos_por_tipo_e_codigo("NF", "ABC")
    print(f"Lançamentos 'NF' para 'ABC' ({len(lancamentos_abc_nf)}):")
    for l in lancamentos_abc_nf:
        print(f"  - {l.descricao} (Valor: {l.valor})")

    lancamentos_def_rec = obter_lancamentos_por_tipo_e_codigo("REC", "DEF")
    print(f"Lançamentos 'REC' para 'DEF' ({len(lancamentos_def_rec)}):")
    if lancamentos_def_rec:
        for l in lancamentos_def_rec:
            print(f"  - {l.descricao} (Valor: {l.valor})")
    else:
        print("  Nenhum lançamento encontrado.")

    print("\n--- Testando empresas_ativas ---")
    ativas_nf = empresas_ativas("NF")
    print(f"Empresas ativas com tipo 'NF': {ativas_nf}")

    ativas_rec = empresas_ativas("REC")
    print(f"Empresas ativas com tipo 'REC': {ativas_rec}")

    # Para testar a exclusão de CSVs, descomente `excluir_csv()` acima.

