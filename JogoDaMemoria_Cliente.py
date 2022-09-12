import os
import sys
import threading
import random
import socket
import json

##
# Funcoes uteis
##

# Limpa a tela.
def limpaTela():
    
    os.system('cls' if os.name == 'nt' else 'clear')

##
# Funcoes de manipulacao do tabuleiro
##

# Imprime estado atual do tabuleiro
def imprimeTabuleiro(tabuleiro):

    # Limpa a tela
    limpaTela()

    # Imprime coordenadas horizontais
    dim = len(tabuleiro)
    sys.stdout.write("     ")
    for i in range(0, dim):
        sys.stdout.write("{0:2d} ".format(i))

    sys.stdout.write("\n")

    # Imprime separador horizontal
    sys.stdout.write("-----")
    for i in range(0, dim):
        sys.stdout.write("---")

    sys.stdout.write("\n")

    for i in range(0, dim):

        # Imprime coordenadas verticais
        sys.stdout.write("{0:2d} | ".format(i))

        # Imprime conteudo da linha 'i'
        for j in range(0, dim):

            # Peca ja foi removida?
            if tabuleiro[i][j] == '-':

                # Sim.
                sys.stdout.write(" - ")

            # Peca esta levantada?
            elif tabuleiro[i][j] >= 0:

                # Sim, imprime valor.
                sys.stdout.write("{0:2d} ".format(tabuleiro[i][j]))
            else:

                # Nao, imprime '?'
                sys.stdout.write(" ? ")

        sys.stdout.write("\n")

# Cria um novo tabuleiro com pecas aleatorias. 
# 'dim' eh a dimensao do tabuleiro, necessariamente
# par.
def novoTabuleiro(dim):

    # Cria um tabuleiro vazio.
    tabuleiro = []
    for i in range(0, dim):

        linha = []
        for j in range(0, dim):

            linha.append(0)

        tabuleiro.append(linha)

    # Cria uma lista de todas as posicoes do tabuleiro. Util para
    # sortearmos posicoes aleatoriamente para as pecas.
    posicoesDisponiveis = []
    for i in range(0, dim):

        for j in range(0, dim):

            posicoesDisponiveis.append((i, j))

    # Varre todas as pecas que serao colocadas no 
    # tabuleiro e posiciona cada par de pecas iguais
    # em posicoes aleatorias.
    for j in range(0, int(dim / 2)):
        for i in range(1, dim + 1):

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoesDisponiveis)
            indiceAleatorio = random.randint(0, maximo - 1)
            rI, rJ = posicoesDisponiveis.pop(indiceAleatorio)

            tabuleiro[rI][rJ] = -i

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoesDisponiveis)
            indiceAleatorio = random.randint(0, maximo - 1)
            rI, rJ = posicoesDisponiveis.pop(indiceAleatorio)

            tabuleiro[rI][rJ] = -i

    return tabuleiro

# Abre (revela) peca na posicao (i, j). Se posicao ja esta
# aberta ou se ja foi removida, retorna False. Retorna True
# caso contrario.
def abrePeca(tabuleiro, i, j):

    if tabuleiro[i][j] == '-':
        return False
    elif tabuleiro[i][j] < 0:
        tabuleiro[i][j] = -tabuleiro[i][j]
        return True

    return False

# Fecha peca na posicao (i, j). Se posicao ja esta
# fechada ou se ja foi removida, retorna False. Retorna True
# caso contrario.
def fechaPeca(tabuleiro, i, j):

    if tabuleiro[i][j] == '-':
        return False
    elif tabuleiro[i][j] > 0:
        tabuleiro[i][j] = -tabuleiro[i][j]
        return True

    return False

# Remove peca na posicao (i, j). Se posicao ja esta
# removida, retorna False. Retorna True
# caso contrario.
def removePeca(tabuleiro, i, j):

    if tabuleiro[i][j] == '-':
        return False
    else:
        tabuleiro[i][j] = "-"
        return True

## 
# Funcoes de manipulacao do placar
##

# Cria um novo placar zerado.
def novoPlacar(nJogadores):

    return [0] * nJogadores

# Adiciona um ponto no placar para o jogador especificado.
def incrementaPlacar(placar, jogador):

    placar[jogador] = placar[jogador] + 1

# Imprime o placar atual.
def imprimePlacar(placar):

    nJogadores = len(placar)

    print("Placar:")
    print("---------------------")
    for i in range(0, nJogadores):
        print ("Jogador {0}: {1:2d}".format(i + 1, placar[i]))

##
# Funcoes de interacao com o usuario
#

# Imprime informacoes basicas sobre o estado atual da partida.
def imprimeStatus(tabuleiro, placar, vez):

        imprimeTabuleiro(tabuleiro)
        sys.stdout.write('\n')

        imprimePlacar(placar)
        sys.stdout.write('\n')
        sys.stdout.write('\n')

        print ("Vez do Jogador {0}.\n".format(vez + 1))

# Le um coordenadas de uma peca. Retorna uma tupla do tipo (i, j)
# em caso de sucesso, ou False em caso de erro.
def leCoordenada(dim,entry):


    try:
        i = int(entry.split(' ')[0])
        j = int(entry.split(' ')[1])
    except ValueError:
        print("Coordenadas invalidas! Use o formato \"i j\" (sem aspas),")
        print("onde i e j sao inteiros maiores ou iguais a 0 e menores que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False
    except IndexError:
        print("Coordenadas invalidas! Use o formato \"i j\" (sem aspas),")
        print("onde i e j sao inteiros maiores ou iguais a 0 e menores que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    if i < 0 or i >= dim:

        print ("Coordenada i deve ser maior ou igual a zero e menor que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    if j < 0 or j >= dim:

        print ("Coordenada j deve ser maior ou igual a zero e menor que {0}".format(dim))
        input("Pressione <enter> para continuar...")
        return False

    return (i, j)

##
# Parametros da partida
##
class client_lock():
    def __init__(self):
        self.gameStarted = False
        self.turn = -1
        self.tabuleiro = []
        self.placar = []
        self.myId = 0
        self.terminate=False      
    

def client_send(client, client_lock: client_lock):
    while not client_lock.terminate:
        message = f'{input("")}'
        if not client_lock.gameStarted:  
            client.send(message.encode('utf-8'))
        elif client_lock.gameStarted and client_lock.turn == client_lock.myId:
            coordenadas = leCoordenada(len(client_lock.tabuleiro),message)
            if(not coordenadas):
                pass
            else:
                i, j = coordenadas
                if client_lock.tabuleiro[i][j] == "-" or client_lock.tabuleiro[i][j] > 0:
                    print("Essa peça já foi removida ou aberta!")
                else:
                    client.send((str(i) + " " + str(j)).encode('utf-8'))
                    client_lock.turn = -1  
        else:
            print("Chat desabilitado!")
    sys.exit(0)


host = input("Digite o IP do servidor: ")
port = int(input("Digite a porta do servidor: "))

tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (host, port)
tcp_client.connect(dest)
print("Conectado ao servidor em ", dest)
client_lock = client_lock()
send_thread = threading.Thread(target=client_send, args=(tcp_client, client_lock), daemon=True)
send_thread.start()
while True:
        try:
            message = tcp_client.recv(1024).decode('utf-8').split("|")
            if message:
                for data in message:
                    if data != "":
                        if data[0] == "0":
                            print(data[1:])
                        elif data[0] == "1":
                            print(data[1:])
                            json_message = json.loads(data[1:])
                            client_lock.tabuleiro = json_message["tabuleiro"]
                            client_lock.placar = json_message["placar"]
                            client_lock.turn = int(json_message["turn"])
                            imprimeStatus(client_lock.tabuleiro,client_lock.placar, client_lock.turn)
                        elif data[0] == "2":
                            client_lock.gameStarted = True
                        elif data[0] == "3":
                            client_lock.myId = int(data[1:])
                        elif data[0] == "4":
                            tcp_client.close()
                            client_lock.terminate = True
                            sys.exit(0)


        except:
            if client_lock.terminate:
                sys.exit(0)
            print("Ocorreu um erro!")
            tcp_client.close()
            break

