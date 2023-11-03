import socket
from tkinter import *
from tkinter import scrolledtext
from urllib.parse import urljoin, urlparse
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup


# Função para executar a varredura
def executar_varredura():
    # Limpa a área de resultados
    txt.delete('1.0', END)

    # Obtém a URL inserida pelo usuário
    url = entry.get()

    try:
        # Faz uma requisição GET para a URL
        resposta_http = requests.get(url)
        resposta_http.raise_for_status()  # Lança uma exceção para erros HTTP
        texto_html = resposta_http.text

        soup = BeautifulSoup(texto_html, 'html.parser')
   
        
        # Procura por links que poderiam ser vulneráveis a ataques de força bruta
        for link in soup.find_all('a'):
            # Verifica se o link parece ser uma área restrita
            if 'admin' in link.get('href'):
                txt.insert(INSERT, f'Potencial área administrativa encontrada: {link.get("href")}\n')
            else:
                txt.insert(INSERT, f'Nenhuma informação sobre area administrativa encontrada.\n')
                break

        # Verifica se a página possui um formulário de login
        formulario = soup.find('form')
        if formulario:
            txt.insert(INSERT, 'Formulário de login encontrado.\n')

        # Exibe a quantidade total de imagens e os URLs das imagens
        imagens = soup.find_all('img')
        txt.insert(INSERT, f'\nTotal de imagens encontradas: {len(imagens)}\n')
        for img in imagens:
            txt.insert(INSERT, f'URL da imagem: {urljoin(url, img["src"])}\n')

        # Exibe links externos
        links_externos = set()
        for link in soup.find_all('a', href=True):
            link_absoluto = urljoin(url, link['href'])
            if urlparse(link_absoluto).netloc != urlparse(url).netloc:
                links_externos.add(link_absoluto)
        if links_externos:
            txt.insert(INSERT, '\nLinks externos encontrados:\n')
            for link in links_externos:
                txt.insert(INSERT, f'{link}\n')

    except requests.exceptions.RequestException as e:
        txt.insert(INSERT, f'Erro ao acessar a URL: {e}\n')


def verificar_portas_abertas(url):
    # Obtem o nome do host a partir da URL
    host = urlparse(url).hostname

    # Lista de portas para verificar
    portas_alvo = [22, 80, 443, 8080]

    # Tenta se conectar a cada porta e verifica certificações SSL
    for porta in portas_alvo:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)

            resultado = s.connect_ex((host, porta))

            if resultado == 0:
                txt.insert(INSERT, f'A porta {porta} está aberta\n')
            else:
                txt.insert(INSERT, f'A porta {porta} está fechada\n')

            s.close()

           # Verifica as certificações SSL do site
        
            ssl_context = ssl.create_default_context()
            conn = ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            conn.connect((host, 443))
            cert = conn.getpeercert()
            txt.insert(INSERT, f'Certificações SSL do site:\n')
            for key, value in cert.items():
                txt.insert(INSERT, f'{key}: {value}\n')
            conn.close()
        except Exception as ex:
            txt.insert(INSERT, f'Erro ao verificar portas e certificações SSL do site: {ex}\n')
# Função para limpar os resultados na área de texto
def impar_resultados():
    txt.delete('1.0', END)

def arquivar_resultados():
    try:
        # Abre uma janela de salvamento de arquivo
        nome_arquivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivos de Texto", "*.txt")])

        # Verifica se um nome de arquivo foi selecionado
        if nome_arquivo:
            with open(nome_arquivo, 'w') as arquivo:
                # Obtém o conteúdo da área de texto e escreve no arquivo
                conteudo = txt.get('1.0', END)
                arquivo.write(conteudo)
            txt.insert(INSERT, f'Resultados arquivados em: {nome_arquivo}\n')
    except Exception as e:
        txt.insert(INSERT, f'Erro ao arquivar resultados: {e}\n')


# Cria a janela principal
janela = Tk()

# Configura a janela
janela.title('ToolScany - Ferramenta de Varredura de Sites')
janela.geometry('800x600')


# Cria um rótulo para a entrada da URL
lbl1 = Label(janela, text='Insira a URL do site a ser verificado:')
lbl1.grid(row=0, column=0, padx=10, pady=10)

# Cria uma entrada para a URL do site
entry = Entry(janela, width=40)
entry.grid(row=0, column=1, padx=10, pady=10)

# Cria um botão para iniciar a varredura
btn_executar = Button(janela, text='Executar', command=executar_varredura, bg='blue', fg='white')
btn_executar.grid(row=0, column=2, padx=10, pady=10)

# Cria um botão para limpar os resultados
btn_limpar = Button(janela, text='Limpar Resultados', command=impar_resultados, bg='blue', fg='white')
btn_limpar.grid(row=0, column=3, padx=10, pady=10)

# Cria uma área de texto para exibir os resultados
txt = scrolledtext.ScrolledText(janela, wrap=WORD)
txt.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

btn_arquivar = Button(janela, text='Arquivar', command=arquivar_resultados, bg='blue', fg='white')
btn_arquivar.grid(row=0, column=4, padx=10, pady=10)

# Loop principal da janela
janela.mainloop()