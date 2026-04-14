import numpy as np
import copy

from scipy.optimize import differential_evolution, brute

class RocketOptimizer:
    """Оптимизатор массы ракеты"""

    def __init__(self, rocket, simulator, atmosphere, gravity, aerodynamics, integrationMethod: str = "euler"):
        self.rocket = rocket
        self.simulator = simulator
        self.atmosphere = atmosphere
        self.gravity = gravity
        self.aerodynamics = aerodynamics
        self.integrationMethod = integrationMethod.lower()

    def _objectiveFunction(self, fuelMasses: list[float], targetVelocity: float) -> float:
        """Целевая функция: максимизирует финальную скорость ракеты"""

        rocket = copy.deepcopy(self.rocket)
        rocket.initializeMassesFromFuelMasses(fuelMasses)

        _, _, velocityHistory = self.simulator.runSimulation(
            rocket, self.gravity, self.atmosphere, self.aerodynamics,
            plot=False, integrationMethod=self.integrationMethod
        )

        finalVelocity = velocityHistory[-1]    

        return -finalVelocity

    def optimize(self, bounds: list[tuple[float, float]] | None = None,
                 targetVelocity: float | None = None,
                 maxiter: int = 500) -> dict:
        """Запуск оптимизации"""

        if targetVelocity is None:
            targetVelocity = self.simulator.targetVelocity

        if bounds is None:
            payload = self.rocket.payloadMass
            bounds = [(payload, 500_000.0) for _ in self.rocket.stages]

        result = differential_evolution(
            self._objectiveFunction,
            bounds=bounds,
            args=(targetVelocity,),
            maxiter=maxiter,
            workers=-1,
            updating="deferred",
            popsize=15 * len(bounds)
        )

        optimalFuelMasses: list[float] = result.x.tolist()
        self.rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
        self.rocket.reloadRocket()

        finalMass = self.rocket.getFullRocketMass()

        print(f"Оптимизация завершена. Полная масса: {finalMass:.2f} кг")
        print(f"Массы топлива: {[round(m, 1) for m in optimalFuelMasses]} кг")

        return {
            "optimalFuelMasses": optimalFuelMasses,
            "minimalFullMass": finalMass,
            "success": result.success,
            "message": result.message
        }
    
    def optimizeByBruteForce(self,
                            bounds: list[tuple[float, float]] | None = None,
                            targetVelocity: float | None = None,
                            gridResolution: int = 20) -> dict:
        """Перебирает все комбинации масс по равномерной сетке."""

        if targetVelocity is None:
            targetVelocity = self.simulator.targetVelocity

        if bounds is None:
            payload = self.rocket.payloadMass
            bounds = [(payload, 500_000.0) for _ in self.rocket.stages]

        # Преобразуем границы в формат scipy.brute (slice с complex для равномерной сетки)
        ranges = tuple(
            slice(low, high, complex(0, gridResolution))
            for low, high in bounds
        )

        result = brute(
            self._objectiveFunction,
            ranges=ranges,
            args=(targetVelocity,),
            full_output=True,
            workers=-1
        )

        optimalFuelMasses = np.atleast_1d(result[0]).tolist()
        totalEvaluations = gridResolution ** len(bounds)

        self.rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
        self.rocket.reloadRocket()

        finalMass = self.rocket.getFullRocketMass()

        print(f"Брутфорс-перебор завершён ({gridResolution}^{len(bounds)} = {totalEvaluations} точек)")
        print(f"Полная масса: {finalMass:.2f} кг")
        print(f"Массы топлива: {[round(m, 1) for m in optimalFuelMasses]} кг")

        return {
            "optimalFuelMasses": optimalFuelMasses,
            "minimalFullMass": finalMass,
            "gridEvaluations": totalEvaluations,
            "gridResolution": gridResolution
        }
