from banco_de_dados import (proxima_nota, proximo_id_de_documento,
                            novo_documento_de_cobranca, inserir_documento_de_cobranca,
                            proximo_id_de_item_de_cobranca, novo_item_de_cobranca,
                            inserir_item_de_cobranca, proxima_nota,
                            Empresa, DocCobranca, ItemCobranca, Lancamento)
from carregar_dados import (carregar_dados, empresas_ativas, obter_empresa_por_codigo,
                            obter_lancamentos_por_tipo_e_codigo)
from configuracoes import data_de_emissao, data_de_vencimento

def empresas_com_numeros(tipo):
    lista_empresas_ativas = empresas_ativas(tipo)
    proxima_nota_inicial = proxima_nota(tipo)
    # Gera uma lista de números de notas, um para cada empresa ativa
    numeros_de_notas = list(range(proxima_nota_inicial, 
                                  proxima_nota_inicial + len(lista_empresas_ativas)))
    return lista_empresas_ativas, numeros_de_notas

def inserir_documento(data_de_emissao, data_de_vencimento, 
                      tipo, codigo_empresa, numero_da_nota, empresa):
    novo_id_documento = proximo_id_de_documento()
    documento = novo_documento_de_cobranca(novo_id_documento, numero_da_nota, empresa,
                                                      data_de_emissao, data_de_vencimento, tipo)
    lancamentos_associados = obter_lancamentos_por_tipo_e_codigo(tipo, codigo_empresa)
    print(f"Inserindo {documento}.")
    inserir_documento_de_cobranca(documento)
    return novo_id_documento,lancamentos_associados

def inserir_itens_de_cobranca(novo_id_documento, lancamentos_associados):
    for lancamento in lancamentos_associados:
        novo_id_item = proximo_id_de_item_de_cobranca()
        item = novo_item_de_cobranca(novo_id_item, novo_id_documento, lancamento)
        print(f"Inserindo {item}.")
        inserir_item_de_cobranca(item)

def gerar_documentos(data_de_emissao, data_de_vencimento):
    _, _, tipos = carregar_dados()
    print(f"Iniciando a geração de documentos para emissão em {data_de_emissao} e vencimento em {data_de_vencimento}...")
    print(f"Tipos: {tipos}.")
    for tipo in tipos:
        print(f"\nProcessando tipo: {tipo}")
        empresas_do_tipo, numeros_do_tipo = empresas_com_numeros(tipo)
        for codigo_empresa, numero_da_nota in zip(empresas_do_tipo, numeros_do_tipo):
            empresa = obter_empresa_por_codigo(codigo_empresa)
            if empresa: # Verifica se a empresa foi encontrada
                novo_id_doc, itens = inserir_documento(data_de_emissao, data_de_vencimento, 
                                                       tipo, codigo_empresa, numero_da_nota, empresa)
                inserir_itens_de_cobranca(novo_id_doc, itens)
            else:
                print(f"  Aviso: Empresa com código '{codigo_empresa}' não encontrada para o tipo '{tipo}'. Pulando.")
    print("\nGeração de documentos concluída.")

