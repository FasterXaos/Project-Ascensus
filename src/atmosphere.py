import math

class Atmosphere:
    """Класс атмосферы"""
    def __init__(self, seaLevelDensity: float = 1.225, scaleHeight: float = 8500.0):
        self.seaLevelDensity = seaLevelDensity
        self.scaleHeight = scaleHeight

    def getAirDensityAtHeight(self, height: float) -> float:
        """Плотность воздуха на заданной высоте"""
        return self.seaLevelDensity * math.exp(-height / self.scaleHeight)
