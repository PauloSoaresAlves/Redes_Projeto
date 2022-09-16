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

## 
# Funcoes de manipulacao do placar
##

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


#<<MODIFICADA>>
# Recebe as coordenadas de uma peca. Retorna uma tupla do tipo (i, j)
# em caso de sucesso, ou False em caso de erro.
def leCoordenada(dim,user_input):


    try:
        i = int(user_input.split(' ')[0])
        j = int(user_input.split(' ')[1])
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


##<<Autoria Própria>>##

#Clase para facilitar a comunicação entre as threads
#Contém todas as informações necessárias para o cliente
class client_status():
    def __init__(self):
        self.gameStarted = False
        self.turn = -1
        self.tabuleiro = []
        self.placar = []
        self.myId = 0
        self.terminate=False      
    
#Função que lida com a entrada do usuário e o envio de mensagens para o servidor
#Thread que fica rodando em paralelo com a thread de recebimento de mensagens
#Por ser uma thread daemon, finaliza a execução quando a thread principal termina
def client_send(tcp_client, clientInfo: client_status):
    while not clientInfo.terminate:
        message = f'{input("")}'
        if not clientInfo.gameStarted:  
            tcp_client.send(message.encode('utf-8'))
        elif clientInfo.gameStarted and clientInfo.turn == clientInfo.myId:
            coordenadas = leCoordenada(len(clientInfo.tabuleiro),message)
            if(not coordenadas):
                pass
            else:
                i, j = coordenadas
                if clientInfo.tabuleiro[i][j] == "-" or clientInfo.tabuleiro[i][j] > 0:
                    print("Essa peça já foi removida ou aberta!")
                else:
                    tcp_client.send((str(i) + " " + str(j)).encode('utf-8'))
                    clientInfo.turn = -1  
        else:
            print("Chat desabilitado!")
    sys.exit(0)

#inputs do usuário
host = input("Digite o IP do servidor: ")
port = int(input("Digite a porta do servidor: "))

#Cria o socket
try:
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest = (host, port)
    tcp_client.connect(dest)
    print("Conectado ao servidor em ", dest)
except:
    print("Não foi possível conectar ao servidor")
    sys.exit(0)

#Cria a thread que lida com a entrada do usuário
clientInfo = client_status()
send_thread = threading.Thread(target=client_send, args=(tcp_client, clientInfo), daemon=True)
send_thread.start()

#Loop principal que fica recebendo mensagens do servidor
#Decodifica a mensagem e executa a ação correspondente
#0 - Mensagem para printar no console
#1 - Mensagem para atualizar dados do jogo corrente
#2 - Mensagem para iniciar o jogo
#3 - Mensagem para finalizar o jogo
while True:
        try:
            message = tcp_client.recv(1024).decode('utf-8').split("|")
            if message:
                for data in message:
                    if data != "":
                        if data[0] == "0":
                            print(data[1:])
                        elif data[0] == "1":
                            json_message = json.loads(data[1:])
                            clientInfo.tabuleiro = json_message["tabuleiro"]
                            clientInfo.placar = json_message["placar"]
                            clientInfo.turn = int(json_message["turn"])
                            imprimeStatus(clientInfo.tabuleiro,clientInfo.placar, clientInfo.turn)
                        elif data[0] == "2":
                            clientInfo.gameStarted = True
                        elif data[0] == "3":
                            clientInfo.myId = int(data[1:])
                        elif data[0] == "4":
                            tcp_client.close()
                            clientInfo.terminate = True
                            sys.exit(0)


        except:
            if clientInfo.terminate:
                sys.exit(0)
            print("Ocorreu um erro!")
            tcp_client.close()
            break

