Todos os módulos funcionando:

- dynheiros (módulo principal, coordena todo o resto)
- atualizar_planilha
- banco_de_dados
- carregar_dados
- configuracoes
- emitir_notas
- enviar_emails
- extensos
- gerar_documentos
- gerar_relatorios
- encerrar-libreoffice.py
- inserir-linha.py

O código foi checado e limpo.

Terminei a migração da geração de relatórios e notas 
para o WeasyPrint, removendo todas as dependências de 
executáveis externos (wkhtmltopdf, enscript, recode, etc.),
exceto pelo LibreOffice, que não temos como emular.
