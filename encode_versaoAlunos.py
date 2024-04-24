#importe as bibliotecas
from suaBibSignal import *
from math import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

#funções caso queriram usar para sair...
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

tecla_por_freq = {
     "0": [941, 1336],
     "1": [679, 1209],
     "2": [679, 1336],
     "3": [679, 1477],
     "4": [770, 1209],
     "5": [770, 1336],
     "6": [770, 1477],
     "7": [852, 1209],
     "8": [852, 1336],
     "9": [852, 1477],
     "X": [941, 1209],
     "#": [941, 1477],
     "A": [679, 1633],
     "B": [770, 1633],
     "C": [852, 1633],
     "D": [941, 1633],
}

teclas_validas = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "X", "#", "A", "B", "C", "D"]

def gerar_senoides(freqs, lista_tempo):
    senoide1 = []
    senoide2 = []
    
    for t in lista_tempo:
        senoide1.append(sin(2*pi*freqs[0]*t))
        senoide2.append(sin(2*pi*freqs[1]*t))

    signal = np.array(senoide1) + np.array(senoide2)
    return signal

def main():
    #********************************************instruções*********************************************** 
    # Seu objetivo aqui é gerar duas senoides. Cada uma com frequencia corresposndente à tecla pressionada, conforme tabela DTMF.
    # Então, inicialmente peça ao usuário para digitar uma tecla do teclado numérico DTMF.
    # De posse das duas frequências, agora voce tem que gerar, por alguns segundos suficientes para a outra aplicação gravar o audio, duas senoides com as frequencias correspondentes à tecla pressionada.
    # Essas senoides têm que ter taxa de amostragem de 44100 amostras por segundo, sendo assim, voce tera que gerar uma lista de tempo correspondente a isso e entao gerar as senoides
    # Áudio terá duração de 2 segundos. Sendo assim, serão 88200 amostras
    # Lembre-se que a senoide pode ser construída com A*sin(2*pi*f*t).
    # O tamanho da lista tempo estará associada à duração do som. A intensidade é controlada pela constante A (amplitude da senoide). Construa com amplitude 1 (A = 1).4
    # Some as duas senoides. A soma será o sinal a ser emitido.
    # Utilize a funcao da biblioteca sounddevice para reproduzir o som. Entenda seus argumentos.
    # Você pode gravar o som com seu celular ou qualquer outro microfone para o lado receptor decodificar depois. Ou reproduzir enquanto o receptor já capta e decodifica.
    # construa o gráfico do sinal emitido e o gráfico da transformada de Fourier. Cuidado, como as frequencias sao relativamente altas, voce deve plotar apenas alguns pontos (alguns periodos) para conseguirmos ver o sinal
    print("Inicializando encoder")
    tecla = ''

    while tecla not in teclas_validas:
        tecla = input(str(("Digite uma das teclas do teclado numérico DTMF [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, X, #, A, B, C, D]: "))).upper()
        # Verificação se a tecla é válida
        if tecla in tecla_por_freq:
            freqs = tecla_por_freq[tecla]
        else:
            print("Tecla inválida.")
    
    # Taxa de amostragem
    taxa_amostragem = 44100
    # Duração do áudio em segundos
    duracao_audio_seg = 2
    # Número total de amostras
    num_amostras = int(taxa_amostragem * duracao_audio_seg)
    # Lista de tempo
    lista_tempo = np.linspace(0, duracao_audio_seg, num_amostras)

    print("Gerando Tons base")
    # Gerar as senoides
    signal = gerar_senoides(freqs, lista_tempo)

    print("Executando as senoides (emitindo o som)")
    print("Gerando Tom referente ao símbolo : {}".format(tecla))
    # Reproduzir o som utilizando a função da biblioteca sounddevice
    sd.play(signal, 44100)
    # aguarda fim do audio
    sd.wait()

    amostras_plot = 1000  # número de amostras para plotar

    #Exibe gráficos
    plt.figure(figsize=(7,7))
    # Gráfico do sinal no domínio do tempo
    plt.subplot(2, 1, 1)
    plt.plot(lista_tempo[:amostras_plot], signal[:amostras_plot])
    plt.title("Sinal x Tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Sinal")
    # plt.grid(True)

    # Gráfico do sinal (transformada de Fourier) no domínio da frequência 
    # Calcular a FFT do sinal
    fft_result = np.fft.fft(signal)

    # Calcular as frequências correspondentes
    frequencias = np.fft.fftfreq(len(signal), 1/taxa_amostragem)

    plt.subplot(2, 1, 2)
    plt.plot(frequencias[:len(frequencias)//2], np.abs(fft_result[:len(frequencias)//2]))
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude')
    plt.title('Espectro de Frequência')
    # plt.grid(True)

    plt.tight_layout()
    plt.show()

    print("Salvando em txt")
    np.savetxt('sinal_gerado.txt', signal)

if __name__ == "__main__":
    main()
