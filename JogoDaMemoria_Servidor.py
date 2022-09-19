import os
import sys
import time
import threading
import socket
import random
import json


##
# Funcoes de manipulacao do tabuleiro
##

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


##<<Autoria Própria>>##

#Classe que representa uma instancia do jogo
#Inicializa as variaveis para o jogo
#Possui a função de rodar e resetar o jogo
class gameInstance():
    def __init__(self, dim:int, nJogadores:int,socket: socket.socket):
        self.checkerSize = dim
        self.nJogadores = nJogadores
        self.clients = []
        self.ids = []
        self.tabuleiro = novoTabuleiro(dim)
        self.placar = novoPlacar(nJogadores)
        self.gameState = 0 #gameState 1 = rodando, 0 = parado
        self.turn = 0
        self.move = []
        self.socket = socket

    #Reseta o jogo para o estado inicial
    def reset(self):
        self.tabuleiro = novoTabuleiro(self.checkerSize)
        self.placar = novoPlacar(self.nJogadores)
        self.gameState = 0
        self.turn = 0
        self.move = []
        self.clients = []
        self.ids = []

    #Função que roda o jogo
    #0 - Mensagem para printar no console
    #1 - Mensagem para atualizar dados do jogo corrente
    #2 - Mensagem para iniciar o jogo
    #3 - Mensagem para receber o id do cliente
    #4 - Mensagem para finalizar o jogo
    def play(self):
        self.gameState = 1
        totalDePares = self.checkerSize**2 / 2
        paresEncontrados = 0
        self.turn = 0
        while paresEncontrados < totalDePares:

            #Envia mensagem para o cliente atual que o jogo começou
            sendMessageToClients(f"2|",self.clients)

            #Da os dados da de tabuleiro, placar e turno para todos os clientes
            json_message = json.dumps({"tabuleiro": self.tabuleiro, "placar": self.placar, "turn": self.turn})
            sendMessageToClients(f"1{json_message}|",self.clients)

            #Pede uma peça para o cliente da vez
            self.clients[self.turn].send(f"0Escolha uma peça|".encode("utf-8"))

            #Espera ocupada
            while(len(self.move) == 0):
                time.sleep(0.1)

            #Pega a peça escolhida
            i1, j1 = int(self.move[0]),int(self.move[1])
            self.move = []

            # Vira a peça escolhida
            self.tabuleiro[i1][j1] = -self.tabuleiro[i1][j1]

            #Da os dados da de tabuleiro, placar e turno para todos os clientes
            json_message = json.dumps({"tabuleiro": self.tabuleiro, "placar": self.placar, "turn": self.turn})
            sendMessageToClients(f"1{json_message}|",self.clients)

            #Pede uma peça para o cliente da vez
            self.clients[self.turn].send(f"0Escolha uma peça|".encode("utf-8"))

            #Espera ocupada
            while(len(self.move) == 0):
                time.sleep(0.1)

            #Pega a peça escolhida
            i2, j2 = int(self.move[0]),int(self.move[1])
            self.move = []

            # Vira a peça escolhida
            self.tabuleiro[i2][j2] = -self.tabuleiro[i2][j2]

            #Da os dados da de tabuleiro, placar e turno para todos os clientes
            json_message = json.dumps({"tabuleiro": self.tabuleiro, "placar": self.placar, "turn": self.turn})
            sendMessageToClients(f"1{json_message}|",self.clients)
            time.sleep(0.5)

            #Mensagem de se as peças são iguais
            sendMessageToClients(f"0Pecas escolhidas --> ({i1}, {j1}) e ({i2}, {j2})|",self.clients)
            time.sleep(0.5)

            # Pecas escolhidas sao iguais?
            if self.tabuleiro[i1][j1] == self.tabuleiro[i2][j2]:

                sendMessageToClients(f"0Pecas casam! Ponto para o jogador {self.turn + 1}.|",self.clients)
                
                incrementaPlacar(self.placar, self.turn)
                paresEncontrados = paresEncontrados + 1
                removePeca(self.tabuleiro, i1, j1)
                removePeca(self.tabuleiro, i2, j2)

                time.sleep(3)
            else:

                sendMessageToClients(f"0Pecas nao casam!|",self.clients)
                
                time.sleep(3)

                fechaPeca(self.tabuleiro, i1, j1)
                fechaPeca(self.tabuleiro, i2, j2)
                self.turn = (self.turn + 1) % self.nJogadores

        # Verificar o vencedor, imprimir e resetar
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
            sendMessageToClients(f"0Jogador {vencedores[0] + 1} foi o vencedor!|",self.clients)
        time.sleep(3)
        print("Jogo finalizado")
        sendMessageToClients(f"4|",self.clients)
        self.reset()
        receive(self.socket,self.clients,self.ids,self)

# Função padrão que manda uma mensagem para todos os clientes
def sendMessageToClients(message,clients):
    for client in clients:
        try:
            client.send(message.encode("utf-8"))
        except:
            pass

# Função que recebe a mensagem do cliente e retorna a para todos os outros clientes
def clientThread(conn:socket.socket, game: gameInstance):
    connIndex = game.clients.index(conn)
    clientId = game.ids[connIndex]
    conn.send(f"3{clientId}|".encode("utf-8"))
    conn.send(f"0Bem vindo ao jogo, jogador {clientId+1}!\nSinta-se a vontade para usar o chat enquanto os jogadores se conectam!|".encode('utf-8'))
    while conn in game.clients:
        try:
            message = conn.recv(1024)
            if not message:
                break
            if(game.gameState == 0):
                if message != "":
                    message_to_send = f"0Jogador {clientId+1}: {message.decode('utf-8')}|"
                    sendMessageToClients(message_to_send,game.clients)
            else:
                move = message.decode('utf-8').split(' ')
                if(game.turn == clientId and len(move) > 1):
                    game.move = message.decode('utf-8').split(' ')
                else:
                    conn.send("0Não é sua vez|".encode('utf-8'))

        except:
            if conn in game.clients:
                game.clients.remove(conn)
                sendMessageToClients(f"0Jogador {clientId} Deixou o jogo!\nAguardando conexões... {len(game.clients)}/{game.nJogadores}|",game.clients)
                game.ids.remove(clientId)      
            break

#Função que aguarda a conexão dos clientes e, quando todos se conectarem, inicia o jogo
def receive(server : socket.socket, game: gameInstance):
    while len(game.clients) < game.nJogadores:
        print(f"Aguardando conexões... {len(game.clients)}/{game.nJogadores}")
        sendMessageToClients(f"0Aguardando conexões... {len(game.clients)}/{game.nJogadores}|",game.clients)
        conn, address = server.accept()
        game.clients.append(conn)
        game.ids.append(len(game.clients)-1)
        print(f"Conectado com {address}\nId: {len(game.clients)-1}")
        sendMessageToClients(f"0Jogador {game.ids[len(game.ids)-1]+1} entrou no jogo!|",game.clients)
        thread = threading.Thread(target=clientThread, args=(conn,game.clients,game.ids,game))
        thread.start()
    print("Todos os jogadores conectados!\nIniciando jogo...")
    sendMessageToClients("0Todos os jogadores conectados!\nIniciando jogo...|",game.clients)
    time.sleep(3)
    game.play()
    
#Inicializador do servidor           
def main():
    ##
    # Parametros da partida
    ##

    # Tamanho (da lateral) do tabuleiro. NECESSARIAMENTE PAR E MENOR QUE 10!
    dim = int(input("Digite o tamanho do tabuleiro (Menor que 10, maior que 2 e par!): "))
    while(dim < 2 or int(dim) > 10 or int(dim) % 2 != 0):
        print("Tamanho invalido!")
        dim = int(input("Digite o tamanho do tabuleiro (Menor que 10, maior que 2 e par!): "))


    # Numero de jogadores
    nJogadores = int(input("Digite o numero de jogadores (Min: 1 jogador): "))
    while(nJogadores < 1):
        print("Numero invalido!")
        nJogadores = int(input("Digite o numero de jogadores: "))
    
    ##
    # Programa principal
    ##

    # Cria o socket do servidor
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Define o IP e a porta do servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address=s.getsockname()[0]
    s.close()
    print(f"IP privado do servidor: {ip_address}")
    port = 25542
    print(f"Servidor aberto na porta: {port}")
    tcp_server.bind((ip_address, port))
    tcp_server.listen(nJogadores)
    game = gameInstance(dim,nJogadores,tcp_server)
    receive(tcp_server,game)

main()
