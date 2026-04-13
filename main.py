from src.utils.analysis import (
    runThrustExhaustVelocityGridAnalysis,
    runSingleRocketOptimizationComparison,
    runEngineAnalysis,
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

    enginePresets = [
        "configs/rocket/engine/V-2.json",
        "configs/rocket/engine/RD-107.json",
        "configs/rocket/engine/F-1.json",
        "configs/rocket/engine/NK_33.json",
        # "configs/rocket/engine/J-2.json",     # upper-stage
        # "configs/rocket/engine/RS-25.json",   # core
        "configs/rocket/engine/RD-170.json",
        "configs/rocket/engine/RD-180.json",
        "configs/rocket/engine/RD-191.json",
        "configs/rocket/engine/Merlin_1D.json",
        "configs/rocket/engine/YF-100.json",
        "configs/rocket/engine/BE-4.json",
        "configs/rocket/engine/Raptor_3.json",
    ]
    engineIndex = 0

    runEngineAnalysis(
        enginePresetPaths=enginePresets,
        saveIndividualPlots=False,
        saveConfigs=False,
        saveCommonPlot=True,
        saveCommonTable=True,
        commonPlotShow=True,
        integrationMethod="rk4"
    )

    # # === Симуляция одной ракеты ===
    # config = loadConfiguration(presets[0])
    # rocket = config["rocket"]
    # simulator = config["simulator"]
    # atmosphere = config["atmosphere"]
    # gravity = config["gravity"]
    # aerodynamics = config["aerodynamics"]

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
