import copy
import os
import csv
from itertools import product
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from src.config import loadConfiguration, saveRocketConfiguration
from src.optimizer import RocketOptimizer


def plotMultipleRocketSimulations(
    simulationDataList: list[tuple[str, float, list, list, list]],
    targetVelocity: float,
    savePath: str | None = None,
    show: bool = True
):
    """Выводит результат нескольких симуляций на одном рисунке."""
    
    if not simulationDataList:
        print("Нет данных для общего графика")
        return

    fig, axs = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("Сравнение симуляций по сетке тяги и Ve", fontsize=16)

    cmap = plt.colormaps['rainbow']
    colors = cmap(np.linspace(0, 1, len(simulationDataList)))

    for idx, (rocketName, rocketMass, timeHistory, heightHistory, velocityHistory) in enumerate(simulationDataList):
        color = colors[idx]

        axs[0].plot(timeHistory, heightHistory, linewidth=2, color=color, label=rocketName)
        if heightHistory:
            axs[0].plot(timeHistory[-1], heightHistory[-1], marker='*', markersize=10, color=color)

        axs[1].plot(timeHistory, velocityHistory, linewidth=2, color=color, label=rocketName)
        if velocityHistory:
            axs[1].plot(timeHistory[-1], velocityHistory[-1], marker='*', markersize=10, color=color)

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
    exhaustVelocityValues: list[float],
    thrustPairs: list[tuple[float, float]],
    rocketConfigPath: str = "configs/rocket/OneStageRocket.json",
    baseVeRatios: list[float] | None = None,
    baseThrustRatios: list[float] | None = None,
    saveIndividualPlots: bool = True,
    saveConfigs: bool = True,
    saveCommonPlot: bool = True,
    saveCommonTable: bool = True,
    commonPlotShow: bool = True,
    integrationMethod: str = "euler"
):
    """
    1. Загружает ракету (одно- или многоступенчатую).
    2. Перебирает сетку тяги + Ve (с учётом base-коэффициентов для ступеней).
    3. Оптимизирует, запускает симуляцию, сохраняет конфиги и графики.
    4. В конце — общий график и таблица.
    """

    print(f"Запуск анализа по сетке: {len(thrustPairs)} значений тяги * {len(exhaustVelocityValues)} значений Ve")

    config = loadConfiguration(rocketConfigPath)
    originalRocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    numStages = len(originalRocket.stages)
    
    # По умолчанию — одинаковые значения для всех ступеней
    if baseVeRatios is None:
        baseVeRatios = [1.0] * numStages
    if baseThrustRatios is None:
        baseThrustRatios = [1.0] * numStages

    if len(baseThrustRatios) < numStages or len(baseVeRatios) < numStages:
        raise ValueError(f"Длина baseThrustRatios/baseVeRatios должна быть не меньше числа ступеней: {numStages}")

    if len(baseThrustRatios) > numStages or len(baseVeRatios) > numStages:
        print(f"Предупреждение: лишние коэффициенты будут проигнорированы")

    simulationDataList = []

    for ve, (seaLevelThrust, vacuumThrust) in product(exhaustVelocityValues, thrustPairs):
        rocketCopy = copy.deepcopy(originalRocket)

        for idx, stage in enumerate(reversed(rocketCopy.stages)):
            thisVe = ve * baseVeRatios[idx]
            thisSeaLevelThrust = seaLevelThrust * baseThrustRatios[idx]
            thisVacuumThrust = vacuumThrust * baseThrustRatios[idx]
            stage.updateThrustAndExhaustVelocity(thisVe, thisSeaLevelThrust, thisVacuumThrust)

        shortVe = f"{ve / 1000 :.1f}km_s"
        shortSeaLevelThrust = f"{seaLevelThrust / 1000 :.0f}kN(sl)"
        shortVacuumThrust = f"{vacuumThrust / 1000 :.0f}kN(v)"
        rocketCopy.name = f"{originalRocket.name}—Ve{shortVe}—T{shortSeaLevelThrust}_{shortVacuumThrust}"
        print(f"- Запуск оптимизации и симуляции для {rocketCopy.name}")

        optimizer = RocketOptimizer(rocketCopy, simulator, atmosphere, gravity, aerodynamics, integrationMethod)
        result = optimizer.optimize(maxiter=300)

        shortRocketMass = f"{rocketCopy.getFullRocketMass() / 1000.0 :.0f}t"
        rocketCopy.name = rocketCopy.name + f"—M{shortRocketMass}"

        timeHist, heightHist, velHist = simulator.runSimulation(
            rocketCopy,
            gravity,
            atmosphere,
            aerodynamics,
            plot=False,
            saveCSV=False,
            savePlot=saveIndividualPlots, 
            integrationMethod=integrationMethod
        )

        if saveConfigs:
            saveRocketConfiguration(
                rocket=rocketCopy,
                aerodynamics=aerodynamics,
                fileName=None
            )

        simulationDataList.append((rocketCopy.name, rocketCopy.getFullRocketMass(), timeHist, heightHist, velHist))

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
            writer.writerow([
                "rocket_name",
                "rocket_mass_kg",
                "final_time_s",
                "final_height_m",
                "final_velocity_m_s",
                "target_velocity_m_s"
            ])
            
            for name, mass, timeHist, heightHist, velHist in simulationDataList:
                finalT= timeHist[-1] if timeHist else 0.0
                finalH = heightHist[-1] if heightHist else 0.0
                finalV = velHist[-1] if velHist else 0.0
                writer.writerow([name, f"{mass:.2f}", f"{finalT:.2f}", f"{finalH:.2f}", f"{finalV:.2f}", f"{simulator.targetVelocity:.2f}"])
        
        print(f"Таблица результатов сохранена: {tablePath}")

    print(f"Анализ сетки завершён. Обработано {len(simulationDataList)} симуляций.")


def runSingleRocketOptimizationComparison(
    rocketConfigPath: str = "configs/rocket/OneStageRocket.json",
    maxIterForDifferentialEvolution: int = 500,
    gridResolutionForBruteForce: int = 10,
    plot: bool = True,
    savePlot: bool = True,
    saveCsv: bool = True,
    integrationMethod: str = "euler"
):
    """
    Выполняет оптимизацию одной ракеты:
    - Differential Evolution
    - Brute Force
    - Сравнение масс топлива ступеней
    """

    config = loadConfiguration(rocketConfigPath)
    rocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    optimizer = RocketOptimizer(rocket, simulator, atmosphere, gravity, aerodynamics, integrationMethod)

    # === Differential Evolution ===
    differentialEvolutionResult = optimizer.optimize(
        bounds=None,
        maxiter=maxIterForDifferentialEvolution
    )
    optimalFuelMassesFromDe = differentialEvolutionResult["optimalFuelMasses"]
    rocket.initializeMassesFromFuelMasses(optimalFuelMassesFromDe)
    rocket.reloadRocket()
    rocket.name = rocket.name + '-opt'

    idealSpeedDe = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский) после DE: {idealSpeedDe:.1f} м/с")
    simulator.runSimulation(
        rocket, gravity, atmosphere, aerodynamics,
        plot=plot, saveCSV=saveCsv, savePlot=savePlot, 
            integrationMethod=integrationMethod
    )

    # === Brute Force ===
    bruteForceResult = optimizer.optimizeByBruteForce(gridResolution=gridResolutionForBruteForce)
    optimalFuelMassesFromBrute = bruteForceResult["optimalFuelMasses"]
    rocket.initializeMassesFromFuelMasses(optimalFuelMassesFromBrute)
    rocket.reloadRocket()
    rocket.name = rocket.name + '-brute'

    idealSpeedBrute = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский) после BruteForce: {idealSpeedBrute:.1f} м/с")
    simulator.runSimulation(
        rocket, gravity, atmosphere, aerodynamics,
        plot=plot, saveCSV=saveCsv, savePlot=savePlot, 
            integrationMethod=integrationMethod
    )

    # === Comparison ===
    print("Сравнение масс оптимального топлива:")
    print(f"DE     : {[f"{mass:.1f}" for mass in differentialEvolutionResult["optimalFuelMasses"]]} кг")
    print(f"Brute  : {[f"{mass:.1f}" for mass in bruteForceResult["optimalFuelMasses"]]} кг")


def runEngineAnalysis(
    enginePresetPaths: list[str],
    saveIndividualPlots: bool = False,
    saveConfigs: bool = False,
    saveCommonPlot: bool = True,
    saveCommonTable: bool = True,
    commonPlotShow: bool = True,
    integrationMethod: str = "euler"
):
    """
    Анализирует список пресетов ракет (одноступенчатые ракеты с разными двигателями).  
    1. Загружает конфигурацию.
    2. Запускает оптимизацию.
    3. Запускает симуляцию.
    4. Собирает данные и строит общий график (и таблицу).
    """
    print(f"Запуск анализа пресетов двигателей: {len(enginePresetPaths)} конфигураций")

    simulationDataList = []

    for presetPath in enginePresetPaths:
        config = loadConfiguration(presetPath)
        originalRocket = config["rocket"]
        simulator = config["simulator"]
        atmosphere = config["atmosphere"]
        gravity = config["gravity"]
        aerodynamics = config["aerodynamics"]

        rocketCopy = copy.deepcopy(originalRocket)

        ve = rocketCopy.stages[0].exhaustVelocity if rocketCopy.stages else 0.0
        seaLevelThrust = rocketCopy.stages[0].seaLevelThrust if rocketCopy.stages else 0.0
        vacuumThrust = rocketCopy.stages[0].vacuumThrust if rocketCopy.stages else 0.0

        shortVe = f"{ve / 1000:.1f}km_s"
        shortSeaLevelThrust = f"{seaLevelThrust / 1000:.0f}kN(sl)"
        shortVacuumThrust = f"{vacuumThrust / 1000:.0f}kN(v)"

        rocketCopy.name = f"{originalRocket.name}—Ve{shortVe}—T{shortSeaLevelThrust}_{shortVacuumThrust}"
        print(f"- Запуск оптимизации и симуляции для {rocketCopy.name}")

        optimizer = RocketOptimizer(rocketCopy, simulator, atmosphere, gravity, aerodynamics, integrationMethod)
        result = optimizer.optimize(maxiter=300)

        shortRocketMass = f"{rocketCopy.getFullRocketMass() / 1000.0:.0f}t"
        rocketCopy.name = rocketCopy.name + f"—M{shortRocketMass}"

        timeHist, heightHist, velHist = simulator.runSimulation(
            rocketCopy,
            gravity,
            atmosphere,
            aerodynamics,
            plot=False,
            saveCSV=False,
            savePlot=saveIndividualPlots,
            integrationMethod=integrationMethod
        )

        if saveConfigs:
            saveRocketConfiguration(
                rocket=rocketCopy,
                aerodynamics=aerodynamics,
                fileName=None
            )

        simulationDataList.append((rocketCopy.name, rocketCopy.getFullRocketMass(), timeHist, heightHist, velHist))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("results/plots", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)

    if simulationDataList and saveCommonPlot:
        commonSavePath = f"results/plots/engine_comparison_{timestamp}.png"
        plotMultipleRocketSimulations(
            simulationDataList=simulationDataList,
            targetVelocity=simulator.targetVelocity,
            savePath=commonSavePath,
            show=commonPlotShow
        )

    if simulationDataList and saveCommonTable:
        tablePath = f"results/tables/engine_results_{timestamp}.csv"
        with open(tablePath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "rocket_name",
                "rocket_mass_kg",
                "final_time_s",
                "final_height_m",
                "final_velocity_m_s",
                "target_velocity_m_s"
            ])
            for name, mass, timeHist, heightHist, velHist in simulationDataList:
                finalT = timeHist[-1] if timeHist else 0.0
                finalH = heightHist[-1] if heightHist else 0.0
                finalV = velHist[-1] if velHist else 0.0
                writer.writerow([
                    name,
                    f"{mass:.2f}",
                    f"{finalT:.2f}",
                    f"{finalH:.2f}",
                    f"{finalV:.2f}",
                    f"{simulator.targetVelocity:.2f}"
                ])
        print(f"Общая таблица сохранена: {tablePath}")
