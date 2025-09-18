#!/usr/bin/env python

import sys
import uno


def init(arquivo):
    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context)
    ctx = resolver.resolve(
        "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    smgr = ctx.ServiceManager

    # Cria uma instância do aplicativo Calc
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

    # Abre a planilha
    path = uno.systemPathToFileUrl(arquivo)
    document = desktop.loadComponentFromURL(path, '_default', 0, ())

    # Obtém planilha ativa
    sheet = document.CurrentController.ActiveSheet

    # Devolve desktop, modelo e planilha
    return (document, sheet)


def encontrar_o_total(sheet):
    search_column = 6
    search_text = "TOTAL"
    for row_index in range(sheet.Rows.Count):
        cell_value = sheet.getCellByPosition(
            search_column, row_index).getString()
        if cell_value == search_text:
            return row_index
    else:
        print("A linha do TOTAL não foi encontrada."
              + " Cheque pra ver se não excluiram.")


def inserir_linha(sheet, data, descricao, valor):
    indice = encontrar_o_total(sheet)
    sheet.Rows.insertByIndex(indice, 1)
    data_formatada = data[3:5] + "/" + data[0:2] + "/" + data[6:10]
    # Adiciona valores específicos às células nas novas linhas
    sheet.getCellByPosition(0, indice).setFormula(data_formatada)
    sheet.getCellByPosition(1, indice).setFormula(descricao)
    sheet.getCellByPosition(2, indice).setValue(valor)
    sheet.getCellByPosition(4, indice).setFormula("não")
    sheet.getCellByPosition(5, indice).setValue(0)
    index = indice + 1
    sheet.getCellByPosition(7, indice).setFormula(
        "=C" + str(index) + "-F" + str(index))
    # Atualiza a linha do TOTAL
    sheet.getCellByPosition(7, index).setFormula(
        "=SUM(H2:H" + str(index) + ")")


def save_and_close(document):
    # Salva a planilha
    document.store()

    # Fecha a planilha
    # document.close(True)


if __name__ == "__main__":
    arquivo = sys.argv[1]
    print("ARQUIVO: " + arquivo)
    data, descricao, valor = sys.argv[-3:]
    document, sheet = init(arquivo)
    inserir_linha(sheet, data, descricao, float(valor))
    save_and_close(document)
