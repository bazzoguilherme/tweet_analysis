# coding=UTF-8
from string import ascii_lowercase, punctuation
from unidecode import unidecode
import csv
import re
import linecache


# Estrutura de Nodo -- Rtrie
class Node():
    tam_alfabeto = 36

    def __init__(self, lista_nodos=[], val=0):
        self.lista_nodos = [None] * self.tam_alfabeto
        self.val = val

    # Insere string na Rtrie
    def insere_string(self, str_inserir):
        if len(str_inserir) > 0:
            str_inserir = str_inserir.lower()

            posi_char = ord(str_inserir[0]) - (97 if ord(str_inserir[0]) > 96 else 22)
            
            if self.lista_nodos[posi_char] == None:
                self.lista_nodos[posi_char] = Node()

            if len(str_inserir) == 1:
                self.lista_nodos[posi_char].val += 1
            else:
                self.lista_nodos[posi_char].insere_string(str_inserir[1:])

    def imprime_RTrie(self, out_writer ,palavra=''):
        if self != None and self.val > 0:
            # print(palavra + " " + str(self.val))
            out_writer.writerow([palavra])
        for i in range(self.tam_alfabeto):
            if self.lista_nodos[i] != None:
                self.lista_nodos[i].imprime_RTrie(out_writer, palavra + chr( (97 if i < 26 else 22) + i))
                # if self.lista_nodos[i].val > 0:
                # print(str(self.lista_nodos[i].val) + "," + palavra + chr(97+i))
                # file.write('(' + palavra + chr(97+i) + " "  +  str(self.lista_nodos[i].val)+ '), ')

    # realiza busca da palavra e retorna a quantidade de vezes que está inserida
    def busca_palavra(self, palavra=""):
        if len(palavra) == 0:
            return self.val
        else:
            posi_char = ord(palavra[0]) - (97 if ord(palavra[0]) > 96 else 22)
            if self.lista_nodos[posi_char] == None:
                return 0
            else:
                return self.lista_nodos[posi_char].busca_palavra(palavra[1:])

    # Realiza a busca de palavras em relação à um prefixo em comum
    def busca_nodo_prefixo(self, palavra=""):
        if len(palavra) == 0:
            return self
        else:
            posi_char = ord(palavra[0]) - (97 if ord(palavra[0]) > 96 else 22)
            if self.lista_nodos[posi_char] == None:
                return None
            else:
                return self.lista_nodos[posi_char].busca_nodo_prefixo(palavra[1:])

    def lista_palavras(self, prefixo, out_writer):
        nodo = self.busca_nodo_prefixo(prefixo)
        if nodo != None:
            nodo.imprime_RTrie(out_writer, prefixo)
        else:
            print("\nPrefixo não encontrado")



# Estrutura da palavra, contém a palavra, quantidade de vezes que ela aparece, a média dos valores associados à ela e os índices dos tweets em que aparece
class WordValue:
    def __init__(self, palavra, value):
        self.palavra = palavra
        self.cont = 1
        self.soma = value
        self.value = value
        self.tweet_id = []

    def add_value_media(self, value):
        self.soma += value
        self.cont += 1
        self.value = self.soma / self.cont

    def new_tweet_index(self, id, value):
        if id not in self.tweet_id:
            self.tweet_id.append((id, value))

    def retorna_indices(self, value):
        l_index = []
        if value is not None:
            for i, v in self.tweet_id:
                if v == value:
                    l_index.append(i)
        else:
            for i, v in self.tweet_id:
                l_index.append(i)

        return l_index



# Estrutura da Hash Table, estrutura é uma tabela (aka lista) contendo as estruturas das palavras (WordValue)
class HashTable:
    const_a = 37
    tax_max = 1/2

    # Inicialização da tabela
    def __init__(self, tam=503):
        self.tam_tabela = tam
        self.tabela = [None] * self.tam_tabela
        self.quant_elementos = 0
        self.tax_ocupacao = 0 # Taxa de Ocupação atual da tabela

    # Adiciona elemento à tabela
    def add_tabela(self, palavra, value, index_tweet):
        # Calcula a posição na tabela hash
        pos = int(self.poly_func_hash(palavra))

        # Caso já exista algo na posição atual e não for o elemento que estou querendo, realiza Linear Probing até encontrar a primeira posição vazia ou
        # a posição contendo o elemento que quero
        if self.tabela[pos] is not None and self.tabela[pos].palavra != palavra:
            pos = int(self.linear_prob(pos, palavra))

        if self.tabela[pos] == None:
            self.quant_elementos += 1
            self.tabela[pos] = WordValue(palavra, value)
        else:
            self.tabela[pos].add_value_media(value)

        self.tabela[pos].new_tweet_index(index_tweet, value)

        # Gera nova taxa de ocupação da tabela
        self.nova_tax_ocup()

    def add_tabela_rehash(self, palavra_struct):
        # Enconta posiçao para inserir estrutura que já contém palavra (aqui não é necessário conferir se a palavra já está inserida
        # porque ela não deve estar, já que estamos inserindo as estruturas do "zero", com elas já feitas.
        pos = int(self.poly_func_hash(palavra_struct.palavra))
        if self.tabela[pos] is not None:
            pos = int(self.linear_prob(pos, palavra_struct.palavra))
        self.tabela[pos] = palavra_struct
        self.nova_tax_ocup()

    # Realiza o cálculo da função hash polinomial
    def poly_func_hash(self, palavra):
        soma = 0
        for i in range(len(palavra)):
            soma += ord(palavra[i]) * pow(self.const_a, i)
        return soma % self.tam_tabela

    # Caso houve colisão no endereço primeiramente calculado, realiza a 'Linear Probing' para encontrar o próximo endereço livre
    def linear_prob(self, pos, palavra):
        new_pos = pos
        # se a posição não é vazia e o elemento que está lá não é o que eu quero continua o laço
        while True:
            # Se a posição é vazia, retorno nova posição, porque quero adiconar nova palavra na tabela
            if self.tabela[new_pos] is None:
                break
            # Caso a posição não for vazia, confiro se a posição atual contém o conteúdo de interesse (palavra que quero), para "incrementar" o valor
            elif self.tabela[new_pos].palavra == palavra:
                break

            new_pos += 1
            if new_pos == self.tam_tabela:
                new_pos = 0

            if new_pos == pos:
                break


        return new_pos

    def busca_palavra(self, palavra):
        pos = int(self.poly_func_hash(palavra))

        # Caso já exista algo na posição atual e não for o elemento que estou querendo, realiza Linear Probing até encontrar a primeira posição vazia ou
        # a posição contendo o elemento que quero
        if self.tabela[pos] is not None and self.tabela[pos].palavra != palavra:
            pos = int(self.linear_prob(pos, palavra))

        if self.tabela[pos] is None:
            return 0
        else:
            return self.tabela[pos].value

    def nova_tax_ocup(self):
        self.tax_ocupacao = self.quant_elementos / self.tam_tabela

	# Verifica se a palavra está na Tabela Hash, retornando sua lista de postings caso esteja, ou uma lista vazia caso contrário
    def indice_tweets(self, palavra, value):
        pos = int(self.poly_func_hash(palavra))

        if self.tabela[pos] == None:				#Se posição calculada esta vazia, palavra não está.
            return []
        if self.tabela[pos].palavra == palavra:  	#Se a palavra está na posição indicada pela função,
            # return self.tabela[pos].tweet_id			#retorna a lista de postings da palavra
            return self.tabela[pos].retorna_indices(value)
        else:
            pos = self.linear_prob(pos, palavra)	#Verifica se a palavra está nas próximas posições
            if self.tabela[pos].palavra == palavra:	  #retorna a lista de postings se encontra a palavra ou
                # return self.tabela[pos].tweet_id
                return self.tabela[pos].retorna_indices(value)
            else:
                return []							  # ,caso não, retorna lista vazia




""" Realiza ReHash
 Recebe tabela atual e cria nova com o tamanho com pelo menos o sobro da tabela anterior
 Para os elementos que já estavam na tabela anterior, eles são inseridos na nova tabela na ordem que se encontram na tabela hash anterior
"""
def reHash(tabela_atual):
    # Encontra novo tamanho de tabela
    p = find_next_size(tabela_atual.tam_tabela)
    # Cria nova tabela com tamanho atulizado
    new_table = HashTable(p)
    # atualiza quantidade de elementos em relação à tabela anterios
    # como está fazendo rehash terá a mesma quantidade de elementos
    new_table.quant_elementos = tabela_atual.quant_elementos
    # Para todas as estrutudas de palavra que estão inseridas na tabela, faz a inserção delas na nova tabela hash
    for pal in tabela_atual.tabela:
        if pal is not None:
            new_table.add_tabela_rehash(pal)

    del tabela_atual
    return new_table


# função que encontra o próximo primo para criar a tabela hash
def find_next_size(p_atual):
    prime_list = [503, 1051, 2503, 5303, 10607, 21221, 49999, 99991]
    for p in prime_list:
        if p > p_atual:
            return p
    # p = p_atual * 2 + 1
    # while(True):
    #     for i in range(2, p):
    #         if (p % i) == 0:
    #             break
    #     else:
    #         return p
    #     p += 1


# Printa a tabela hash na tela
def print_hash(tabela_hash):
    for pal in tabela_hash.tabela:
        if pal is not None:
            print(pal.palavra, pal.cont, pal.value, pal.tweet_id)

def arruma_palavra(palavra):
    translator = str.maketrans(punctuation, ' ' * len(punctuation))
    palavra = palavra.lower()
    palavra = palavra.translate(translator)
    palavra_tam_m2 = palavra.split()
    palavra_arrumada = [pal for pal in palavra_tam_m2 if len(pal)>2]
    palavra_arrumada = ' '.join(palavra_arrumada)
    return palavra_arrumada


def leitura_arquivo(nome_arq, r_trie, hash_t, name_new_file, flag_file, cont_linha):
    if not flag_file:
        aux_file = open(name_new_file, 'a', encoding='utf-8', newline='')
        file_writer = csv.writer(aux_file)

    else:
        aux_file = open(name_new_file, 'w+', encoding='utf-8', newline='')
        file_writer = csv.writer(aux_file)


    nome_arq = nome_arq.replace(" ", '')
    if '.' not in nome_arq:
        nome_arq += '.csv'
    try:
        csvFile = open(nome_arq, 'r', encoding='utf-8', errors='ignore')

        line = csv.reader(csvFile)
        for row in line:
            # print(row[0])
            file_writer.writerow(row)
            tweet = row[0]
            tweet = unidecode(tweet)
            tweet = arruma_palavra(tweet)
            palavras = tweet.split()
            for p in palavras:
                r_trie.insere_string(p)
                hash_t.add_tabela(p, int(row[1]), cont_linha)

            if hash_t.tax_ocupacao >= hash_t.tax_max:
                hash_t = reHash(hash_t)

            cont_linha += 1

        csvFile.close()
        aux_file.close()
        return hash_t, cont_linha

    except:
        print("Erro na leitura do arquivo" + str(nome_arq) + ".\nLembre que a leitura é de um arquivo CSV")
        csvFile.close()
        aux_file.close()
        return hash_t, cont_linha

def encontra_tweet_linha(nome_arq, list_index, out_word_writer):
    csvFile =  open(nome_arq, 'r', encoding='utf-8')
    cont = 1
    # Le cada linha do arquivo até que não há mais indices para encontrar no aquivo
    while(len(list_index) != 0):
        line = csvFile.readline()
        # line = csv.reader(csvFile)
        if cont in list_index:
            out_word_writer.writerow([line.replace("\n", "")])
            list_index.remove(cont)

        cont += 1

    csvFile.close()


def encontra_tweets(palavra, hash_t, nome_arq, out_word_writer, value):
    # Encontra a lista dos indices dos tweets de determinada palavra
	indices = hash_t.indice_tweets(palavra, value)
	encontra_tweet_linha(nome_arq, indices, out_word_writer)
	
def analisa_sentimentos(nome_arq, hash_t):
    out_file = open("saida_sentimentos.csv", 'w+', encoding='utf-8', newline='')
    out_file_writer = csv.writer(out_file)

    nome_arq = nome_arq.replace(" ", '')
    if '.' not in nome_arq:
        nome_arq += '.csv'
    try:
        with open(nome_arq, 'r', encoding='utf-8', errors='ignore') as csvFile:
            line = csv.reader(csvFile)
            for row in line:
                soma_tweet = 0
                tweet = row[0]
                tweet = unidecode(tweet)
                tweet = arruma_palavra(tweet)
                palavras = tweet.split()
                # Calcula escore para cada palavra
                for p in palavras:
                    soma_tweet += hash_t.busca_palavra(p)

                # Verifica escore
                if soma_tweet > 0.1:
                    sentimento_out = 1
                elif soma_tweet < -0.1:
                    sentimento_out = -1
                else:
                    sentimento_out = 0

                # Salva no arquivo de saida
                out_file_writer.writerow([row[0], sentimento_out])
    except:
        print("Erro no arquivo " + str(nome_arq) + ". Tente com algum csv compatível.")

    out_file.close()


def print_commands():
    print("Comandos: ")
    print("- le_arq 'nomearq.csv' -> realiza a leitura de arquivo (CSV), dado que recebe um nome de arquivo para tal operação")
    print("- analisar 'nomearq.csv' -> realiza a calculo do sentimento dos tweets de um arquivo (CSV)")
    print("- pref 'prefixo' -> encontra todas as palavras baseadas em um radical em comum ('prefixo')")
    print("- word 'palavra' valor(opcional) -> encontra os tweets com a palavra dada e gera um arquivo CSV com os tweets")
    print("- help -> lista as funcionalidades novamente")
    print("- close -> encerra programa")



def main():
    # primeiramente cria as estruturas que serão usadas no programa
    r_trie = Node()
    hash_t = HashTable()

    flag_new_file = True
    file_app_name = "file_aux.csv"
    linha = 1

    # Imprime janela informativa na tela
    print_commands()
    while(True):
        command = input(">> ")

        if command == "close":
            break

        elif command == "help":
            print_commands()

        elif "le_arq " in command:
            hash_t, linha = leitura_arquivo(command[command.find(' ') + 1:], r_trie, hash_t, file_app_name, flag_new_file, linha)
            flag_new_file = False

        elif "analisar " in command:
            if flag_new_file:
                print("Nenhum arquivo de tweets analisado ainda, por favor insira algum.")
            else:
                analisa_sentimentos(command[command.find(' ') + 1:], hash_t)
                print("\nAnalise realizada, arquivo com os valores pode ser encontrado em: saida_sentimentos.csv")

        # Comando para procurar prefixos
        elif "pref " in command:
            if flag_new_file:
                print("Nenhum arquivo de tweets analisado ainda, por favor insira algum.")
            else:
                prefix = command[command.find(' ') + 1:]
                file_pref = "pref_" + prefix + ".csv"
                out_pref = open(file_pref, 'w+', newline='')
                out_pref_writer = csv.writer(out_pref)

                r_trie.lista_palavras(prefix, out_pref_writer)
                print("\nArquivo contendo as palavras com o prefixo '"+ prefix +"' em : pref_" + prefix +".csv ")

                out_pref.close()

        # Comando para procurar tweets para ocorrencia de determinada palavra
        elif "word " in command:
            if flag_new_file:
                print("Nenhum arquivo de tweets analisado ainda, por favor insira algum.")
            else:
                cmd = command.split()
                if len(cmd) > 1:
                    word = cmd[1]
                if len(cmd) > 2:
                    val = int(cmd[2])
                    if val > 0.1:
                        val = 1
                    elif val < -0.1:
                        val = -1
                    else:
                        val = 0
                else:
                    val = None

                file_word = "tweets_" + word + ".csv"
                out_word = open(file_word, 'w+', newline='')
                out_word_writer = csv.writer(out_word)

                encontra_tweets(word, hash_t, file_app_name, out_word_writer, val)

                print("\nArquivo contendo os tweets para a palavra '" + word + "' em : tweets_" + word + ".csv ")

                out_word.close()

        else:
            print("Instrução Incorreta, tenta uma instrução válida!\n")
            # print_commands()

    print("\nPrograma encerrado com sucesso.")




if __name__ == "__main__":
    main()
