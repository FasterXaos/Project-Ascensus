class Stage:
    """Класс одной ступени ракеты"""

    def __init__(self, name: str, fuelMass: float,
                 structuralMass: float, exhaustVelocity: float,
                 structuralFraction: float, interstagePenalty: float,
                 thrust: float):
        self.name = name
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

    def updateFuelMassOverTime(self, timeStep: float) -> float:
        """Обновляет currentFuelMass и возвращает эффективную тягу за этот шаг.
        Учитывает случай, когда remainingFuel < massFlowRate * timeStep (partial burn)."""
        if self.massFlowRate <= 0.0 or self.currentFuelMass <= 0.0:
            return 0.0

        burnedMass = self.massFlowRate * timeStep

        if burnedMass > self.currentFuelMass:
            fraction = self.currentFuelMass / burnedMass
            self.currentFuelMass = 0.0
            return self.thrust * fraction
        else:
            self.currentFuelMass -= burnedMass
            return self.thrust

    def getCurrentStageMass(self) -> float:
        """Текущая масса ступени (учитывает сгорание топлива)"""
        return self.structuralMass + self.currentFuelMass + self.interstagePenalty
    
    def getFullStageMass(self) -> float:
        """Полная масса ступени при полном топливе"""
        return self.structuralMass + self.fuelMass + self.interstagePenalty

    def updateThrustAndExhaustVelocity(self, newExhaustVelocity: float, newThrust: float):
        """Обновляет тягу и скорость истечения газов ступени"""
        self.exhaustVelocity = newExhaustVelocity
        self.thrust = newThrust
        
        if self.fuelMass > 0 and newExhaustVelocity > 0:
            self.massFlowRate = newThrust / newExhaustVelocity if newThrust > 0 else 0.0
            self.burnTime = self.fuelMass / self.massFlowRate if self.massFlowRate > 0 else 0.0
