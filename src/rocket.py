import math

class Rocket:
    """Класс ракеты"""
    def __init__(self, name: str, initialAltitude: float, payloadMass: float, stages: list):
        self.name = name
        self.initialAltitude = initialAltitude
        self.currentHeight = initialAltitude
        self.payloadMass = payloadMass
        self.stages = stages
        self.activeStages = stages.copy()

    def getCurrentRocketMass(self) -> float:
        """Текущая масса всей ракеты (учитывает отсоединённые ступени и расход топлива)"""
        activeMass = sum(stage.getCurrentStageMass() for stage in self.activeStages)

        return activeMass + self.payloadMass
    
    def getFullRocketMass(self) -> float:
        """Полная масса всей ракеты (все ступени активны + полное топливо в каждой)"""
        fullMass = sum(stage.getFullStageMass() for stage in self.stages)

        return fullMass + self.payloadMass
    
    def setHeight(self, height: float | None = None) -> None:
        """
        Устанавливает текущую высоту ракеты.  
        Если height=None — сбрасывает на initialAltitude (по умолчанию)
        """

        self.currentHeight = height if height is not None else self.initialAltitude

    def initializeMassesFromFuelMasses(self, fuelMasses: list[float]) -> None:
        """
        Инициализирует `fuelMass` и `structuralMass` для каждой ступени по списку топлива.  
        Полностью пересчитывает все зависимые поля ступени.
        """
        
        if len(fuelMasses) != len(self.stages):
            raise ValueError(f"Список fuelMasses должен содержать {len(self.stages)} значений")

        for i, stage in enumerate(self.stages):
            fuelMass = fuelMasses[i]
            structuralFraction = stage.structuralFraction

            if structuralFraction <= 0.0 or structuralFraction >= 1.0:
                raise ValueError(f"Некорректный structuralFraction {structuralFraction} у ступени {stage.name}")

            structuralMass = (structuralFraction / (1.0 - structuralFraction)) * fuelMass

            stage.fuelMass = fuelMass
            stage.structuralMass = structuralMass
            stage.massFlowRate = stage.vacuumThrust / stage.exhaustVelocity if stage.vacuumThrust > 0 else 0.0
            stage.currentFuelMass = stage.fuelMass
            stage.burnTime = stage.fuelMass / stage.massFlowRate if stage.massFlowRate > 0 else 0.0

        self.activeStages = self.stages.copy()

    def detachStage(self, stageIndex: int) -> None:
        """Функция отсоединения ступени"""

        if not self.activeStages:
            return
        
        if -len(self.activeStages) <= stageIndex < len(self.activeStages):
            self.activeStages.pop(stageIndex)


    def reloadRocket(self, resetHeight: bool = True) -> None:
        """
        Перезагрузка ракеты: полностью восстанавливает активные ступени и топливо.  
        Флаг `resetHeight` (по умолчанию `True`) вызывает `setHeight()`
        """
        
        for stage in self.stages:
            stage.currentFuelMass = stage.fuelMass

        self.activeStages = self.stages.copy()

        if resetHeight:
            self.setHeight()

        print(f"Ракета {self.name} успешно перезагружена. "
              f"Высота {'сброшена' if resetHeight else 'не изменена'}.")
        
    def calculateIdealMaximumVelocity(self) -> float:
        """
        Расчёт максимальной идеальной скорости (Δv) по формуле Циолковского
        для многоступенчатой ракеты в вакууме (без гравитации и сопротивления).
        """

        totalDeltaV = 0.0
        upperMass = self.payloadMass

        for stage in self.stages:
            fullStageMass = stage.getFullStageMass()
            dryStageMass = stage.structuralMass + stage.interstagePenalty

            mInitial = fullStageMass + upperMass
            mFinal = dryStageMass + upperMass

            if mInitial > mFinal and stage.exhaustVelocity > 0:
                stageDeltaV = stage.exhaustVelocity * math.log(mInitial / mFinal)
                totalDeltaV += stageDeltaV

            upperMass += fullStageMass

        return totalDeltaV
