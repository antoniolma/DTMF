
#Importe todas as bibliotecas
from suaBibSignal import *
import peakutils    #alternativas  #from detect_peaks import *   #import pickle
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time
from statistics import mean

# ============================================================================================================================================================

frequenciasTeclas = {
    
    '1' : [679, 1209],  '2' : [679, 1336],  '3' : [679, 1477],  'A' : [679, 1633], 
    '4' : [770, 1209],  '5' : [770, 1336],  '6' : [770, 1477],  'B' : [770, 1633],
    '7' : [852, 1209],  '8' : [852, 1336],  '9' : [852, 1477],  'C' : [852, 1633],
    'X' : [941, 1209],  '0' : [941, 1336],  '#' : [941, 1477],  'D' : [941, 1633]
}

freqBaixas = [679, 770, 852, 941]
freqAltas = [1209, 1336, 1477, 1633]

# ============================================================================================================================================================

#funcao para transformas intensidade acustica em dB, caso queira usar
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def trataDados(audio):
    output = []
    filtro = 1e-4
    for dado in audio:
        # if abs(dado[0]) > filtro and abs(dado[1]) > filtro:
        #   output.append((dado[0], dado[1]))
        if abs(dado[0]) > filtro:
            output.append(dado[0])
    return output

def encontraPicos(amplitudes, frequencias):
    # Amplitudes e frequencias combinadas -> output: [(amplitude[0], frequencia[0]), ...]
    num_picos = 10
    picos = []

    for i in range(len(amplitudes)):
        longeDePico = checaDistanciaPicos(frequencias[i], picos)
        if longeDePico:
            novoMaioresAmp = chechaMaioresAmplitudes(amplitudes[i], frequencias[i], picos, num_picos=num_picos)
            if novoMaioresAmp and 600 < frequencias[i] < 1750:
                if len(picos) < num_picos:
                    picos.append((amplitudes[i], frequencias[i]))
                else:
                    picos[num_picos-1] = (amplitudes[i], frequencias[i])
                picos.sort(reverse=True)

    # Organiza a lista de maior para menor baseando apenas no primeiro argumento da tupla, ou seja, a amplitude
    picos.sort(reverse=True)

    return picos[:num_picos]


    # num_picos = 20        # numero de valores que queremos registrar
    # maiores_amp = []
    # freq_picos = []
    # for i in range(amplitudes):
    #     # Verifica se é um pico
    #     if amplitudes[i] > amplitudes[i - 1] and amplitudes[i] > amplitudes[i + 1]:
    #         longeDePico = checaDistanciaPicos(frequencias[i], freq_picos)
    #         novoMaioresAmp = chechaMaioresAmplitudes(amplitudes[i], maiores_amp)
    #         if longeDePico and novoMaioresAmp and frequencias[i] < 1750 and frequencias[i] > 600:
    #             maiores_amp.append(amplitudes[i])
    #             freq_picos.append(frequencias[i])
    # return maiores_amp, freq_picos


def combinaDados(amplitudes, frequencias):
    dados_combinados = []
    for i in range(amplitudes):
        dados_combinados.append(amplitudes[i], frequencias[i])
    return dados_combinados

# Checa se o pico está a pelo menos 5 Hz de distância de algum outro pico
# Se estiver muito próximo de outro pico, menos de 5 Hz, então retorna False
def checaDistanciaPicos(frequencia, picos, distancia_minima = 10.0):
    # Se estiver vazia, pode registrar
    if len(picos) == 0:
        return True
    
    freq_pico = picos[-1][1]
    if abs(frequencia - freq_pico) < distancia_minima:
        return False
    
    return True

# Verifiica se é uma das 5 maiores amplitudes, se sim avisa e manda trocar
def chechaMaioresAmplitudes(amplitude, frequencia, picos, num_picos):
    
    # Tendo menos q a quantidade que queremos, ele entra na lista
    if len(picos) < num_picos:
        return True
    # Se a amplitude for maior que a amplitude do último da lista
    elif amplitude > picos[num_picos-1][0]:
        # Novo último da lista = (amplitude, frequencia)
        return True
    return False

# 
def filtraFrequenciasDePico(freq_pico):
    # Ex. 1: [862.1167945197724, 1646.1063775582415, 1656.6365669318086, 873.3263509496985, 2448.43887111840]
    # Ex. 2: [681.9509304589512, 692.4476925464525, 2599.810945414016, 1643.928384994145, 3954.909070387562]
    agrupamento = [0, 0]
    procuraBaixo = True
    procuraAlto = True

    for freq in freq_pico:
        if freq != 0:
            print(f"\nfrequencia = {freq}")
            # Procura frequencia baixa
            if procuraBaixo == True:
                for fBaixa in freqBaixas:
                    print(f"fBaixa = {fBaixa}")
                    if abs(fBaixa - freq) < 80:
                        agrupamento[0] = fBaixa
                        procuraBaixo = False
                        print(f"Achou Baixo")
                        break
                        

            # Procura frequencia alta
            if procuraAlto:
                for fAlta in freqAltas:
                    print(f"fAlto = {fAlta}")
                    if abs(fAlta - freq) < 80:
                        agrupamento[1] = fAlta
                        procuraAlto = False
                        print(f"Achou Alto")
                        break
            
            # Se ja achou as frequencias, pode sair do for
            if agrupamento[0] != 0 and agrupamento[1] != 0:
                break

    return agrupamento

# Recebe a lista de frequencias dos picos e devolve qual a tecla
def identificaTecla(freqFiltradas):
    for tecla, frequencias in frequenciasTeclas.items():
        if frequencias == freqFiltradas:
            return tecla
    return 'Tecla não identificada'

# ============================================================================================================================================================

def main():

    #*****************************instruções********************************
 
    # declare um objeto da classe da sua biblioteca de apoio (cedida)   
    # algo como:
    signal = signalMeu() 
       
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    numChannels = 1
    freqDeAmostragem = 48000
    
    sd.default.samplerate = freqDeAmostragem  #taxa de amostragem
    sd.default.channels = numChannels  #numCanais # o numero de canais, tipicamente são 2. Placas com dois canais. Se ocorrer problemas pode tentar com 1. No caso de 2 canais, ao gravar um audio, terá duas listas.
    #Muitas vezes a gravação retorna uma lista de listas. Você poderá ter que tratar o sinal gravado para ter apenas uma lista.

    duration =  2  # #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic   

    #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisições) durante a gravação. Para esse cálculo você deverá utilizar a taxa de amostragem e o tempo de gravação
    numAmostras = duration * freqDeAmostragem  # Ex.: 2 segundos * 48000 amostras/segundo = 96000 amostras

    #faca um print na tela dizendo que a captação comecará em n segundos. e então 
    #use um time.sleep para a espera.
    #A seguir, faca um print informando que a gravacao foi inicializada

    #para gravar, utilize
    while True:
        print('\nA captação começará em: 3 segundos')
        time.sleep(3)
        print('\nA gravação começou')

        audio = sd.rec(int(numAmostras), freqDeAmostragem, channels=numChannels)
        sd.wait()

        playback = input("\nDeseja escutar a gravação? (y/n)  ->  ")
        if playback == 'y':
            sd.play(audio, freqDeAmostragem)
            sd.wait()

        refazer = input("\nRefazer gravação? (y/n)  ->  ")
        if refazer == 'n':
            break

    print("\n...     FIM")
    print('='*50)
    print()

    # analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, ou uma lista, ou ainda uma lista de listas (isso dependerá do seu sistema, drivers etc...).
    # extraia a parte que interessa da gravação (as amostras) gravando em uma variável "dados". Isso porque a variável audio pode conter dois canais e outas informações). 
    dados = trataDados(audio)
    # print(dados)
    print(len(dados))
    
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    listaTempo = np.linspace(0, duration, len(dados))
  
    # plot do áudio gravado (dados) vs tempo! Não plote todos os pontos, pois verá apenas uma mancha (freq altas) .
    plt.plot(listaTempo, dados)
    plt.xlabel('Tempo [s]')
    plt.ylabel('Audio gravado')
    plt.show()
    
    ## Calcule e plote o Fourier do sinal audio. como saída tem-se a amplitude e as frequências.
    freqFourier, ampliFourier = signal.calcFFT(dados, freqDeAmostragem)
    plt.plot(freqFourier, ampliFourier)
    plt.xlabel('Frequencia das Amostras [Hz]')
    plt.ylabel('Amplitude')
    plt.show()

    #Agora você terá que analisar os valores xf e yf e encontrar em quais frequências estão os maiores valores (picos de yf) de da transformada.
    #Encontrando essas frequências de maior presença (encontre pelo menos as 5 mais presentes, ou seja, as 5 frequências que apresentam os maiores picos de yf). 
    #Cuidado, algumas frequências podem gerar mais de um pico devido a interferências na tranmissão. Quando isso ocorre, esses picos estão próximos. Voce pode desprezar um dos picos se houver outro muito próximo (5 Hz). 
    #Alguns dos picos  (na verdade 2 deles) devem ser bem próximos às frequências do DTMF enviadas!
    #Para descobrir a tecla pressionada, você deve encontrar na tabela DTMF frquências que coincidem com as 2 das 5 que você selecionou.
    #Provavelmente, se tudo deu certo, 2 picos serao PRÓXIMOS aos valores da tabela. Os demais serão picos de ruídos.
    picos = encontraPicos(ampliFourier, freqFourier)
    
    ampliPicos = []
    freqPicos = []

    for i in range(len(picos)):
        ampliPicos.append(picos[i][0])
        freqPicos.append(picos[i][1])

    print("\nMaiores picos:")
    print(ampliPicos)
    print("Frequencia desses picos:")
    print(freqPicos) 
    
    #printe os picos encontrados! 
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print o valor tecla!!!
    #Se acertou, parabens! Voce construiu um sistema DTMF
    frequenciasFiltradas = filtraFrequenciasDePico(freqPicos)
    print(f"\n{frequenciasFiltradas}\n")
    tecla = identificaTecla(frequenciasFiltradas)
    print(tecla)

    #Você pode tentar também identificar a tecla de um telefone real! Basta gravar o som emitido pelo seu celular ao pressionar uma tecla. 

      
    ## Exiba gráficos do fourier do som gravados 
    plt.show()

if __name__ == "__main__":
    main()
