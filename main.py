from src.utils.analysis import (
    runThrustExhaustVelocityGridAnalysis,
    runSingleRocketOptimizationComparison
)

if __name__ == "__main__":
    presets = [
        "configs/rocket/OneStageRocket.json",
        "configs/rocket/TwoStageRocket.json",
        "configs/rocket/ThreeStageRocket.json",
        "configs/rocket/FourStageRocket.json",
    ]
    rocketIndex = 0

    veGrid = [2100.0, 3100.0, 4100.0]   # м/с
    thrustGrid = [3e6, 4e6, 5e6]        # Н

    baseThrustRatios = [1.0, 0.3, 0.1, 0.03]  # Stage1, Stage2 ...
    baseVeRatios = [1.0, 1.16, 1.45, 1.65]

    # === Grid-анализ ===
    for rocketIndex in range(0, 4):
        runThrustExhaustVelocityGridAnalysis(
            thrustValues=thrustGrid,
            exhaustVelocityValues=veGrid,
            rocketConfigPath=presets[rocketIndex],
            baseVeRatios=baseVeRatios,
            baseThrustRatios=baseThrustRatios,
            saveIndividualPlots=False,
            saveConfigs=True,
            saveCommonPlot=True,
            saveCommonTable=True,
            commonPlotShow=False
        )

    # === Оптимизация одной ракеты ===
    runSingleRocketOptimizationComparison(
        rocketConfigPath=presets[rocketIndex],
        maxIterForDifferentialEvolution=500,
        gridResolutionForBruteForce=10,
        plot=True,
        savePlot=True,
        saveCsv=True
    )
