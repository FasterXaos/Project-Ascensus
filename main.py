import copy
import os
import csv
from itertools import product
from datetime import datetime

import matplotlib.pyplot as plt

from src.config import loadConfiguration, saveRocketConfigurationToMyConfigs
from src.optimizer import RocketOptimizer


def plotMultipleRocketSimulations(
    simulationDataList: list[tuple[str, list, list, list]],
    targetVelocity: float,
    savePath: str | None = None,
    show: bool = True):
    """Выводит все симуляции на одном рисунке.
    simulationDataList — список кортежей (rocketName, timeHistory, heightHistory, velocityHistory)."""

    if not simulationDataList:
        print("Нет данных для общего графика")
        return

    fig, axs = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("Сравнение симуляций по сетке тяги и Ve", fontsize=16)

    cmap = plt.colormaps['tab10']
    colors = cmap(range(len(simulationDataList)))

    for idx, (rocketName, timeHistory, heightHistory, velocityHistory) in enumerate(simulationDataList):
        color = colors[idx]

        axs[0].plot(timeHistory, heightHistory, linewidth=2, color=color, label=rocketName)
        if heightHistory:
            maxHeight = heightHistory[-1]
            maxTime = timeHistory[-1]
            axs[0].plot(maxTime, maxHeight, marker='*', markersize=10, color=color)

        axs[1].plot(timeHistory, velocityHistory, linewidth=2, color=color, label=rocketName)
        if velocityHistory:
            maxVel = velocityHistory[-1]
            maxTime = timeHistory[-1]
            axs[1].plot(maxTime, maxVel, marker='*', markersize=10, color=color)

    axs[0].set_ylabel('Высота (м)')
    axs[0].grid(True, alpha=0.3)
    axs[0].legend(loc='upper left', fontsize=9)

    axs[1].set_ylabel('Скорость (м/с)')
    axs[1].set_xlabel('Время (с)')
    axs[1].axhline(y=targetVelocity, color='red', linestyle='--', linewidth=1.5, label='Целевая скорость')
    axs[1].grid(True, alpha=0.3)
    axs[1].legend(loc='upper left', fontsize=9)

    plt.tight_layout()

    if savePath:
        plt.savefig(savePath, dpi=300, bbox_inches='tight')
        print(f"Общий график сохранён: {savePath}")

    if show:
        plt.show()
    else:
        plt.close(fig)

def runThrustExhaustVelocityGridAnalysis(
    thrustValues: list[float],
    exhaustVelocityValues: list[float],
    rocketConfigPath: str = "configs/rocket/OneStageRocket.json",
    baseThrustRatios: list[float] | None = None,
    baseVeRatios: list[float] | None = None,
    saveIndividualPlots: bool = True,
    saveConfigs: bool = True,
    saveCommonPlot: bool = True,
    saveCommonTable: bool = True,
    commonPlotShow: bool = True
):
    """
    1. Загружает одноступенчатую ракету.
    2. Перебирает сетку тяги + Ve.
    Для многоступенчатых: baseThrustRatios и baseVeRatios — коэффициенты-множители для каждой ступени
    3. Для каждой комбинации: меняет параметры, вызывает оптимизатор,
       инициализирует массы, запускает симуляцию.
    4. Сохраняет индивидуальный график без показа + конфиг.
    5. В конце рисует общий график со всеми симуляциями.
    """

    print(f"Запуск анализа по сетке: {len(thrustValues)} значений тяги * {len(exhaustVelocityValues)} значений Ve")

    config = loadConfiguration(rocketConfigPath)
    originalRocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    numStages = len(originalRocket.stages)
    
    # По умолчанию — одинаковые значения для всех ступеней
    if baseThrustRatios is None:
        baseThrustRatios = [1.0] * numStages
    if baseVeRatios is None:
        baseVeRatios = [1.0] * numStages

    if len(baseThrustRatios) < numStages or len(baseVeRatios) < numStages:
        raise ValueError(f"Длина baseThrustRatios/baseVeRatios должна быть не меньше числа ступеней ({numStages})")

    if len(baseThrustRatios) > numStages or len(baseVeRatios) > numStages:
        print(f"Предупреждение: лишние коэффициенты будут проигнорированы")

    simulationDataList = []  # для общего графика: (name, time, height, velocity)

    for thrust, ve in product(thrustValues, exhaustVelocityValues):
        rocketCopy = copy.deepcopy(originalRocket)

        # Применяем коэффициенты к каждой ступени
        for idx, stage in enumerate(reversed(rocketCopy.stages)):
            thisThrust = thrust * baseThrustRatios[idx]
            thisVe = ve * baseVeRatios[idx]
            stage.updateThrustAndExhaustVelocity(thisThrust, thisVe)

        shortThrust = f"{thrust/1000:.0f}kN"
        shortVe = f"{ve/1000:.1f}km_s"
        rocketCopy.name = f"{originalRocket.name}_T{shortThrust}_Ve{shortVe}"
        print(f"- Запуск оптимизации и симуляции для {rocketCopy.name}")

        optimizer = RocketOptimizer(rocketCopy, simulator, atmosphere, gravity, aerodynamics)
        result = optimizer.optimize(maxiter=300)

        timeHist, heightHist, velHist = simulator.runSimulation(
            rocketCopy,
            gravity,
            atmosphere,
            aerodynamics,
            plot=False,
            saveCSV=False,
            savePlot=saveIndividualPlots
        )

        if saveConfigs:
            saveRocketConfigurationToMyConfigs(
                rocket=rocketCopy,
                aerodynamics=aerodynamics,
                fileName=None
            )

        simulationDataList.append((rocketCopy.name, timeHist, heightHist, velHist))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("results/plots", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)
    
    if simulationDataList and saveCommonPlot:
        commonSavePath = f"results/plots/grid_comparison_{timestamp}.png"
        plotMultipleRocketSimulations(
            simulationDataList=simulationDataList,
            targetVelocity=simulator.targetVelocity,
            savePath=commonSavePath,
            show=commonPlotShow
        )

    if simulationDataList and saveCommonTable:
        tablePath = f"results/tables/grid_results_{timestamp}.csv"
        with open(tablePath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["rocket_name", "final_height_m", "final_velocity_m_s", "target_velocity_m_s"])
            
            for name, _, heightHist, velHist in simulationDataList:
                finalH = heightHist[-1] if heightHist else 0.0
                finalV = velHist[-1] if velHist else 0.0
                writer.writerow([name, f"{finalH:.2f}", f"{finalV:.2f}", f"{simulator.targetVelocity:.2f}"])
        
        print(f"Таблица результатов сохранена: {tablePath}")

    print(f"Анализ сетки завершён. Обработано {len(simulationDataList)} симуляций.")

if __name__ == "__main__":
    thrustGrid = [3000000.0, 4000000.0, 5000000]      # Н
    veGrid = [2100.0, 3100.0, 4100.0]               # м/с

    baseThrustRatios = [1.0, 0.3, 0.1]   # Stage1, Stage2 ...
    baseVeRatios = [1.0, 1.16, 1.45]

    runThrustExhaustVelocityGridAnalysis(
        thrustValues=thrustGrid,
        exhaustVelocityValues=veGrid,
        rocketConfigPath="configs/rocket/ThreeStageRocket.json",
        baseThrustRatios=baseThrustRatios,
        baseVeRatios=baseVeRatios,
        saveIndividualPlots=True,
        saveConfigs=True,
        saveCommonPlot=True,
        saveCommonTable=True,
        commonPlotShow=True
    )

    # presets = [
    #     "configs/rocket/OneStageRocket.json",
    #     "configs/rocket/TwoStageRocket.json",
    #     "configs/rocket/ThreeStageRocket.json",
    #     "configs/rocket/FourStageRocket.json",
    # ]
    # rocketIndex = 2

    # config = loadConfiguration(presets[rocketIndex])
    # rocket = config["rocket"]
    # simulator = config["simulator"]
    # atmosphere = config["atmosphere"]
    # gravity = config["gravity"]
    # aerodynamics = config["aerodynamics"]

    # optimizer = RocketOptimizer(rocket, simulator, atmosphere, gravity, aerodynamics)

    # result = optimizer.optimize(
    #     bounds=None,
    #     maxiter=500
    # )

    # optimalFuelMasses = result["optimalFuelMasses"]
    # rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
    # rocket.reloadRocket()
    # rocket.name = rocket.name + '-opt'

    # idealSpeed = rocket.calculateIdealMaximumVelocity()
    # print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    # simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)


    # resultBrute = optimizer.optimizeByBruteForce(gridResolution=10)

    # optimalFuelMasses = resultBrute["optimalFuelMasses"]
    # rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
    # rocket.reloadRocket()
    # rocket.name = rocket.name + '-brute'

    # idealSpeed = rocket.calculateIdealMaximumVelocity()
    # print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    # simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)

    # print("Сравнение масс:")
    # print("DE   :", result["optimalFuelMasses"])
    # print("Brute:", resultBrute["optimalFuelMasses"])


    # config = loadConfiguration(presets[rocketIndex])
    # rocket = config["rocket"]
    # simulator = config["simulator"]
    # atmosphere = config["atmosphere"]
    # gravity = config["gravity"]
    # aerodynamics = config["aerodynamics"]

    # idealSpeed = rocket.calculateIdealMaximumVelocity()
    # print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    # simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)
    # print(f"Масса ракеты (Циолковский): {rocket.getFullRocketMass():.1f} кг")
