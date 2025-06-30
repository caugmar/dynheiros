from banco_de_dados import (proxima_nota, proximo_id_de_documento,
                             novo_documento_de_cobranca, inserir_documento_de_cobranca,
                             proximo_id_de_item_de_cobranca, novo_item_de_cobranca,
                             inserir_item_de_cobranca,
                             Empresa, DocCobranca, ItemCobranca, Lancamento)

from carregar_dados import (carregar_dados, empresas_ativas, obter_empresa_por_codigo,
                            obter_lancamentos_por_tipo_e_codigo, tipos, empresas, lancamentos)

from configuracoes import data_de_emissao, data_de_vencimento

_next_doc_id = 1
_next_item_id = 1
_next_nf_number = 1
_next_rec_number = 1

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

def empresas_ativas(tipo):
    return sorted(list(set(l.nome for l in lancamentos if l.modelo == tipo)))

def obter_empresa_por_codigo(codigo):
    for emp in empresas:
        if emp.codigo == codigo:
            return emp
    return None

def obter_lancamentos_por_tipo_e_codigo(tipo, codigo):
    return [l for l in lancamentos if l.modelo == tipo and l.nome == codigo]

#  de 'configuracoes.py'
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
    print(f"Iniciando a geração de documentos para emissão em {data_de_emissao} e vencimento em {data_de_vencimento}...")
    for tipo in tipos:
        print(f"\nProcessando tipo: {tipo}")
        empresas_do_tipo, numeros_do_tipo = empresas_com_numeros(tipo)
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
