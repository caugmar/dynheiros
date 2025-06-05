import sqlite3
from collections import namedtuple # Uma alternativa leve para structs
import os # Para simular o 'configuracoes.rkt' e operações de arquivo

# --- Configurações (simulando "configuracoes.rkt") ---
def banco_de_dados():
    """Retorna o nome do arquivo do banco de dados."""
    return "meu_banco_de_dados.db"

# --- Conexão com o Banco de Dados ---
# A conexão será estabelecida ao chamar uma função ou ao inicializar a aplicação
# Para este exemplo, a conexão é global, mas em uma aplicação real,
# você pode querer gerenciá-la de forma diferente (ex: pool de conexões).
conn = None

def get_db_connection():
    global conn
    if conn is None:
        conn = sqlite3.connect(banco_de_dados())
        conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
        _criar_tabelas() # Garante que as tabelas existem
    return conn

def close_db_connection():
    global conn
    if conn:
        conn.close()
        conn = None

def _criar_tabelas():
    """Cria as tabelas no banco de dados se não existirem."""
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS documentos_de_cobranca (
            id INTEGER PRIMARY KEY,
            numero_da_nota TEXT,
            nome TEXT,
            logradouro TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            cep TEXT,
            cnpj TEXT,
            inscricao_estadual TEXT,
            inscricao_municipal TEXT,
            telefone TEXT,
            email TEXT,
            data_de_emissao TEXT,
            data_de_vencimento TEXT,
            modelo TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS itens_de_cobranca (
            id INTEGER PRIMARY KEY,
            documento INTEGER,
            qtd REAL,
            descricao TEXT,
            valor REAL
        )
    ''')
    conn.commit()

# --- Classes (equivalente a STRUCTS) ---

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
        return f"Empresa(nome='{self.nome}', cnpj='{self.cnpj}')"

class Lancamento:
    def __init__(self, modelo, nome, qtd, descricao, valor):
        self.modelo = modelo
        self.nome = nome
        self.qtd = qtd
        self.descricao = descricao
        self.valor = valor

    def __repr__(self):
        return f"Lancamento(descricao='{self.descricao}', valor={self.valor})"

class DocCobranca:
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

    @classmethod
    def from_db_row(cls, row):
        """Cria um objeto DocCobranca a partir de uma linha do banco de dados."""
        return cls(
            id=row['id'],
            numero_da_nota=row['numero_da_nota'],
            nome=row['nome'],
            logradouro=row['logradouro'],
            numero=row['numero'],
            complemento=row['complemento'],
            bairro=row['bairro'],
            cidade=row['cidade'],
            estado=row['estado'],
            cep=row['cep'],
            cnpj=row['cnpj'],
            inscricao_estadual=row['inscricao_estadual'],
            inscricao_municipal=row['inscricao_municipal'],
            telefone=row['telefone'],
            email=row['email'],
            data_de_emissao=row['data_de_emissao'],
            data_de_vencimento=row['data_de_vencimento'],
            modelo=row['modelo']
        )

    def __repr__(self):
        return f"DocCobranca(id={self.id}, numero_da_nota='{self.numero_da_nota}', nome='{self.nome}')"


def novo_documento_de_cobranca(novo_id, numero_da_nota, empresa,
                               data_de_emissao, data_de_vencimento, tipo):
    return DocCobranca(novo_id,
                       numero_da_nota,
                       empresa.nome,
                       empresa.logradouro,
                       empresa.numero,
                       empresa.complemento,
                       empresa.bairro,
                       empresa.cidade,
                       empresa.estado,
                       empresa.cep,
                       empresa.cnpj,
                       empresa.inscricao_estadual,
                       empresa.inscricao_municipal,
                       empresa.telefone,
                       empresa.email,
                       data_de_emissao,
                       data_de_vencimento,
                       tipo)

class ItemCobranca:
    def __init__(self, id, documento, qtd, descricao, valor):
        self.id = id
        self.documento = documento
        self.qtd = qtd
        self.descricao = descricao
        self.valor = valor

    @classmethod
    def from_db_row(cls, row):
        """Cria um objeto ItemCobranca a partir de uma linha do banco de dados."""
        return cls(
            id=row['id'],
            documento=row['documento'],
            qtd=row['qtd'],
            descricao=row['descricao'],
            valor=row['valor']
        )

    def __repr__(self):
        return f"ItemCobranca(id={self.id}, documento={self.documento}, descricao='{self.descricao}')"


def novo_item_de_cobranca(novo_id_item, novo_id_documento, lancamento):
    return ItemCobranca(novo_id_item,
                        novo_id_documento,
                        lancamento.qtd,
                        lancamento.descricao,
                        lancamento.valor)

# --- Funções de Query (Queries) ---

def proxima_nota(tipo):
    """Retorna o próximo número de nota disponível para um dado tipo."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(numero_da_nota) FROM documentos_de_cobranca WHERE modelo LIKE ?", (tipo,))
    result = cur.fetchone()[0]
    return int(result) + 1 if result else 1

def proximo_id_de_documento():
    """Retorna o próximo ID disponível para um documento de cobrança."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM documentos_de_cobranca")
    result = cur.fetchone()[0]
    return int(result) + 1 if result else 1

def proximo_id_de_item_de_cobranca():
    """Retorna o próximo ID disponível para um item de cobrança."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM itens_de_cobranca")
    result = cur.fetchone()[0]
    return int(result) + 1 if result else 1

def inserir_documento_de_cobranca(doc: DocCobranca):
    """Insere um novo documento de cobrança no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO documentos_de_cobranca VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        doc.id, doc.numero_da_nota, doc.nome, doc.logradouro, doc.numero,
        doc.complemento, doc.bairro, doc.cidade, doc.estado, doc.cep,
        doc.cnpj, doc.inscricao_estadual, doc.inscricao_municipal,
        doc.telefone, doc.email, doc.data_de_emissao,
        doc.data_de_vencimento, doc.modelo
    ))
    conn.commit()

def inserir_item_de_cobranca(item: ItemCobranca):
    """Insere um novo item de cobrança no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO itens_de_cobranca VALUES (?, ?, ?, ?, ?)
    ''', (item.id, item.documento, item.qtd, item.descricao, item.valor))
    conn.commit()

def obter_documentos_por_tipo_e_data(tipo, data_de_emissao):
    """Obtém documentos de cobrança por tipo e data de emissão."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM documentos_de_cobranca
        WHERE modelo LIKE ? AND data_de_emissao LIKE ?
        ORDER BY nome
    ''', (tipo, data_de_emissao))
    rows = cur.fetchall()
    return [DocCobranca.from_db_row(row) for row in rows]

def obter_documentos_por_data(data_de_emissao):
    """Obtém todos os documentos de cobrança para uma dada data de emissão."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM documentos_de_cobranca
        WHERE data_de_emissao LIKE ?
        ORDER BY nome
    ''', (data_de_emissao,))
    rows = cur.fetchall()
    return [DocCobranca.from_db_row(row) for row in rows]

def obter_itens_de_cobranca_por_id_do_documento(doc_id):
    """Obtém itens de cobrança associados a um ID de documento."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM itens_de_cobranca
        WHERE documento LIKE ?
    ''', (str(doc_id),)) # SQLite pode converter int para string em LIKE, mas é bom ser explícito
    rows = cur.fetchall()
    return [ItemCobranca.from_db_row(row) for row in rows]

def obter_documentos_por_id(doc_id):
    """Obtém um documento de cobrança pelo seu ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM documentos_de_cobranca
        WHERE id LIKE ?
    ''', (str(doc_id),))
    row = cur.fetchone()
    return DocCobranca.from_db_row(row) if row else None

# --- Funções Utilitárias ---

def dinheiro(valor):
    """Formata um valor numérico como string de dinheiro (ex: 1.234,56)."""
    if valor == 0:
        return ""
    # Arredonda para 2 casas decimais e formata como string com separador de milhar e decimal
    return f"{valor:_.2f}".replace('.', '#').replace('_', '.').replace('#', ',')

def numerico(valor):
    """Converte uma string formatada em dinheiro para um número (float)."""
    if not isinstance(valor, str):
        return float(valor)
    if valor == "":
        return 0.0
    # Remove separadores de milhar, substitui vírgula por ponto e converte para float
    return float(valor.strip().replace(".", "").replace(",", ".").replace("R$ ", ""))

def slurp(arquivo):
    """Lê o conteúdo completo de um arquivo."""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "" # Ou levantar uma exceção, dependendo do comportamento desejado

def spit(arquivo, conteudo):
    """Escreve conteúdo em um arquivo, anexando se ele já existir."""
    with open(arquivo, 'a', encoding='utf-8') as f:
        f.write(conteudo)

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Garante que a conexão e tabelas são criadas
    get_db_connection()

    print("--- Testando Proximos IDs/Notas ---")
    print(f"Próxima nota 'NF': {proxima_nota('NF')}")
    print(f"Próximo ID de Documento: {proximo_id_de_documento()}")
    print(f"Próximo ID de Item de Cobrança: {proximo_id_de_item_de_cobranca()}")

    print("\n--- Testando Inserção ---")
    empresa_exemplo = Empresa(
        codigo="EMP001", nome="Empresa Teste LTDA", logradouro="Rua Exemplo",
        numero="123", complemento="Sala 1", bairro="Centro", cidade="São Paulo",
        estado="SP", cep="01000-000", cnpj="12.345.678/0001-90",
        inscricao_estadual="", inscricao_municipal="", telefone="11987654321",
        email="contato@empresa.com", planilha="planilha_teste.xlsx"
    )

    id_doc = proximo_id_de_documento()
    doc1 = novo_documento_de_cobranca(
        id_doc, "001", empresa_exemplo, "2025-06-05", "2025-07-05", "NF"
    )
    inserir_documento_de_cobranca(doc1)
    print(f"Documento inserido: {doc1.numero_da_nota}")

    lancamento1 = Lancamento("SERV", "Serviço A", 1, "Manutenção de Software", 1500.75)
    lancamento2 = Lancamento("PROD", "Produto B", 2, "Licença de Software", 500.50)

    id_item1 = proximo_id_de_item_de_cobranca()
    item1 = novo_item_de_cobranca(id_item1, doc1.id, lancamento1)
    inserir_item_de_cobranca(item1)
    print(f"Item de cobrança inserido: {item1.descricao}")

    id_item2 = proximo_id_de_item_de_cobranca()
    item2 = novo_item_de_cobranca(id_item2, doc1.id, lancamento2)
    inserir_item_de_cobranca(item2)
    print(f"Item de cobrança inserido: {item2.descricao}")

    print("\n--- Testando Consultas ---")
    docs_nf_hoje = obter_documentos_por_tipo_e_data("NF", "2025-06-05")
    print(f"Documentos tipo 'NF' de 2025-06-05 ({len(docs_nf_hoje)}):")
    for doc in docs_nf_hoje:
        print(f"  - {doc.nome}, Nota: {doc.numero_da_nota}")

    docs_hoje = obter_documentos_por_data("2025-06-05")
    print(f"\nDocumentos de 2025-06-05 ({len(docs_hoje)}):")
    for doc in docs_hoje:
        print(f"  - {doc.nome}, Nota: {doc.numero_da_nota}, Modelo: {doc.modelo}")

    itens_doc1 = obter_itens_de_cobranca_por_id_do_documento(doc1.id)
    print(f"\nItens do documento {doc1.id} ({len(itens_doc1)}):")
    for item in itens_doc1:
        print(f"  - Qtd: {item.qtd}, Descrição: {item.descricao}, Valor: {dinheiro(item.valor)}")

    doc_por_id = obter_documentos_por_id(doc1.id)
    print(f"\nDocumento obtido por ID {doc1.id}: {doc_por_id.nome}")

    print("\n--- Testando Funções Utilitárias ---")
    valor_dinheiro = dinheiro(1234.56)
    print(f"Formatar 1234.56 como dinheiro: {valor_dinheiro}")
    valor_numerico = numerico("R$ 1.234,56")
    print(f"Converter 'R$ 1.234,56' para numérico: {valor_numerico}")

    arquivo_teste = "teste.txt"
    spit(arquivo_teste, "Primeira linha.\n")
    spit(arquivo_teste, "Segunda linha.\n")
    conteudo_lido = slurp(arquivo_teste)
    print(f"\nConteúdo do arquivo '{arquivo_teste}':\n{conteudo_lido}")
    os.remove(arquivo_teste) # Limpa o arquivo de teste

    # Fechar a conexão com o banco de dados
    close_db_connection()

