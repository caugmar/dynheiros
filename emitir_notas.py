from weasyprint import HTML, CSS
from configuracoes import caminho_dos_templates
import chevron
import os
import subprocess
from banco_de_dados import (
    ItemCobranca, dinheiro,
    obter_documentos_por_tipo_e_data,
    obter_itens_de_cobranca_por_id_do_documento)
from extensos import em_reais
from carregar_dados import carregar_dados
from configuracoes import caminho_dos_templates

def procusto(lista):
    """
    Garante que a lista tenha exatamente 4 objetos ItemCobranca,
    preenchendo com itens vazios se necessário.
    """
    # Cria um item de preenchimento. Assumimos que
    # ItemCobranca(0, 0, "", "", 0) representa um item vazio
    # para fins de preenchimento.
    padding_item = ItemCobranca(
        id=0, documento=0, descricao="", qtd=0, valor=0.0)
    padded_list = lista + [padding_item] * 4
    return padded_list[:4]


def ajustar(texto, tamanho):
    """
    Ajusta o texto a um tamanho específico, truncando se for muito longo
    e preenchendo à esquerda com espaços se for muito curto.
    """
    s_texto = str(texto)
    if s_texto == "0":  # Para quando item.quantidade for zero
        s_texto = " "
    return s_texto.ljust(tamanho)[:tamanho]


def _posso_quebrar_em(texto, local):
    """
    Encontra o último ponto de quebra possível (espaço) antes ou em 'local',
    ou -1 se nenhum espaço for encontrado.
    """
    for i in range(local, -1, -1):
        if texto[i] == ' ':
            return i
    return -1  # Nenhum espaço encontrado


def quebrar(texto, local):
    """
    Quebra uma string em duas partes em uma posição 'local' especificada,
    priorizando a quebra em um espaço.
    """
    if local + 1 >= len(texto):
        # Se 'local' for o final ou além da string, retorna a string completa
        # e uma vazia
        return [texto, ""]
    posicao = _posso_quebrar_em(texto, local)
    if posicao == -1:  # Se nenhum espaço for encontrado, quebra em 'local'
        return [texto[:local], texto[local:]]
    else:
        # Retorna a primeira parte até o espaço e a segunda parte após o espaço
        return [texto[:posicao], texto[posicao + 1:]]


def _expandir_template(template, contexto):
    return chevron.render(template, contexto)


def _limpar_arquivos_antigos():
    for f in ["notas.txt", "notas.ps", "notas.pdf"]:
        if os.path.exists(f):
            os.remove(f)


def construir_contexto(documento, itens, end1, end2, total):
    return {"nome": ajustar(documento.nome, 52),
            "nffs": f"{documento.numero_da_nota:06d}",
            "endereco1": ajustar(end1, 48),
            "endereco2": ajustar(end2, 48),
            "endereco3": ajustar(end1, 48),
            "endereco4": ajustar(end2, 58),
            "bairro": ajustar(documento.bairro, 18),
            "cep": ajustar(documento.cep, 9),
            "uf": ajustar(documento.estado, 2),
            "cidade": ajustar(documento.cidade, 10),
            "cnpj": ajustar(documento.cnpj, 18),
            "ie": ajustar(documento.inscricao_estadual, 15),
            "im": ajustar(documento.inscricao_municipal, 5),
            "q1": ajustar(itens[0].qtd, 4),
            "d1": ajustar(itens[0].descricao, 36),
            "v1": dinheiro(itens[0].valor).rjust(11),
            "q2": ajustar(itens[1].qtd, 4),
            "d2": ajustar(itens[1].descricao, 36),
            "v2": dinheiro(itens[1].valor).rjust(11),
            "q3": ajustar(itens[2].qtd, 4),
            "d3": ajustar(itens[2].descricao, 36),
            "v3": dinheiro(itens[2].valor).rjust(11),
            "q4": ajustar(itens[3].qtd, 4),
            "d4": ajustar(itens[3].descricao, 36),
            "v4": dinheiro(itens[3].valor).rjust(11),
            "emissao": ajustar(documento.data_de_emissao, 10),
            "vcto": ajustar(documento.data_de_vencimento, 10),
            "total": dinheiro(total).rjust(11),
            "extenso": ajustar(em_reais(total), 69)}


def _endereco(documento):
    tmp = f"{documento.logradouro}, {documento.numero}"
    if documento.complemento != "-":
        tmp += f" - {documento.complemento}"
    tmp += f" - {documento.bairro} - {documento.cidade}"
    tmp += f" - {documento.estado} - CEP {documento.cep}"
    return tmp


def _obter_template(tipo):
    nome_do_arquivo_template = f"{tipo.lower()}.html"
    caminho_template = os.path.join(
        caminho_dos_templates, nome_do_arquivo_template)
    template = ""
    with open(caminho_template, "r", encoding="utf-8") as f:
        template = f.read()
    return template


def emitir_documentos(emissao):
    print("Iniciando a emissão de documentos via WeasyPrint...")
    
    # Lista para acumular o HTML de todos os documentos
    html_acumulado = ""
    _, _, tipos = carregar_dados()

    for tipo in tipos:
        template = _obter_template(tipo) # O template agora deve ser HTML
        documentos = obter_documentos_por_tipo_e_data(tipo, emissao)
        
        for doc in documentos:
            itens = procusto(obter_itens_de_cobranca_por_id_do_documento(doc.id))
            end1, end2 = quebrar(_endereco(doc), 48)
            total = sum(item.valor for item in itens)
            contexto = construir_contexto(doc, itens, end1, end2, total)
            
            # Concatena os documentos (cada um em uma página)
            # Adicionamos uma div com quebra de página se necessário
            html_acumulado += f'{_expandir_template(template, contexto)}'

    # Estilização para garantir o visual de "nota"
    css = CSS(string='''
        body { font-family: 'Courier New', Courier, monospace; }
    ''')

    # Gera o PDF final único
    HTML(string=html_acumulado, base_url='.').write_pdf("notas.pdf", stylesheets=[css])
    print("PDF 'notas.pdf' gerado com sucesso sem dependências externas.")
