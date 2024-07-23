import re

def parseGameNotation(string):

    Pcord = r'\(-?\d,-?\d\)'
    PbasicFlower = r'[RW][345]'
    PaccentChoice = r'([RWKB],?){4}'
    PharmonyPlant = r'[RWKBLO]' + Pcord
    Pbeginning = r'\d+[GH]'

    Pfull = f'{Pbeginning}.({PbasicFlower}{Pcord}-{Pcord})|({Pcord}-{Pcord}({PharmonyPlant}(-{Pcord})?)?)|{PaccentChoice}'

    moveInfo = {
        'isHost': None,
        'turnNumber': None,
        'type': None, #accentChoice, plant, or arrange.
        'relaventTile': None, #list of accents for accentChoice, code (ex. 'R3') for planting, or cordinate (ex. (2, 1)) for arrange
        'moveCord': None,
        'harmonyBonusTile': None,
        'harmonyBonusCord': None,
        'harmonyBonusExtraCord': None
    }

    if not re.match(f'{Pbeginning}\\.(({PbasicFlower}{Pcord})|({Pcord}-{Pcord}\\+({PharmonyPlant}(-{Pcord})?)?)|({PaccentChoice}))$', string):
        return 'Not a valid notation'

    focusList = re.split(r'\.', string)
    moveInfo['isHost'] = focusList[0][1] == 'H'
    moveInfo['turnNumber'] = int(focusList[0][0])
    print(focusList)

    focusString = focusList[1]
    if re.match(PaccentChoice + '$', focusString):
        moveInfo['type'] = 'accentChoice'

    elif re.match(PbasicFlower + Pcord + '$', focusString):
        moveInfo['type'] = 'plant'

    else:
        moveInfo['type'] = 'arrange'

parseGameNotation('0G.R,W,W,B')
parseGameNotation('4G.(-8,0)-(-7,-3)+B(8,3)-(7,3)')
parseGameNotation('5G.R3(-8,0)')