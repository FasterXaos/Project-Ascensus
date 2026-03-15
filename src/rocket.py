class Rocket:
    """Класс ракеты"""

    def __init__(self, name: str, initialAltitude: float, payloadMass: float, stages: list):
        self.name = name
        self.currentHeight = initialAltitude
        self.payloadMass = payloadMass
        self.stages = stages
        self.activeStages = stages.copy()

    def getCurrentRocketMass(self) -> float:
        """Текущая масса всей ракеты (учитывает отсоединённые ступени и расход топлива)"""

        activeMass = sum(stage.getCurrentStageMass() for stage in self.activeStages)
        return activeMass + self.payloadMass

    def detachStage(self, stageIndex: int) -> None:
        """Функция отсоединения ступени"""

        if not self.activeStages:
            return
        
        if -len(self.activeStages) <= stageIndex < len(self.activeStages):
            detachedStage = self.activeStages.pop(stageIndex)

            print(
                f"Ступень {detachedStage.name} отсоединена. "
                f"Текущая масса ракеты: {self.getCurrentRocketMass():.2f} кг"
            )
