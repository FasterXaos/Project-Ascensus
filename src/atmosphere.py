import math

class Atmosphere:
    """Класс атмосферы"""
    
    def __init__(self, seaLevelDensity: float = 1.225, seaLevelPressure: float = 101325.0, scaleHeight: float = 8500.0):
        self.seaLevelDensity = seaLevelDensity
        self.seaLevelPressure = seaLevelPressure
        self.scaleHeight = scaleHeight

    def getAirDensityAtHeight(self, height: float) -> float:
        """Плотность воздуха на заданной высоте"""
        return self.seaLevelDensity * math.exp(-height / self.scaleHeight)
    
    def getPressureAtHeight(self, height: float) -> float:
        """Давление воздуха на заданной высоте"""
        return self.seaLevelPressure * math.exp(-height / self.scaleHeight)
