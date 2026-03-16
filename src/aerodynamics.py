class Aerodynamics:
    """Класс аэродинамики"""
    def __init__(self, dragCoefficient: float = 0.5, referenceArea: float = 20.0):
        self.dragCoefficient = dragCoefficient
        self.referenceArea = referenceArea

    def calculateDragForce(self, velocity: float, airDensity: float) -> float:
        """Сила сопротивления воздуха"""
        return 0.5 * self.dragCoefficient * airDensity * (velocity ** 2) * self.referenceArea
