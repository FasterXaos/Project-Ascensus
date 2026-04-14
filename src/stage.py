class Stage:
    """Класс одной ступени ракеты"""

    def __init__(self, name: str, fuelMass: float,
                 structuralMass: float, exhaustVelocity: float,
                 structuralFraction: float, interstagePenalty: float,
                 seaLevelThrust: float, vacuumThrust: float,
                 seaLevelPressure: float = 101325.0):
        self.name = name
        self.fuelMass = fuelMass
        self.structuralMass = structuralMass
        self.exhaustVelocity = exhaustVelocity
        self.structuralFraction = structuralFraction
        self.interstagePenalty = interstagePenalty
        self.seaLevelThrust = seaLevelThrust
        self.vacuumThrust = vacuumThrust
        self.seaLevelPressure = seaLevelPressure
        self.exhaustArea = (self.vacuumThrust - self.seaLevelThrust) / self.seaLevelPressure \
                            if self.vacuumThrust > self.seaLevelThrust else 0.0
        self.massFlowRate = self.vacuumThrust / self.exhaustVelocity \
                            if self.exhaustVelocity > 0.0 and self.vacuumThrust > 0.0 else 0.0
        self.currentFuelMass = self.fuelMass

    def getThrustAtHeight(self, height: float, atmosphere) -> float:
        """Тяга на заданной высоте"""
        if self.vacuumThrust <= 0.0:
            return 0.0
        ambientPressure = atmosphere.getPressureAtHeight(height)

        return max(self.vacuumThrust - ambientPressure * self.exhaustArea, 0.0)

    def updateFuelMassOverTime(self, timeStep: float, atmosphere, height: float = 0.0) -> float:
        """Обновляет `currentFuelMass` и возвращает тягу за этот шаг."""
        if self.massFlowRate <= 0.0 or self.currentFuelMass <= 0.0:
            return 0.0

        currentThrust = self.getThrustAtHeight(height, atmosphere)
        burnedMass = self.massFlowRate * timeStep

        if burnedMass > self.currentFuelMass:
            fraction = self.currentFuelMass / burnedMass
            self.currentFuelMass = 0.0
            return currentThrust * fraction
        else:
            self.currentFuelMass -= burnedMass
            return currentThrust

    def getCurrentStageMass(self) -> float:
        """Текущая масса ступени (учитывает сгорание топлива)"""
        return self.structuralMass + self.currentFuelMass + self.interstagePenalty
    
    def getFullStageMass(self) -> float:
        """Полная масса ступени при полном топливе"""
        return self.structuralMass + self.fuelMass + self.interstagePenalty

    def updateThrustAndExhaustVelocity(self, newExhaustVelocity: float, newSeaLevelThrust: float, newVacuumThrust: float):
        """Обновляет тягу и скорость истечения газов ступени"""
        self.exhaustVelocity = newExhaustVelocity
        self.seaLevelThrust = newSeaLevelThrust
        self.vacuumThrust = newVacuumThrust

        self.exhaustArea = (self.vacuumThrust - self.seaLevelThrust) / self.seaLevelPressure \
                            if self.vacuumThrust > self.seaLevelThrust else 0.0
        
        self.massFlowRate = (self.vacuumThrust / newExhaustVelocity) \
                            if newExhaustVelocity > 0.0 and self.vacuumThrust > 0.0 else 0.0
