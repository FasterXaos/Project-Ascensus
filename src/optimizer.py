import numpy as np

from scipy.optimize import differential_evolution, brute

class RocketMassOptimizer:
    """Оптимизатор массы ракеты (минимизация полной массы при достижении целей)"""
    def __init__(self, rocket, simulator, atmosphere, gravity, aerodynamics):
        self.rocket = rocket
        self.simulator = simulator
        self.atmosphere = atmosphere
        self.gravity = gravity
        self.aerodynamics = aerodynamics

    def _objectiveFunction(self, fuelMasses: list[float], targetVelocity: float,
                           penaltyWeight: float = 2_000_000.0) -> float:
        """Целевая функция: минимизируем полную массу + штраф за недостижение скорости"""

        self.rocket.initializeMassesFromFuelMasses(fuelMasses)

        _, _, velocityHistory = self.simulator.runSimulation(
            self.rocket, self.gravity, self.atmosphere, self.aerodynamics, plot=False
        )

        finalVelocity = velocityHistory[-1]    
        velocityDeficit = targetVelocity - finalVelocity
        fullMass = self.rocket.getFullRocketMass()

        if finalVelocity < targetVelocity:
            return 1e10 + velocityDeficit * 1e7

        return fullMass - 0.01 * velocityDeficit

    def optimize(self, bounds: list[tuple[float, float]] | None = None,
                 targetVelocity: float | None = None,
                 maxiter: int = 500) -> dict:
        """Запуск оптимизации"""

        if targetVelocity is None:
            targetVelocity = self.simulator.targetVelocity

        if bounds is None:
            payload = self.rocket.payloadMass
            bounds = [(payload, 200_000.0) for _ in self.rocket.stages]

        result = differential_evolution(
            self._objectiveFunction,
            bounds=bounds,
            args=(targetVelocity,),
            maxiter=maxiter,
            workers=-1,
            updating="deferred",
            popsize=15 * len(bounds)
        )
        print(len(bounds))

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
    
    def optimizeByBruteForce(self,
                            bounds: list[tuple[float, float]] | None = None,
                            targetVelocity: float | None = None,
                            gridResolution: int = 20,
                            finish: bool = True) -> dict:
        """Брутфорс-перебор. Работает точно так же, как optimize(), но перебирает все комбинации по равномерной сетке."""

        if targetVelocity is None:
            targetVelocity = self.simulator.targetVelocity

        if bounds is None:
            payload = self.rocket.payloadMass
            bounds = [(payload, 200_000.0) for _ in self.rocket.stages]

        # Преобразуем границы в формат scipy.brute (slice с complex для равномерной сетки)
        ranges = tuple(
            slice(low, high, complex(0, gridResolution))
            for low, high in bounds
        )

        result = brute(
            self._objectiveFunction,
            ranges=ranges,
            args=(targetVelocity,),
            finish=finish,
            full_output=True,
            workers=-1
        )

        optimalFuelMasses = np.atleast_1d(result[0]).tolist()
        totalEvaluations = gridResolution ** len(bounds)

        self.rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
        self.rocket.reloadRocket()

        finalMass = self.rocket.getFullRocketMass()

        print(f"Брутфорс-перебор завершён ({gridResolution}^{len(bounds)} = {totalEvaluations} точек)")
        print(f"Минимальная полная масса: {finalMass:.2f} кг")
        print(f"Оптимальные массы топлива: {[round(m, 1) for m in optimalFuelMasses]} кг")

        return {
            "optimalFuelMasses": optimalFuelMasses,
            "minimalFullMass": finalMass,
            "gridEvaluations": totalEvaluations,
            "gridResolution": gridResolution
        }
