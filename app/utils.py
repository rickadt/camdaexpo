# Utilidades do sistema.
# from .app import app


# Log do sistema
def Log(text=''):
    uri = 'saida.log'
    file = open(uri, 'a')
    file.write(text)
    file.write('\n')
    file.close()
