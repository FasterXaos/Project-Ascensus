class Gravity:
    """Класс расчета гравитации"""

    def __init__(self,
                 standardGravity: float = 9.80665,
                 planetRadius: float = 6371000.0,
                 planetMass: float = 5.972e24,
                 gConstant: float = 6.67430e-11):
        self.standardGravity = standardGravity
        self.planetRadius = planetRadius
        self.planetMass = planetMass
        self.gConstant = gConstant

    def getGravityAtHeight(self, height: float) -> float:
        """Гравитация на высоте"""

        r = self.planetRadius + height

        return self.gConstant * self.planetMass / (r ** 2)
