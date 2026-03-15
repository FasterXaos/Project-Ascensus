class Stage:
    """Класс одной ступени ракеты"""

    def __init__(self, name: str, initialMass: float, fuelMass: float,
                 structuralMass: float, exhaustVelocity: float,
                 structuralFraction: float, interstagePenalty: float,
                 thrust: float):
        self.name = name
        self.initialMass = initialMass
        self.fuelMass = fuelMass
        self.structuralMass = structuralMass
        self.exhaustVelocity = exhaustVelocity
        self.structuralFraction = structuralFraction
        self.interstagePenalty = interstagePenalty
        self.thrust = thrust
        self.massFlowRate = self.thrust / self.exhaustVelocity if self.thrust > 0 else 0.0
        self.currentFuelMass = self.fuelMass
        self.burnTime = self.fuelMass / self.massFlowRate if self.massFlowRate > 0 else 0.0

    def calculateBurnTime(self) -> float:
        """Время полного выгорания топлива ступени"""

        return self.burnTime

    def updateFuelMassOverTime(self, timeStep: float) -> None:
        """Расход топлива за шаг времени (fuelFlow)"""
        
        if self.massFlowRate > 0 and self.currentFuelMass > 0:
            burnedMass = self.massFlowRate * timeStep
            self.currentFuelMass = max(0.0, self.currentFuelMass - burnedMass)

    def getCurrentStageMass(self) -> float:
        """Текущая масса ступени (учитывает сгорание топлива)"""
        return self.structuralMass + self.currentFuelMass + self.interstagePenalty