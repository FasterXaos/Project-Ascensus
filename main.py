from src.utils.analysis import (
    runThrustExhaustVelocityGridAnalysis,
    runSingleRocketOptimizationComparison
)
from src.optimizer import RocketOptimizer
from src.config import loadConfiguration

if __name__ == "__main__":
    presets = [
        "configs/rocket/OneStageRocket.json",
        "configs/rocket/TwoStageRocket.json",
        "configs/rocket/ThreeStageRocket.json",
        "configs/rocket/FourStageRocket.json",
    ]
    rocketIndex = 0

    # # === Симуляция одной ракеты ===
    # config = loadConfiguration(presets[0])
    # rocket = config["rocket"]
    # simulator = config["simulator"]
    # atmosphere = config["atmosphere"]
    # gravity = config["gravity"]
    # aerodynamics = config["aerodynamics"]

    # optimizer = RocketOptimizer(rocket, simulator, atmosphere, gravity, aerodynamics)

    # simulator.runSimulation(
    #     rocket, gravity, atmosphere, aerodynamics,
    #     plot=True, saveCSV=False, savePlot=True, 
    #     integrationMethod="rk4"
    # )

    # # === Grid-анализ ===
    # veGrid = [2100.0, 3100.0, 4100.0]       # м/с
    # seaLevelThrustGrid = [3e6, 4e6, 5e6]        # Н
    # vacuumThrustGrid = [round(vacuumThrust * 1.15, 1) for vacuumThrust in seaLevelThrustGrid]       # Н
    # thrustPairs = list(zip(seaLevelThrustGrid, vacuumThrustGrid))

    # baseThrustRatios = [1.0, 0.3, 0.1, 0.03]  # Stage1, Stage2 ...
    # baseVeRatios = [1.0, 1.16, 1.45, 1.65]

    # for rocketIndex in range(0, 4):
    #     runThrustExhaustVelocityGridAnalysis(
    #         exhaustVelocityValues=veGrid,
    #         thrustPairs=thrustPairs,
    #         rocketConfigPath=presets[rocketIndex],
    #         baseVeRatios=baseVeRatios,
    #         baseThrustRatios=baseThrustRatios,
    #         saveIndividualPlots=False,
    #         saveConfigs=True,
    #         saveCommonPlot=True,
    #         saveCommonTable=True,
    #         commonPlotShow=False,
    #         integrationMethod="euler"
    #     )

    # # === Оптимизация одной ракеты ===
    # runSingleRocketOptimizationComparison(
    #     rocketConfigPath=presets[rocketIndex],
    #     maxIterForDifferentialEvolution=500,
    #     gridResolutionForBruteForce=10,
    #     plot=True,
    #     savePlot=True,
    #     saveCsv=True,
    #     integrationMethod="euler"
    # )
