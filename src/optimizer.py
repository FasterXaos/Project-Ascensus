import numpy as np
from typing import Optional

from scipy.optimize import differential_evolution

class RocketMassOptimizer:
    """Оптимизатор массы ракеты (минимизация полной массы при достижении целей)"""
    def __init__(self, rocket, simulator, atmosphere, gravity, aerodynamics):
        self.rocket = rocket
        self.simulator = simulator
        self.atmosphere = atmosphere
        self.gravity = gravity
        self.aerodynamics = aerodynamics

    def _objectiveFunction(self, fuelMasses: list[float], targetVelocity: float,
                           penaltyWeight: float = 1_000_000.0) -> float:
        """Целевая функция: минимизируем полную массу + штраф за недостижение скорости"""

        self.rocket.initializeMassesFromFuelMasses(fuelMasses)

        timeHistory, heightHistory, velocityHistory = self.simulator.runSimulation(
            self.rocket, self.gravity, self.atmosphere, self.aerodynamics, plot=False
        )

        finalVelocity = velocityHistory[-1]
        velNormError = abs(finalVelocity - targetVelocity) / targetVelocity

        fullMass = self.rocket.getFullRocketMass()
        penalty = penaltyWeight * (velNormError ** 2)

        return fullMass + penalty

    def optimize(self, initialFuelGuess: Optional[list[float]] = None,
                 bounds: Optional[list[tuple[float, float]]] = None,
                 targetVelocity: Optional[float] = None,
                 maxiter: int = 200) -> dict:
        """Запуск оптимизации"""

        if targetVelocity is None:
            targetVelocity = self.simulator.targetVelocity

        if bounds is None:
            payload = self.rocket.payloadMass
            bounds = [(payload, 2_000_000.0) for _ in self.rocket.stages]

        if initialFuelGuess is None:
            initialFuelGuess = [stage.fuelMass for stage in self.rocket.stages]

        result = differential_evolution(
            self._objectiveFunction,
            bounds=bounds,
            args=(targetVelocity,),
            maxiter=maxiter,
            workers=-1,
            updating="deferred"
        )

        optimalFuelMasses = result.x.tolist()
        self.rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
        self.rocket.reloadRocket()

        finalMass = self.rocket.getFullRocketMass()

        print(f"Оптимизация завершена. Минимальная полная масса: {finalMass:.2f} кг")
        print(f"Оптимальные массы топлива: {[round(m, 1) for m in optimalFuelMasses]} кг")

        return {
            "optimalFuelMasses": optimalFuelMasses,
            "minimalFullMass": finalMass,
            "success": result.success,
            "message": result.message
        }
