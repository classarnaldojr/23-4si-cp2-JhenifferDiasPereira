import cv2
import mediapipe as mp



# pega as imagens que estão no vídeo
mp_maos = mp.solutions.hands


# identificando o gesto da mão
def detect_gesto(mao_gesto):
    marc_limite = []
    for marc_mao in mao_gesto.landmark:
        marc_limite.append((marc_mao.x, marc_mao.y, marc_mao.z))

    # distância entre os dedos
    dist_1 = ((marc_limite[8][0] - marc_limite[12][0])**2 + (marc_limite[8][1] - marc_limite[12][1])**2)**0.5
    dist_2 = ((marc_limite[8][0] - marc_limite[4][0])**2 + (marc_limite[8][1] - marc_limite[4][1])**2)**0.5

    # identifica o que é: pedra, papel ou tesoura
    if dist_1 < 0.04 and dist_2 < 0.04:
        return "pedra"
    elif dist_1 > 0.06 and dist_2 > 0.06:
        return "tesoura"
    else:
        return "papel"


# pega o video
cap = cv2.VideoCapture('pedra-papel-tesoura.mp4')

# identificando a mão
with mp_maos.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

    gesto_primeiro_jogador = None
    gesto_segundo_jogador = None
    jogador_vencedor = None  
    pontos = [0, 0]

    while True:
        success, img = cap.read()

        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img)

        # perguntar para o prof, não entendi
        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        hls = results.multi_hand_landmarks

        # se as duas mãos forem detectadas
        if hls and len(hls) == 2:
            # menor valor de X da primeira mão detectada
            coord_min1 = min(list(
                map(lambda l: l.x, hls[0].landmark)))
            # menor valor de X da segunda mão detectada
            coord_min2 = min(list(
                map(lambda l: l.x, hls[1].landmark)))
            mao_primeiro_jogador = hls[0] if coord_min1 < coord_min2 else hls[1]
            mao_segundo_jogador = hls[0] if coord_min1 > coord_min2 else hls[1]

            if (detect_gesto(mao_segundo_jogador) != gesto_segundo_jogador or detect_gesto(mao_primeiro_jogador) != gesto_primeiro_jogador):

                print("Primeira mao", coord_min1)
                print("Segunda mao", coord_min2)
                
                # gesto da mao direita
                gesto_segundo_jogador = detect_gesto(mao_segundo_jogador)

                # gesto da mao esquerda
                gesto_primeiro_jogador = detect_gesto(mao_primeiro_jogador)

                # regras para definir o vencedor
                if success:
                    if gesto_primeiro_jogador == gesto_segundo_jogador:
                        jogador_vencedor = 0
                    elif gesto_primeiro_jogador == "papel" and gesto_segundo_jogador == "pedra":
                        jogador_vencedor = 1
                    elif gesto_primeiro_jogador == "papel" and gesto_segundo_jogador == "tesoura":
                        jogador_vencedor = 2
                    elif gesto_primeiro_jogador == "pedra" and gesto_segundo_jogador == "tesoura":
                        jogador_vencedor = 1
                    elif gesto_primeiro_jogador == "pedra" and gesto_segundo_jogador == "papel":
                        jogador_vencedor = 2
                    elif gesto_primeiro_jogador == "tesoura" and gesto_segundo_jogador == "papel":
                        jogador_vencedor = 1
                    elif gesto_primeiro_jogador == "tesoura" and gesto_segundo_jogador == "pedra":
                        jogador_vencedor = 2
                    else:
                        print("Não encontrado")
                else:
                    success = False

                if jogador_vencedor == 1:
                    pontos[0] += 1
                elif jogador_vencedor == 2:
                    pontos[1] += 1

        resultado_por_partida = "Empate" if jogador_vencedor == 0 else f"Jogador {jogador_vencedor} venceu!"
        # textos que aparecem nas telas
        cv2.putText(img, resultado_por_partida, (600, 950),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)
        cv2.putText(img, str("Jogador 1"), (100, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)
        cv2.putText(img, gesto_primeiro_jogador, (100, 300),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)
        cv2.putText(img, str(pontos[0]), (100, 400),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)
        cv2.putText(img, str('Jogador 2'), (1400, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)
        cv2.putText(img, gesto_segundo_jogador, (1400, 300),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)
        cv2.putText(img, str(pontos[1]), (1400, 400),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (226, 43, 138), 2)

        # janela com tamanho limitado
        cv2.namedWindow('Hands', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Hands', 960, 540)
        cv2.imshow('Hands', img)
        #comando de output
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
