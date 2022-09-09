from ipaddress import ip_address
from multiprocessing import connection
from multiprocessing.connection import wait
import os
import sys
import time
import threading
import types
import random
import socket
import selectors
# Teste

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
def leCoordenada(dim):

    user_input = input("Especifique uma peca: ")

    try:
        i = int(user_input.split(' ')[0])
        j = int(user_input.split(' ')[1])
    except ValueError:
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

class gameInstance():
    def __init__(self, dim, nJogadores,clients,ids,socket: socket.socket):
        self.checkerSize = dim
        self.nJogadores = nJogadores
        self.clients = clients
        self.ids = ids
        self.tabuleiro = novoTabuleiro(dim)
        self.placar = novoPlacar(nJogadores)
        self.gameState = 0
        self.turn = 0
        self.move = []
        self.socket = socket

    def reset(self):
        self.tabuleiro = novoTabuleiro(self.checkerSize)
        self.placar = novoPlacar(self.nJogadores)
        self.gameState = 0
        self.turn = 0
        self.move = []
        self.clients = []
        self.ids = []

    def play(self):
        self.gameState = 1
        totalDePares = self.checkerSize**2 / 2
        paresEncontrados = 0
        self.turn = 0
        while paresEncontrados < totalDePares:

            # Requisita primeira peca do proximo jogador
            #1 - printa o status atual do jogo
            #2 - mensagem
            sendMessageToClients(f"2|",self.clients)
            sendMessageToClients(f"1{encodeArray(self.tabuleiro)};{self.placar};{self.turn}|",self.clients)
            time.sleep(0.5)
            self.clients[self.turn].send(f"0Escolha uma peça|".encode("utf-8"))
            time.sleep(0.1)

            while(len(self.move) == 0):
                time.sleep(0.1)

            i1, j1 = int(self.move[0]),int(self.move[1])
            self.move = []

            # Vira a peça escolhida
            self.tabuleiro[i1][j1] = -self.tabuleiro[i1][j1]
            sendMessageToClients(f"1{encodeArray(self.tabuleiro)};{self.placar};{self.turn}|",self.clients)
            time.sleep(0.5)
            self.clients[self.turn].send(f"0Escolha uma peça|".encode("utf-8"))
            time.sleep(0.1)

            while(len(self.move) == 0):
                time.sleep(0.1)

            i2, j2 = int(self.move[0]),int(self.move[1])
            self.move = []

            self.tabuleiro[i2][j2] = -self.tabuleiro[i2][j2]
            sendMessageToClients(f"1{encodeArray(self.tabuleiro)};{self.placar};{self.turn}|",self.clients)
            time.sleep(0.5)
            sendMessageToClients(f"0Pecas escolhidas --> ({i1}, {j1}) e ({i2}, {j2})|",self.clients)
            time.sleep(0.5)

            # Pecas escolhidas sao iguais?
            if self.tabuleiro[i1][j1] == self.tabuleiro[i2][j2]:

                sendMessageToClients(f"0Pecas casam! Ponto para o jogador {self.turn + 1}.|",self.clients)
                
                incrementaPlacar(self.placar, self.turn)
                paresEncontrados = paresEncontrados + 1
                removePeca(self.tabuleiro, i1, j1)
                removePeca(self.tabuleiro, i2, j2)

                time.sleep(5)
            else:

                sendMessageToClients(f"0Pecas nao casam!|",self.clients)
                
                time.sleep(3)

                fechaPeca(self.tabuleiro, i1, j1)
                fechaPeca(self.tabuleiro, i2, j2)
                self.turn = (self.turn + 1) % self.nJogadores

        # Verificar o vencedor e imprimir
        pontuacaoMaxima = max(self.placar)
        vencedores = []
        for i in range(0, self.nJogadores):

            if self.placar[i] == pontuacaoMaxima:
                vencedores.append(i)

        if len(vencedores) > 1:
            winners = ""
            for i in vencedores:
                winners += str(i + 1) + " "
            sendMessageToClients(f"0Houve empate entre os jogadores {winners}\n|",self.clients)
        else:
            sendMessageToClients(f"0{self.gameState}|{2}|Jogador {vencedores[0] + 1} foi o vencedor!|",self.clients)
        for client in self.clients:
            client.close()
        self.reset()
        receive(self.socket,self.clients,self.ids,self)

    
def encodeArray(array):
    line = ""
    for i in array:
        line += str(i) + "%"
    return line

# Função padrão que manda uma mensagem para todos os clientes
def sendMessageToClients(message,clients):
    for client in clients:
        client.send(message.encode('utf-8'))

# Função que recebe a mensagem do cliente e retorna a para todos os outros clientes
def clientThread(conn,address,clients: list, ids: list, game: gameInstance):
    index = clients.index(conn)
    conn.send(f"3{ids[index]}|".encode("utf-8"))
    conn.send(f"0Bem vindo ao jogo, jogador {ids[index]}!\nSinta-se a vontade para usar o chat enquanto os jogadores se conectam!|".encode('utf-8'))
    while True:
        try:
            message = conn.recv(1024)
            if(game.gameState == 0):
                message_to_send = f"0Jogador {ids[index]}: {message.decode('utf-8')}|"
                print(message_to_send)
                sendMessageToClients(message_to_send,clients)
            else:
                move = message.decode('utf-8').split(' ')
                if(game.turn == index and len(move) > 1):
                    game.move = message.decode('utf-8').split(' ')
                else:
                    conn.send("0Não é sua vez|".encode('utf-8'))

        except:
            sendMessageToClients(f"0Jogador {ids[index]} Deixou o jogo!\nAguardando conexões... {len(clients)}/{game.nJogadores}|",clients)
            clients.remove(conn)
            ids.remove(ids[index])
            conn.close()       
            break

def receive(server : socket.socket, clients: list, ids: list, game: gameInstance):
    while len(clients) < game.nJogadores:
        print(f"Aguardando conexões... {len(clients)}/{game.nJogadores}")
        sendMessageToClients(f"0Aguardando conexões... {len(clients)}/{game.nJogadores}|",clients)
        conn, address = server.accept()
        clients.append(conn)
        ids.append(len(clients)-1)
        print(f"Conectado com {address}")
        sendMessageToClients(f"0Jogador {ids[len(ids)-1]} entrou no jogo!|",clients)
        thread = threading.Thread(target=clientThread, args=(conn,address,clients,ids,game))
        thread.start()
    print("Todos os jogadores conectados!\nIniciando jogo...")
    sendMessageToClients("0Todos os jogadores conectados!\nIniciando jogo...|",clients)
    time.sleep(3)
    game.play()
    
           
def main():
    ##
    # Parametros da partida
    ##

    # Tamanho (da lateral) do tabuleiro. NECESSARIAMENTE PAR E MENOR QUE 10!
    dim = int(input("Digite o tamanho do tabuleiro (Menor que 10, maior que 2 e par!): "))
    while(dim < 2 or int(dim) > 10 or int(dim) % 2 != 0):
        print("Tamanho invalido!")
        dim = int(input("Digite o tamanho do tabuleiro (Menor que 10 e par!): "))


    # Numero de jogadores
    nJogadores = int(input("Digite o numero de jogadores (Min: 1 jogador): "))
    while(nJogadores < 1):
        print("Numero invalido!")
        nJogadores = int(input("Digite o numero de jogadores: "))

    # Numero total de pares de pecas
    

    ##
    # Programa principal
    ##

    hostname=socket.gethostname()   
    ip_address=socket.gethostbyname(hostname)
    print(f"IP do servidor: {ip_address}")
    port = 25542

    print(f"Servidor aberto na porta: {port}")
    tpc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tpc_server.bind((ip_address, port))
    tpc_server.listen(nJogadores)
    client_list = []
    ids = []
    game = gameInstance(dim,nJogadores,client_list,ids,tpc_server)
    receive(tpc_server,client_list,ids,game)

main()

'''
# Partida continua enquanto ainda ha pares de pecas a 
# casar.
paresEncontrados = 0
vez = 0
while paresEncontrados < totalDePares:

    # Requisita primeira peca do proximo jogador
    while True:

        # Imprime status do jogo
        imprimeStatus(tabuleiro, placar, vez)

        # Solicita coordenadas da primeira peca.
        coordenadas = leCoordenada(dim)
        if coordenadas == False:
            continue

        i1, j1 = coordenadas

        # Testa se peca ja esta aberta (ou removida)
        if abrePeca(tabuleiro, i1, j1) == False:

            print ("Escolha uma peca ainda fechada!")
            input("Pressione <enter> para continuar...")
            continue

        break 

    # Requisita segunda peca do proximo jogador
    while True:

        # Imprime status do jogo
        imprimeStatus(tabuleiro, placar, vez)

        # Solicita coordenadas da segunda peca.
        coordenadas = leCoordenada(dim)
        if coordenadas == False:
            continue

        i2, j2 = coordenadas

        # Testa se peca ja esta aberta (ou removida)
        if abrePeca(tabuleiro, i2, j2) == False:

            print ("Escolha uma peca ainda fechada!")
            input("Pressione <enter> para continuar...")
            continue

        break 

    # Imprime status do jogo
    imprimeStatus(tabuleiro, placar, vez)

    print ("Pecas escolhidas --> ({0}, {1}) e ({2}, {3})\n".format(i1, j1, i2, j2))

    # Pecas escolhidas sao iguais?
    if tabuleiro[i1][j1] == tabuleiro[i2][j2]:

        print ("Pecas casam! Ponto para o jogador {0}.".format(vez + 1))
        
        incrementaPlacar(placar, vez)
        paresEncontrados = paresEncontrados + 1
        removePeca(tabuleiro, i1, j1)
        removePeca(tabuleiro, i2, j2)

        time.sleep(5)
    else:

        print("Pecas nao casam!")
        
        time.sleep(3)

        fechaPeca(tabuleiro, i1, j1)
        fechaPeca(tabuleiro, i2, j2)
        vez = (vez + 1) % nJogadores

# Verificar o vencedor e imprimir
pontuacaoMaxima = max(placar)
vencedores = []
for i in range(0, nJogadores):

    if placar[i] == pontuacaoMaxima:
        vencedores.append(i)

if len(vencedores) > 1:

    sys.stdout.write("Houve empate entre os jogadores ")
    for i in vencedores:
        sys.stdout.write(str(i + 1) + ' ')

    sys.stdout.write("\n")

else:

    print("Jogador {0} foi o vencedor!".format(vencedores[0] + 1))

'''
