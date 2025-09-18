import sqlite3
from collections import namedtuple
from configuracoes import banco_de_dados


conn = None


def get_db_connection():
    global conn
    if conn is None:
        conn = sqlite3.connect(banco_de_dados)
    return conn


def close_db_connection():
    global conn
    if conn:
        conn.close()
        conn = None


Empresa = namedtuple('Empresa', '''codigo nome logradouro numero complemento
                     bairro cidade estado cep cnpj inscricao_estadual
                     inscricao_municipal telefone email planilha''')

Lancamento = namedtuple('Lancamento', 'modelo nome qtd descricao valor')

DocCobranca = namedtuple('DocCobranca', '''id numero_da_nota nome
                         logradouro numero complemento bairro
                         cidade estado cep
                         cnpj inscricao_estadual inscricao_municipal
                         telefone email
                         data_de_emissao data_de_vencimento modelo''')


def novo_documento_de_cobranca(novo_id, numero_da_nota, empresa,
                               data_de_emissao, data_de_vencimento, tipo):
    return DocCobranca(novo_id, numero_da_nota, empresa.nome,
                       empresa.logradouro, empresa.numero, empresa.complemento,
                       empresa.bairro, empresa.cidade, empresa.estado,
                       empresa.cep, empresa.cnpj, empresa.inscricao_estadual,
                       empresa.inscricao_municipal, empresa.telefone,
                       empresa.email, data_de_emissao,
                       data_de_vencimento, tipo)


ItemCobranca = namedtuple('ItemCobranca', "id documento qtd descricao valor")


def novo_item_de_cobranca(novo_id_item, novo_id_documento, lancamento):
    return ItemCobranca(novo_id_item, novo_id_documento,
                        lancamento.qtd, lancamento.descricao, lancamento.valor)


def proxima_nota(tipo):
    """Retorna o próximo número de nota disponível para um dado tipo."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT MAX(numero_da_nota)
                FROM documentos_de_cobranca
                WHERE modelo LIKE ?""", (tipo,))
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


def inserir_documento_de_cobranca(doc):
    """Insere um novo documento de cobrança no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    query = '''INSERT INTO documentos_de_cobranca
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cur.execute(query, doc)
    conn.commit()


def inserir_item_de_cobranca(item: ItemCobranca):
    """Insere um novo item de cobrança no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO itens_de_cobranca VALUES (?, ?, ?, ?, ?)', item)
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
    return [DocCobranca(*row) for row in rows]


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
    return [DocCobranca(*row) for row in rows]


def obter_itens_de_cobranca_por_id_do_documento(doc_id):
    """Obtém itens de cobrança associados a um ID de documento."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM itens_de_cobranca
        WHERE documento LIKE ?
    ''', (str(doc_id),))
    rows = cur.fetchall()
    return [ItemCobranca(*row) for row in rows]


def obter_documentos_por_id(doc_id):
    """Obtém um documento de cobrança pelo seu ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM documentos_de_cobranca
        WHERE id LIKE ?
    ''', (str(doc_id),))
    row = cur.fetchone()
    return DocCobranca(*row) if row else None

# --- Funções Utilitárias ---


def dinheiro(valor):
    """Formata um valor numérico como string de dinheiro (ex: 1.234,56)."""
    if valor == 0:
        return ""
    # Arredonda para 2 casas decimais e formata como string
    # com separador de milhar e decimal
    res = f"{valor:_.2f}".replace('.', '#')
    res = res.replace('_', '.').replace('#', ',')
    return res


def numerico(valor):
    """Converte uma string formatada em dinheiro para um número (float)."""
    if not isinstance(valor, str):
        return float(valor)
    if valor == "":
        return 0.0
    # Remove separadores de milhar, substitui vírgula
    # por ponto e converte para float
    res = valor.strip().replace(".", "")
    res = res.replace(",", ".").replace("R$ ", "")
    return float(res)


def slurp(arquivo):
    """Lê o conteúdo completo de um arquivo."""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def spit(arquivo, conteudo):
    """Escreve conteúdo em um arquivo, anexando se ele já existir."""
    with open(arquivo, 'a', encoding='utf-8') as f:
        f.write(conteudo)
