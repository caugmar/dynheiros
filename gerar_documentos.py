# Supondo que esses módulos existam e contenham as funções e classes adaptadas anteriormente.
# Por exemplo:
# from banco_de_dados import (proxima_nota, proximo_id_de_documento,
#                             novo_documento_de_cobranca, inserir_documento_de_cobranca,
#                             proximo_id_de_item_de_cobranca, novo_item_de_cobranca,
#                             inserir_item_de_cobranca,
#                             Empresa, DocCobranca, ItemCobranca, Lancamento, get_db_connection, close_db_connection)

# from carregar_dados import (empresas_ativas, obter_empresa_por_codigo,
#                             obter_lancamentos_por_tipo_e_codigo, tipos, empresas, lancamentos)

# from configuracoes import data_de_emissao, data_de_vencimento

# --- Mock das dependências para que o código seja executável de forma independente ---
# Em um projeto real, você importaria estas funções e classes dos seus respectivos arquivos.

# Mock de 'banco_de_dados.py'
class MockEmpresa:
    def __init__(self, codigo, nome, *args):
        self.codigo = codigo
        self.nome = nome
        # Adicione os outros atributos necessários para novo_documento_de_cobranca
        self.logradouro = "Rua Teste"
        self.numero = "123"
        self.complemento = ""
        self.bairro = "Centro"
        self.cidade = "Cidade Ficticia"
        self.estado = "UF"
        self.cep = "00000-000"
        self.cnpj = "00.000.000/0001-00"
        self.inscricao_estadual = ""
        self.inscricao_municipal = ""
        self.telefone = ""
        self.email = ""
        self.planilha = ""

class MockLancamento:
    def __init__(self, modelo, nome, qtd, descricao, valor):
        self.modelo = modelo
        self.nome = nome
        self.qtd = qtd
        self.descricao = descricao
        self.valor = valor

class MockDocCobranca:
    def __init__(self, id, numero_da_nota, nome, logradouro, numero, complemento,
                 bairro, cidade, estado, cep, cnpj, inscricao_estadual,
                 inscricao_municipal, telefone, email, data_de_emissao,
                 data_de_vencimento, modelo):
        self.id = id
        self.numero_da_nota = numero_da_nota
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
        self.data_de_emissao = data_de_emissao
        self.data_de_vencimento = data_de_vencimento
        self.modelo = modelo
    def __repr__(self):
        return f"DocCobranca(id={self.id}, nota={self.numero_da_nota}, empresa='{self.nome}')"

class MockItemCobranca:
    def __init__(self, id, documento, qtd, descricao, valor):
        self.id = id
        self.documento = documento
        self.qtd = qtd
        self.descricao = descricao
        self.valor = valor
    def __repr__(self):
        return f"ItemCobranca(id={self.id}, doc_id={self.documento}, desc='{self.descricao}')"

_next_doc_id = 1
_next_item_id = 1
_next_nf_number = 1
_next_rec_number = 1
_documents_db = [] # Simula o banco de dados de documentos
_items_db = []     # Simula o banco de dados de itens

def proxima_nota(tipo):
    global _next_nf_number, _next_rec_number
    if tipo == "NF":
        current_val = _next_nf_number
        _next_nf_number += 1
        return current_val
    elif tipo == "REC":
        current_val = _next_rec_number
        _next_rec_number += 1
        return current_val
    return 1 # Fallback

def proximo_id_de_documento():
    global _next_doc_id
    current_id = _next_doc_id
    _next_doc_id += 1
    return current_id

def proximo_id_de_item_de_cobranca():
    global _next_item_id
    current_id = _next_item_id
    _next_item_id += 1
    return current_id

def novo_documento_de_cobranca(novo_id, numero_da_nota, empresa,
                               data_de_emissao, data_de_vencimento, tipo):
    return MockDocCobranca(novo_id, numero_da_nota, empresa.nome, empresa.logradouro,
                           empresa.numero, empresa.complemento, empresa.bairro,
                           empresa.cidade, empresa.estado, empresa.cep, empresa.cnpj,
                           empresa.inscricao_estadual, empresa.inscricao_municipal,
                           empresa.telefone, empresa.email, data_de_emissao,
                           data_de_vencimento, tipo)

def inserir_documento_de_cobranca(doc):
    _documents_db.append(doc)
    print(f"  Inserido documento: {doc.numero_da_nota} para {doc.nome}")

def novo_item_de_cobranca(novo_id_item, novo_id_documento, lancamento):
    return MockItemCobranca(novo_id_item, novo_id_documento,
                            lancamento.qtd, lancamento.descricao, lancamento.valor)

def inserir_item_de_cobranca(item):
    _items_db.append(item)
    print(f"    Inserido item: {item.descricao} para doc ID {item.documento}")

# Mock de 'carregar_dados.py'
_mock_empresas = [
    MockEmpresa("EMP001", "Empresa A"),
    MockEmpresa("EMP002", "Empresa B"),
    MockEmpresa("EMP003", "Empresa C")
]
_mock_lancamentos = [
    MockLancamento("NF", "EMP001", 1, "Serviço X", 1000.00),
    MockLancamento("NF", "EMP002", 2, "Produto Y", 500.00),
    MockLancamento("REC", "EMP001", 1, "Aluguel", 2000.00),
    MockLancamento("NF", "EMP001", 1, "Serviço Z", 750.00)
]
tipos = sorted(list(set(l.modelo for l in _mock_lancamentos)))

def empresas_ativas(tipo):
    return sorted(list(set(l.nome for l in _mock_lancamentos if l.modelo == tipo)))

def obter_empresa_por_codigo(codigo):
    for emp in _mock_empresas:
        if emp.codigo == codigo:
            return emp
    return None

def obter_lancamentos_por_tipo_e_codigo(tipo, codigo):
    return [l for l in _mock_lancamentos if l.modelo == tipo and l.nome == codigo]

# Mock de 'configuracoes.py'
def data_de_emissao():
    return "2025-06-05" # Data fictícia para o exemplo

def data_de_vencimento():
    return "2025-07-05" # Data fictícia para o exemplo

# --- Função Principal ---

def empresas_com_numeros(tipo: str):
    """
    Retorna uma tupla contendo a lista de códigos de empresas ativas para um tipo
    e uma lista de números de notas sequenciais para essas empresas.
    """
    lista_empresas_ativas = empresas_ativas(tipo)
    proxima_nota_inicial = proxima_nota(tipo)
    # Gera uma lista de números de notas, um para cada empresa ativa
    numeros_de_notas = list(range(proxima_nota_inicial, proxima_nota_inicial + len(lista_empresas_ativas)))
    return lista_empresas_ativas, numeros_de_notas

def gerar_documentos(data_de_emissao: str, data_de_vencimento: str):
    """
    Itera sobre os tipos de lançamento e as empresas ativas para cada tipo,
    gerando e inserindo documentos de cobrança e seus respectivos itens.
    """
    print(f"Iniciando a geração de documentos para emissão em {data_de_emissao} e vencimento em {data_de_vencimento}...")
    for tipo in tipos:
        print(f"\nProcessando tipo: {tipo}")
        # Usa desempacotamento de tupla para obter os múltiplos valores
        empresas_do_tipo, numeros_do_tipo = empresas_com_numeros(tipo)

        # Zipar as listas para iterar sobre código da empresa e número da nota simultaneamente
        for codigo_empresa, numero_da_nota in zip(empresas_do_tipo, numeros_do_tipo):
            empresa = obter_empresa_por_codigo(codigo_empresa)
            if empresa: # Verifica se a empresa foi encontrada
                novo_id_documento = proximo_id_de_documento()
                documento = novo_documento_de_cobranca(novo_id_documento, numero_da_nota, empresa,
                                                      data_de_emissao, data_de_vencimento, tipo)
                lancamentos_associados = obter_lancamentos_por_tipo_e_codigo(tipo, codigo_empresa)

                inserir_documento_de_cobranca(documento)

                for lancamento in lancamentos_associados:
                    novo_id_item = proximo_id_de_item_de_cobranca()
                    item = novo_item_de_cobranca(novo_id_item, novo_id_documento, lancamento)
                    inserir_item_de_cobranca(item)
            else:
                print(f"  Aviso: Empresa com código '{codigo_empresa}' não encontrada para o tipo '{tipo}'. Pulando.")
    print("\nGeração de documentos concluída.")


def demo():
    """Função de demonstração para gerar documentos com datas padrão."""
    gerar_documentos(data_de_emissao(), data_de_vencimento())

# --- Exemplo de Uso ---
if __name__ == "__main__":
    demo()

    print("\n--- Documentos Gerados (Simulados) ---")
    for doc in _documents_db:
        print(doc)

    print("\n--- Itens Gerados (Simulados) ---")
    for item in _items_db:
        print(item)

