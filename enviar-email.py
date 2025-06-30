#!/usr/bin/env python

import sys
import yagmail

email = sys.argv[1]
titulo = 'Ficha de Situação - Escritório Minister - ' + sys.argv[2]
anexo = sys.argv[3]

yag = yagmail.SMTP('escritoriominister@gmail.com', 'ryzmfzsnppmgkpmx')
yag.useralias = "Minister Serviços Contábeis Ltda."
contents = """
    <p>Segue anexa a planilha com sua situação atual.<br/>
    Atenciosamente,</p>
    <p>Minister Serviços Contábeis Ltda.</p>
    """
yag.send(to=email, subject=titulo,
        contents=contents, attachments=anexo)

