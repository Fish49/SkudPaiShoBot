import math
from time import sleep

def sign(x):
    if x < 0:
        return -1
    return 1

def absSum(a, b):
    return abs(a) + abs(b)

def absDiff(a, b):
    return abs(abs(a) - abs(b))

def distance(cord):
    return math.sqrt((cord[0]**2)+(cord[1]**2))

class Tile():
    def __init__(self, isHost, moveNumber, cordinate) -> None:
        self.isHost: bool = isHost
        self.moveNumber: int = moveNumber
        self.cordinate: tuple[int, int] | None = cordinate

    def __str__(self) -> str:
        if self.cordinate == None:
            return ''
        return f'({self.cordinate[0]},{self.cordinate[1]})'

    def isInRange(self, cord, relative=False):
        if (self.cordinate == None):
            if relative:
                return False

            if cord in Board.gates:
                return True

        if not relative:
            cord2 = (cord[0]+self.cordinate[0], cord[1]+self.cordinate[1])
        else:
            cord2 = cord

        if absSum(*cord2) > self.moveNumber:
            return False
        if cord2 == (0, 0):
            return False
        return True

    # def getMoves(self):
    #     moves = []
    #     moveGridSize = (self.moveNumber * 2) + 1
    #     for xi in range(moveGridSize):
    #         x = xi - self.moveNumber
    #         for yi in range(moveGridSize):
    #             y = yi - self.moveNumber

    #             if self.isInRange(x, y):
    #                 if (x == 0) and (y == 0):
    #                     continue
    #                 moves.append((x, y))

class BasicFlower(Tile):
    def __init__(self, isHost, moveNumber, isWhite, cordinate) -> None:
        super().__init__(isHost, moveNumber, cordinate)
        self.isWhite = isWhite

    def __str__(self) -> str:
        return 'W' if self.isWhite else 'R' + str(self.moveNumber) + super().__str__()

class SpecialFlower(Tile):
    def __init__(self, isHost, isOrchid, cordinate) -> None:
        moveNumber = 6 if isOrchid else 2
        self.isOrchid = isOrchid
        super().__init__(isHost, moveNumber, cordinate)

    def __str__(self) -> str:
        return 'O' if self.isOrchid else 'L' + super().__str__()

class Accent(Tile):
    accentStrings = ['Rock', 'Wheel', 'Knotweed', 'Boat']
    accentAbbrvs = ['R', 'W', 'K', 'B']

    wheelCordMatrix = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
    # 2 1 0
    # 3   7
    # 4 5 6

    def __init__(self, isHost, accentType, cordinate) -> None:
        super().__init__(isHost, 0, cordinate)
        self.accentType = accentType

    def __str__(self) -> str:
        return Accent.accentAbbrvs[self.accentType] + super().__str__()

class Board():
    gates = ((0, -8), (0, 8), (-8, 0), (8, 0))

    @staticmethod
    def isOnBoard(cord):
        if absSum(*cord) <= 8:
            return True
        if (absSum(cord) <= 12) and (max(abs(cord[0]), abs(cord[1])) <= 8):
            return True
        return False

    @staticmethod
    def boardSection(cord):
        if absSum(*cord) < 7:
            if cord[0] * cord[1] > 0:
                return 'R'
            elif cord[0] * cord[1] < 0:
                return 'W'
        elif absDiff(*cord) > 7:
            return 'G'
        return 'N'

    def __init__(self, reserve, tiles) -> None:
        self.reserve: list[Tile] = reserve
        self.tiles: list[Tile] = tiles
        self.isHostTurn: bool = False
        self.turnNumber: int = 1

        self.gameLog = ['0H.' + ','.join([Accent.accentAbbrvs[i.accentType] for i in self.getAccentsReserve(True)])]
        self.gameLog.append( '0G.' + ','.join([Accent.accentAbbrvs[i.accentType] for i in self.getAccentsReserve(False)]) )

    @staticmethod
    def new(hostAccents = None, guestAccents = None):
        reserve = []
        for i in [True, False]:
            relevantAccents = hostAccents if i else guestAccents

            for j in [False, True]:
                for k in [3, 4, 5]:
                    reserve.extend([BasicFlower(i, k, j, None)] * 3)

            if relevantAccents == None:
                for j in [0, 1, 2, 3]:
                    reserve.append(Accent(i, j, None))
            else:
                reserve.extend(relevantAccents)

            for j in [False, True]:
                reserve.append(SpecialFlower(i, j, None))

        return Board(reserve, [])
    
    @staticmethod
    def fromGameLog(log: str = '', file = None, click=False):
        if file != None:
            with open(file, 'r') as f:
                log = f.read()

        board = None
        hostAccents = []
        guestAccents = []
        for i in log.splitlines():
            if i[0] == '0':
                list1 = i[3:].split(',')
                for j in list1:
                    if i[1] == 'H':
                        hostAccents.append(Accent(True, Accent.accentAbbrvs.index(j), None))
                    else:
                        guestAccents.append(Accent(False, Accent.accentAbbrvs.index(j), None))

            else:
                if board == None:
                    if hostAccents == []:
                        hostAccents = None
                    if guestAccents == []:
                        guestAccents = None

                    board = Board.new(hostAccents, guestAccents)

                board.makeMoveFromString(i, click)

        return board

    def getReserve(self, isHost) -> list[Tile]:
        reserve = []
        for i in self.reserve:
            if i.isHost == isHost:
                reserve.append(i)

        return reserve

    def getAccentsReserve(self, isHost=None):
        accents = []
        for i in self.reserve:
            if isinstance(i, Accent):
                if (isHost == None) or (i.isHost == isHost):
                    accents.append(i)

        return accents
    
    def getMatchingTileFromReserve(self, tile, count = False, index = False):
        num = 0
        for g, i in enumerate(self.reserve):
            if not isinstance(i, type(tile)):
                continue

            conditions = []

            conditions.append(i.isHost == tile.isHost)
            conditions.append(i.moveNumber == tile.moveNumber)

            if isinstance(tile, BasicFlower):
                conditions.append(i.isWhite == tile.isWhite)

            elif isinstance(tile, Accent):
                conditions.append(i.accentType == tile.accentType)

            elif isinstance(tile, SpecialFlower):
                conditions.append(i.isOrchid == tile.isOrchid)

            if not False in conditions:
                if count:
                    num += 1
                else:
                    if index:
                        return g
                    return i

        if count:
            return num
        return None

    def getTileAtCord(self, cord):
        for i in self.tiles:
            if i.cordinate == cord:
                return i

        return None

    def isPlantValid(self, tile, newCord):
        if not newCord in Board.gates:
            return False

        if isinstance(tile, Accent):
            return False

        if self.getTileAtCord(newCord) != None:
            return False

        if not tile in self.reserve:
            return False

        return True

    def isMoveValid(self, tile: Tile, newCord, harmonyBonusTile = None, harmonyBonusCord = None, harmonyBonusExtraCord = None):
        isPlanting = False
        if tile.cordinate == None:
            isPlanting = True
            if harmonyBonusTile != None:
                return False

    def makeMove(self, tile: Tile, newCord, harmonyBonusTile = None, harmonyBonusCord = None, harmonyBonusExtraCord = None, click = False):
        logStr = f'{self.turnNumber}{'H' if tile.isHost else 'G'}.'

        if click:
            self.tileToScreen(tile)
            self.tileToScreen(Tile(True, 0, newCord))

            if harmonyBonusTile != None:
                self.tileToScreen(harmonyBonusTile)
                self.tileToScreen(Tile(True, 0, harmonyBonusCord))

                if harmonyBonusExtraCord != None:
                    self.tileToScreen(Tile(True, 0, harmonyBonusExtraCord))

        if tile.cordinate == None:
            self.reserve.remove(tile)
            tile.cordinate = newCord
            self.tiles.append(tile)
            logStr += str(tile)

        else:
            logStr += str(tile)
            tile.cordinate = newCord
            logStr += f'-({newCord[0]},{newCord[1]})'

        if harmonyBonusTile != None:
            if harmonyBonusExtraCord != None:
                extraTile = self.getTileAtCord(harmonyBonusCord)
                extraTile.cordinate = harmonyBonusExtraCord

            if isinstance(harmonyBonusTile, Accent):
                if harmonyBonusTile.accentType == 1: #wheel
                    print('wheel')
                    rotateList = []
                    for i in Accent.wheelCordMatrix:
                        rotateList.append(self.getTileAtCord((i[0] + harmonyBonusCord[0], i[1] + harmonyBonusCord[1])))

                    for i in range(len(rotateList)):
                        if rotateList[i] == None:
                            continue

                        rotateList[i].cordinate = (Accent.wheelCordMatrix[i-1][0] + harmonyBonusCord[0], Accent.wheelCordMatrix[i-1][1] + harmonyBonusCord[1])

            self.reserve.remove(harmonyBonusTile)
            harmonyBonusTile.cordinate = harmonyBonusCord
            self.tiles.append(harmonyBonusTile)
            logStr += f'+{str(harmonyBonusTile)}'

            if harmonyBonusExtraCord != None:
                logStr += f'-({harmonyBonusExtraCord[0]},{harmonyBonusExtraCord[1]})'

        self.gameLog.append(logStr)

        if tile.isHost:
            self.turnNumber += 1

    def makeMoveFromString(self, string: str, click=False):
        import re

        Pcord = r'\(-?\d,-?\d\)'
        PbasicFlower = r'[RW][345]'
        PaccentChoice = r'([RWKB],?){4}'
        PharmonyPlant = r'[RWKBLO]' + Pcord
        Pbeginning = r'\d+[GH]'

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

        self.makeMove(tile, cord, harmonyTile, harmonyCord, extraHarmonyCord, click=click)

    def tileToScreen(self, tile: Tile, origin = (660, 540), squareSize = 34, tileStartX = 975, tileEndX=1185, minUndDepth = 280, gap1 = 8, gap2 = 16, gap3 = 28, gap4 = 28, click = True, sleepTime=1):
        from pynput import mouse
        from keyboard import hook_key

        hook_key('esc')

        cont = mouse.Controller()

        if tile.cordinate == None:
            from PIL import Image, ImageGrab
            screenHeight = ImageGrab.grab().height
            im = ImageGrab.grab((tileStartX, minUndDepth, tileEndX, screenHeight), all_screens=True)
            bim = im.convert('1', dither=0)
            projection = bim.getprojection()

            reserveX = 0
            reserveY = 0

            for i in projection[0]:
                if i == 1:
                    break
                reserveX += 1

            spanLength = 0
            for i, j in enumerate(projection[1]):
                if j == 0:
                    spanLength += 1
                elif j == 1:
                    if spanLength > (gap4-4):
                        reserveY = i
                        break
                    spanLength = 0

            halfSquareSize = squareSize // 2
            tileOriginLocation = (reserveX + tileStartX + halfSquareSize, reserveY + minUndDepth + halfSquareSize)

            hostDepth = 0
            guestDepth = 0
            currentDepth = 0
            for g in [True, False]:
                for i in [False, True]:
                    for j in [3, 4, 5]:
                        sampTile = BasicFlower(g, j, i, None)
                        currentDepth = self.getMatchingTileFromReserve(sampTile, True)
                        if g:
                            if currentDepth > hostDepth:
                                hostDepth = currentDepth
                        else:
                            if currentDepth > guestDepth:
                                guestDepth = currentDepth

            print(f'host:{hostDepth}, guest:{guestDepth}')
            Yoffset = 0
            Xind = 0
            relavantDepth = hostDepth
            if not tile.isHost:
                relavantDepth = guestDepth
                Yoffset += squareSize * (hostDepth + 1)
                Yoffset += gap1 * (hostDepth - 1)
                Yoffset += (gap2 + gap3)

            if not isinstance(tile, BasicFlower):
                Yoffset += squareSize * relavantDepth
                Yoffset += gap1 * (relavantDepth - 1)
                Yoffset += gap2

                if isinstance(tile, Accent):
                    Xind = tile.accentType
                else:
                    Xind = 4 + int(tile.isOrchid)

            else:
                Xind = 3 * int(tile.isWhite)
                Xind += (tile.moveNumber - 3)

            clickCord = (tileOriginLocation[0] + (Xind * squareSize), tileOriginLocation[1] + Yoffset)

        else:
            clickCord = ((tile.cordinate[0] * squareSize) + origin[0], (-tile.cordinate[1] * squareSize) + origin[1])

        cont.position = clickCord
        if click:
            cont.click(mouse.Button.left)
        sleep(sleepTime)

if __name__ == '__main__':
    b = Board.fromGameLog('', 'exampleGames/gameNotation1.txt', True)