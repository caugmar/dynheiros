#!/usr/bin/env python

import uno
from com.sun.star.beans import PropertyValue

def terminate():
    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context)
    ctx = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    smgr = ctx.ServiceManager

    # Cria uma instância do aplicativo Calc
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    desktop.terminate()

if __name__ == "__main__":
    terminate()

