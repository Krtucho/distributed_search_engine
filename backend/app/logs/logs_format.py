# Crear metodos para imprimir texto con colores 
# en la consola de comandos
#   - print_error
#   - print_warning
#   - print_info
#   - print_success
#   - print_debug
#   - print_log
#   - print
#   - print_line
#   - print_title
#   - print_subtitle
#   - print_subsubtitle
#   - print_subsubsubtitle
#   - print_subsubsubsubtitle
#   - print_subsubsubsubsubtitle
# Creame el codigo de los anteriores metodos por favor  :D
def print_error(text):
    print("\033[91m {}\033[00m" .format(text))

def print_warning(text):
    print("\033[93m {}\033[00m" .format(text))

def print_info(text):
    print("\033[94m {}\033[00m" .format(text))

def print_success(text):
    print("\033[92m {}\033[00m" .format(text))

def print_debug(text):
    print("\033[95m {}\033[00m" .format(text))

def print_log(text):
    print("\033[96m {}\033[00m" .format(text))

def print_line():
    print("--------------------------------------------------")

def print_title(text):
    print_line()
    print(text)
    print_line()

def print_subtitle(text):
    print_line()
    print(text)
    print_line()

def print_subsubtitle(text):
    print_line()
    print(text)
    print_line()