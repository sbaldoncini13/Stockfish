import chess.pgn
import pandas as pd
from collections import Counter
import re


eco_lines = """
A00              Aperturas Irregulares
A01              Ataque Larsen
A02-A03                Apertura Bird
      A03                Variante Holandesa
A04-A09                Ataque Indio de Rey
A10              Apertura Inglesa
A11-A12                Apertura Reti
A13-A39                Apertura Inglesa
      A17                Variante Erizo
      A20-A29                  Siciliana Invertida
      A30-A31                  Variante Erizo
      A32-A39                  Variante Simetrica
A40              Gambito Englund
A41-A42                Defensa Moderna
A43-A44                Defensa Benoni Antigua
A45              Ataque Trompovsky
A46              Partida de Peon de Dama
A47              Defensa India de Dama
A48-A49                India de Rey, Ataque Torre
A50              Defensa India de Dama
A51-A52                Gambito Budapest
      A52                Linea Principal
A53-A55                Defensa India Antigua
A56              Defensa Benoni Checa
A57-A59                Gambito Benko (Volga)
      A58                Aceptado
A60-A79                 Defensa Benoni Moderna
A80-A99                 Defensa Holandesa
      A82                 Gambito Staunton
      A83                 Linea Principal
      A87-A90                   Leningrado
B00               Defensa Nimzowitsch; Defensa Owens
B01               Defensa Escandinava
B02-B05                 Defensa Alekhine
      B03                 Ataque Cuatro Peones
B06               Defensa Moderna
B07-B09                 Defensa Pirc
      B08                 Variante Clasica
      B09                 Ataque Austriaco
B10-B19                 Defensa Caro-Kann
      B11                 Defensa Dos Caballos
      B12                 Variante del Avance
      B14                 Ataque Panov
B20-B99                 Defensa Siciliana
      B21                 Gambito Morra; Ataque Grand Prix
      B22                 Variante Alapin
      B23-B26                   Variante Cerrada
      B29                 Variante Rubinstein
      B30-B31                   Variante Rossolimo
      B32                 Variante Lowenthal
      B33                 Variante Sveshnikov
      B34-B39                   Variante Dragon Acelerado
            B37-B38                      Maroczy Bind
      B40                 Variante del Contrataque
      B41-B49                   Variante Paulsen
            B41-B43                      Sistema Kan
            B44                   Sistema Taimanov
            B45                   Sistema Clasico
            B46-B47                      Sistema Taimanov
      B50                 Variante Kopec
      B51-B52                   Variante Rossolimo
      B53                 Variante Hungara
      B55                 Variante Anti-Dragon
      B57                 Variante Sozin-Benko
      B58                 Variante Boleslavsky
      B60-B69                   Ataque Richter Rauzer
      B70-B79                   Variante Dragon
            B72                   Sistema Clasico
D03               Ataque Torre, Variante Tartakower
D04               Apertura de Peon de Dama
D05               Sistema Colle
D06-D69                 Gambito de Dama
      D07                 Variante Tchigorin
      D08-D09                   Contragambito Albin
      D10-D19                   Defensa Eslava
            D14                   Sistema del Cambio
            D15                   Gambito Geller
            D17                   Sistema Checo
            D18                   Linea Principal
            D19                   Sistema Euwe
      D20-D29                   Aceptado
            D21                   Sistema Borsenko-Furman
      D30-D69                   Rehusado
            D31                   Sistema Alatortsev
            D32-D33                      Sistema Tarrasch
            D34                   Sistema Rubinstein
            D35-D36                      Sistema del Cambio
            D37                   Sistema 5.Af4
            D38-D39                      Defensa Ragozin
            D40-D42                      Defensa Semi-Tarrasch
            D43                   Defensa Semi-Eslava
            D44-D45                      Defensa Anti-Merano
            D46                   Defensa Semi-Eslava
            D47-D49                      Defensa Merano
            D51-D52                      Defensa Cambridge Springs
            D53-D54                      Defensa Ortodoxa
            D55                   Sistema Anti-Tartakower
            D56                   Sistema Lasker
            D57                   Sistema Moderna
            D58-D59                      Sistema Tartakower
            D60-D62                      Defensa Ortodoxa
            D63-D66                      Sistema Blackburne
            D67                   Sistema Capablanca
            D68                   Sistema Blackburne
D70-D99                 Defensa Grunfeld
      D71                 Variante Neo-Grunfeld
      D76                 Variante Ortodoxa del Fianchetto
      D79                 Variante Eslava
      D82-D84                   Sistema Af4
      D85                 Variante del Cambio Moderna
      D87                 Variante del Cambio Botvinnik
      D89                 Variante del Cambio
      D93                 Sistema Ag3
"""


lines = eco_lines.strip().split('\n')


eco_codes = []
openings = []
variations = []


for line in lines:
    # Separar el código ECO del nombre de la apertura o variante
    match = re.match(r"(\w\d{2}(?:-\w\d{2})?)\s+(.*)", line.strip())
    if match:
        eco_code = match.group(1)
        description = match.group(2)
        
        if "-" in eco_code:  # Rango de códigos ECO
            start_code, end_code = eco_code.split("-")
            start_letter = start_code[0]
            start_number = int(start_code[1:])
            end_number = int(end_code[1:])
            
            for i in range(start_number, end_number + 1):
                eco_codes.append(f"{start_letter}{str(i).zfill(2)}")
                if "Variante" in description or "Sistema" in description:
                    openings.append("")
                    variations.append(description.strip())
                else:
                    openings.append(description.strip())
                    variations.append("")
        else:
            eco_codes.append(eco_code)
            if "Variante" in description or "Sistema" in description:
                openings.append("")
                variations.append(description.strip())
            else:
                openings.append(description.strip())
                variations.append("")


eco_df = pd.DataFrame({
    "ECO": eco_codes,
    "Apertura": openings,
    "Variación": variations
})

pgn_file_path = r'I:\ITBA\Stockfish_16_64-bit_4CPU.commented.[1986].pgn'


pgn = open(pgn_file_path)


blancas = []
negras = []
resultado_blancas = []
resultado_negras = []
eco_codes = []


while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break


    blancas.append(game.headers["White"])
    negras.append(game.headers["Black"])
    
    resultado = game.headers["Result"]
    if resultado == "1-0":
        resultado_blancas.append(1.0)
        resultado_negras.append(0.0)
    elif resultado == "0-1":
        resultado_blancas.append(0.0)
        resultado_negras.append(1.0)
    else:
        resultado_blancas.append(0.5)
        resultado_negras.append(0.5)
    
    eco_codes.append(game.headers["ECO"])


df_partidas = pd.DataFrame({
    "Blancas": blancas,
    "Negras": negras,
    "Resultado Blancas": resultado_blancas,
    "Resultado Negras": resultado_negras,
    "ECO": eco_codes
})


df_merged = pd.merge(df_partidas, eco_df, on="ECO", how="left")

# Exportar el DataFrame resultante a un archivo CSV
df_merged.to_csv("I:/ITBA/partidas_con_aperturas_completas.csv", index=False)

