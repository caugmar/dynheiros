import subprocess
import chevron
import os
from functools import reduce
from banco_de_dados import obter_documentos_por_tipo_e_data, obter_itens_de_cobranca_por_id_do_documento
from configuracoes import (mes_de_vencimento_por_extenso, titulo_do_relatorio,
                           caminho_dos_templates, data_de_vencimento_dos_recibos,
                           data_de_pagamento_dos_recibos)
import carregar_dados

def numerico(value):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace('.', '').replace(',', '.'))

def dinheiro(value):
    return f"{value:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')

def html_para_pdf(nome_do_arquivo):
    """
    Converte um arquivo HTML para PDF usando wkhtmltopdf.
    Assume que 'wkhtmltopdf' está instalado e no PATH do sistema.
    """
    nome = nome_do_arquivo.lower()
    command = (
        f"wkhtmltopdf "
        f"--orientation landscape "
        f"--margin-left 20 "
        f"--margin-bottom 20 "
        f"--footer-line "
        f"--footer-spacing 10 "
        f"--footer-left [date] "
        f"--footer-center '[page] de [topage]' "
        f"--footer-right [time] "
        f"{nome}.html "
        f"{nome}.pdf"
    )
    print(f"DEBUG: Executando comando: {command}")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"PDF '{nome}.pdf' gerado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao gerar PDF para {nome}:")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        print(f"Código de saída: {e.returncode}")
    except FileNotFoundError:
        print("ERRO: 'wkhtmltopdf' não encontrado. Certifique-se de que está instalado e no PATH.")

def nova_linha(doc):
    return {
        "numero": doc.numero_da_nota,
        "nome": doc.nome,
        "mensalidade": 0.0,
        "qt_trabalhistas": 0,
        "trabalhistas": 0.0,
        "qt_fiscais": 0,
        "fiscais": 0.0,
        "qt_xerox": 0,
        "xerox": 0.0,
        "qt_outros": 0,
        "outros": 0.0,
        "total": 0.0,
    }

def incr(mapa, campo, valor):
    """
    Incrementa um campo no mapa (dicionário), convertendo valores para numérico.
    Retorna uma cópia do mapa atualizada.
    """
    mapa_copia = mapa.copy()
    original = mapa_copia.get(campo)
    base = original if original is not None else 0
    valor_pronto = numerico(valor)
    base_pronta = numerico(base)
    mapa_copia[campo] = base_pronta + valor_pronto
    return mapa_copia

def atualizar_linha(linha, item):
    """
    Atualiza uma linha de relatório com base em um item de cobrança.
    """
    def desc(trecho):
        """Verifica se a descrição do item começa com um trecho específico."""
        return item.descricao.startswith(trecho)

    def incr_if_desc(mapa_atual, trecho, campo):
        """Incrementa um campo se a descrição do item corresponder ao trecho."""
        if desc(trecho):
            return incr(mapa_atual, campo, item.valor)
        return mapa_atual

    def incr_lanc_if_desc(mapa_atual, trecho, campo):
        """
        Incrementa a quantidade e o valor de um campo se a descrição do item
        corresponder ao trecho.
        """
        if desc(trecho):
            mapa_atual = incr(mapa_atual, f"qt_{campo}", item.qtd)
            mapa_atual = incr(mapa_atual, campo, item.valor)
        return mapa_atual

    def formatado(valor):
        """Formata um valor numérico como string de dinheiro e remove espaços extras."""
        return dinheiro(valor).strip()

    linha_atualizada = incr(linha, "total", item.valor)
    linha_atualizada = incr_if_desc(linha_atualizada, "Serv", "mensalidade")
    linha_atualizada = incr_if_desc(linha_atualizada, "Registro NF Paulista", "mensalidade")
    linha_atualizada = incr_lanc_if_desc(linha_atualizada, "Guias prev./trab.", "trabalhistas")
    linha_atualizada = incr_lanc_if_desc(linha_atualizada, "Guias fiscais", "fiscais")
    linha_atualizada = incr_lanc_if_desc(linha_atualizada, "Xerox", "xerox")
    linha_atualizada = incr_lanc_if_desc(linha_atualizada, "Outros", "outros")

    # Formatação dos campos de moeda
    linha_atualizada["mensalidade"] = formatado(linha_atualizada["mensalidade"])
    linha_atualizada["trabalhistas"] = formatado(linha_atualizada["trabalhistas"])
    linha_atualizada["fiscais"] = formatado(linha_atualizada["fiscais"])
    linha_atualizada["xerox"] = formatado(linha_atualizada["xerox"])
    linha_atualizada["outros"] = formatado(linha_atualizada["outros"])
    linha_atualizada["total"] = formatado(linha_atualizada["total"])
    return linha_atualizada

def gerar_linha_auxiliar(linha, itens):
    for item in itens:
        linha = atualizar_linha(linha, item)
    return linha

def gerar_linha(doc):
    linha = nova_linha(doc)
    itens = obter_itens_de_cobranca_por_id_do_documento(doc.id)
    return gerar_linha_auxiliar(linha, itens)

def somar_valor(campo, map1, map2):
    valor_1 = numerico(map1.get(campo))
    valor_2 = numerico(map2.get(campo))
    return dinheiro(valor_1 + valor_2)

def somar_quantidade(campo, map1, map2):
    valor_1 = map1.get(campo, 0)
    valor_2 = map2.get(campo, 0)
    return valor_1 + valor_2

def stringify_linha(linha):
    """
    Converte todos os valores numéricos de uma linha para string,
    formatando "0,00" para valores vazios ou zero.
    Retorna uma cópia da linha com os valores stringificados.
    """
    linha_copia = linha.copy()
    campos_para_string = [
        "numero", "mensalidade", "total", "trabalhistas", "fiscais",
        "xerox", "outros", "qt_trabalhistas", "qt_fiscais", "qt_xerox", "qt_outros"
    ]
    for campo in campos_para_string:
        val = linha_copia.get(campo)
        if isinstance(val, (int, float)):
            # Se já é um número, converte para string
            linha_copia[campo] = str(val)
        elif isinstance(val, str):
            # Se é string, verifica se está vazio e formata
            linha_copia[campo] = "0,00" if val.strip() == "" else val
        else:
            # Para None ou outros tipos, assume 0 e formata
            linha_copia[campo] = "0,00"
    return linha_copia

def emitir_relatorios(data_de_emissao):
    print(f"\n--- Emitindo Relatórios para a data: {data_de_emissao} ---")
    _, _, tipos = carregar_dados.carregar_dados()
    for tipo in tipos:
        print(f"Processando tipo: {tipo}")
        mes = mes_de_vencimento_por_extenso
        titulo = titulo_do_relatorio(tipo).format(mes)
        template_path = os.path.join(caminho_dos_templates, "relatorio.html")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            print(f"ERRO: Template '{template_path}' não encontrado. Certifique-se de que o arquivo existe.")
            continue
        documentos = obter_documentos_por_tipo_e_data(tipo, data_de_emissao)
        if not documentos:
            print(f"Nenhum documento encontrado para o tipo '{tipo}'. Pulando a geração do relatório.")
            continue
        linhas = [gerar_linha(doc) for doc in documentos]
        
        def combinar_linhas_para_total(acc_map, current_line_map):
            new_acc = acc_map.copy()
            new_acc["mensalidade"] = somar_valor("mensalidade", acc_map, current_line_map)
            new_acc["qt_trabalhistas"] = somar_quantidade("qt_trabalhistas", acc_map, current_line_map)
            new_acc["trabalhistas"] = somar_valor("trabalhistas", acc_map, current_line_map)
            new_acc["qt_fiscais"] = somar_quantidade("qt_fiscais", acc_map, current_line_map)
            new_acc["fiscais"] = somar_valor("fiscais", acc_map, current_line_map)
            new_acc["qt_xerox"] = somar_quantidade("qt_xerox", acc_map, current_line_map)
            new_acc["xerox"] = somar_valor("xerox", acc_map, current_line_map)
            new_acc["qt_outros"] = somar_quantidade("qt_outros", acc_map, current_line_map)
            new_acc["outros"] = somar_valor("outros", acc_map, current_line_map)
            new_acc["total"] = somar_valor("total", acc_map, current_line_map)
            # Campos que não são somados, mas são parte da linha de totais
            new_acc["numero"] = ""
            new_acc["nome"] = "TOTAIS"
            return new_acc
        # O primeiro elemento da lista é o valor inicial do acumulador
        totais = reduce(combinar_linhas_para_total, linhas[1:], linhas[0].copy())

        nome_do_arquivo_html = f"{tipo.lower()}.html"
        contexto = {
            "titulo": titulo,
            "linhas": [stringify_linha(linha) for linha in linhas], # Garante que os valores são strings
            "totais": stringify_linha(totais), # Garante que os valores são strings
        }

        if os.path.exists(nome_do_arquivo_html):
            os.remove(nome_do_arquivo_html)
            print(f"DEBUG: Arquivo existente '{nome_do_arquivo_html}' removido.")
        rendered_html = chevron.render(template=template, data=contexto)
        with open(nome_do_arquivo_html, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"DEBUG: Arquivo HTML '{nome_do_arquivo_html}' gerado.")
        html_para_pdf(tipo)

def emitir_recibos():
    """
    Emite recibos (exemplo: recibo de aluguel).
    """
    print("\n--- Emitindo Recibos ---")
    contexto = {
        "vencimento": data_de_vencimento_dos_recibos,
        "pagamento": data_de_pagamento_dos_recibos,
    }
    nome_do_arquivo_html = "aluguel.html"
    template_path = os.path.join(caminho_dos_templates, nome_do_arquivo_html)

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"ERRO: Template '{template_path}' não encontrado. Certifique-se de que o arquivo existe.")
        return

    rendered_html = chevron.render(template=template, data=contexto)

    with open(nome_do_arquivo_html, "w", encoding="utf-8") as f:
        f.write(rendered_html)
    print(f"DEBUG: Arquivo HTML '{nome_do_arquivo_html}' gerado.")

    try:
        subprocess.run(f"wkhtmltopdf {nome_do_arquivo_html} aluguel.pdf", shell=True, check=True, capture_output=True, text=True)
        print("PDF 'aluguel.pdf' gerado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao gerar PDF para aluguel:")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        print(f"Código de saída: {e.returncode}")
    except FileNotFoundError:
        print("ERRO: 'wkhtmltopdf' não encontrado. Certifique-se de que está instalado e no PATH.")
