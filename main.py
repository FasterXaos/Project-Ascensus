import math
import matplotlib.pyplot as plt

def calculateDeltaVelocity(initialMass, finalMass, exhaustVelocity):
    """Расчет прироста скорости по формуле Циолковского"""
    if finalMass <= 0 or initialMass <= finalMass:
        return 0.0
    
    return exhaustVelocity * math.log(initialMass / finalMass)

def simulateSingleStageRocket(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, exhaustVelocity):
    """Симуляция одной ступени с явным payload"""
    finalMass = payloadMass + totalStructuralMass
    deltaV = calculateDeltaVelocity(totalInitialMass, finalMass, exhaustVelocity)

    return deltaV

def simulateMultiStageRocket(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, numberOfStages, exhaustVelocity):
    """Улучшенная симуляция многоступенчатой ракеты"""
    totalDeltaV = 0.0
    currentMass = totalInitialMass
    fuelPerStage = totalFuelMass / numberOfStages
    structuralPerStage = totalStructuralMass / numberOfStages
    
    for stageNumber in range(1, numberOfStages + 1):
        stageInitialMass = currentMass
        massAfterFuelBurn = stageInitialMass - fuelPerStage
        
        stageDeltaV = calculateDeltaVelocity(stageInitialMass, massAfterFuelBurn, exhaustVelocity)
        totalDeltaV += stageDeltaV
        
        if stageNumber < numberOfStages:
            currentMass = massAfterFuelBurn - structuralPerStage
        else:
            # Последняя ступень: payload + остаток конструкции последней ступени
            currentMass = massAfterFuelBurn
    
    return totalDeltaV

def findOptimalNumberOfStages(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, exhaustVelocity, maxStages=10):
    """Автоматический поиск оптимального количества ступеней"""
    results = []
    bestStages = 1
    bestDeltaV = 0.0
    
    for stages in range(1, maxStages + 1):
        deltaV = simulateMultiStageRocket(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, stages, exhaustVelocity)
        results.append((stages, deltaV))
        if deltaV > bestDeltaV:
            bestDeltaV = deltaV
            bestStages = stages
    
    print(f"Оптимальное количество ступеней: {bestStages} (Δv = {bestDeltaV:,.0f} м/с)")
    return results

def simulateRocketWithTimeSteps(totalInitialMass, totalFuelMass, exhaustVelocity, burnTime=300, timeStep=1.0):
    """Пошаговая симуляция по времени (уменьшение массы со временем)"""
    currentMass = totalInitialMass
    fuelBurnRate = totalFuelMass / burnTime
    totalDeltaV = 0.0
    time = 0.0
    
    while currentMass > (totalInitialMass - totalFuelMass) and time < burnTime:
        massAfterStep = currentMass - fuelBurnRate * timeStep
        deltaVStep = calculateDeltaVelocity(currentMass, massAfterStep, exhaustVelocity)
        totalDeltaV += deltaVStep
        currentMass = massAfterStep
        time += timeStep
    
    return totalDeltaV

def calculateStageInitialMass(upperMass, stageDeltaV, exhaustVelocity, structuralFraction):
    """Расчёт минимальной начальной массы одной ступени (формула со структурным коэффициентом)"""
    R = math.exp(stageDeltaV / exhaustVelocity)     # Массовое отношение

    if R <= 1.0:
        return upperMass
    
    numerator = (R - 1) * (1 - structuralFraction)
    denominator = 1 - structuralFraction * R

    if denominator <= 0:
        return float('inf')
    
    mPropellant = upperMass * numerator / denominator
    mInert = (structuralFraction / (1 - structuralFraction)) * mPropellant

    return upperMass + mPropellant + mInert

def calculateMinimumLaunchMassForTargetDeltaV(payloadMass, numberOfStages, requiredDeltaV, exhaustVelocity,
                                              structuralFraction=0.12, interstagePenalty=800.0):
    """Минимальная стартовая масса ракеты для достижения орбиты"""

    if numberOfStages < 1:
        return float('inf')
    
    perStageDeltaV = requiredDeltaV / numberOfStages
    currentUpperMass = payloadMass

    for stageNum in range(numberOfStages):
        stageInitialMass = calculateStageInitialMass(currentUpperMass, perStageDeltaV, exhaustVelocity, structuralFraction)
        currentUpperMass = stageInitialMass

        if stageNum < numberOfStages - 1:
            currentUpperMass += interstagePenalty
            
    return currentUpperMass

def test():
    print("=== Project Ascensus ===\n")
    
    # Параметры ракеты
    totalInitialMass = 100_000      # кг
    totalFuelMass = 80_000          # кг
    totalStructuralMass = 15_000    # кг
    payloadMass = 5_000             # кг
    exhaustVelocity = 2800          # м/с
    
    print(f"Параметры:")
    print(f"  Стартовая масса:     {totalInitialMass:,} кг")
    print(f"  Топливо:             {totalFuelMass:,} кг")
    print(f"  Конструкция (баки):  {totalStructuralMass:,} кг")
    print(f"  Полезная нагрузка:   {payloadMass:,} кг")
    print(f"  Скорость истечения:  {exhaustVelocity} м/с\n")
    
    print("Сравнение ступеней:")
    for stages in range(1, 8):
        deltaV = simulateMultiStageRocket(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, stages, exhaustVelocity)
        print(f"  {stages} ступен{'ь' if stages == 1 else 'и'}:  Δv = {deltaV:,.0f} м/с")
    
    print("\nОптимизация:")
    findOptimalNumberOfStages(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, exhaustVelocity)
    
    stagesList = list(range(1, 11))
    deltaVList = [simulateMultiStageRocket(totalInitialMass, totalFuelMass, totalStructuralMass, payloadMass, s, exhaustVelocity) for s in stagesList]
    plt.figure(figsize=(10, 5))
    plt.plot(stagesList, deltaVList, marker='o', linewidth=2)
    plt.title("Зависимость Δv от количества ступеней")
    plt.xlabel("Количество ступеней")
    plt.ylabel("Прирост скорости Δv (м/с)")
    plt.grid(True)
    plt.show()
    
    print("\nПошаговая симуляция (одна ступень по времени):")
    deltaVTime = simulateRocketWithTimeSteps(totalInitialMass, totalFuelMass, exhaustVelocity)
    print(f"Итоговый Δv = {deltaVTime:,.0f} м/с\n")

    payloadMass = 5_000             # кг
    requiredDeltaV = 9_400          # м/с (LEO + потери)
    exhaustVelocity = 2_800         # м/с
    structuralFraction = 0.12       # 12% конструкции в каждой ступени
    interstagePenalty = 800.0       # кг штрафа за каждую дополнительную ступень
    
    print(f"Цель: вывести {payloadMass:,} кг на орбиту (Δv = {requiredDeltaV:,} м/с)")
    print(f"Структурный коэффициент: {structuralFraction:.0%}")
    print(f"Штраф за ступень: {interstagePenalty} кг\n")
    
    print("Сравнение (минимальная стартовая масса):")
    results = []
    bestStages = 1
    bestMass = float('inf')
    
    for stages in range(1, 11):
        launchMass = calculateMinimumLaunchMassForTargetDeltaV(
            payloadMass, stages, requiredDeltaV, exhaustVelocity,
            structuralFraction, interstagePenalty
        )
        results.append((stages, launchMass))
        
        print(f"  {stages} ступен{'ь' if stages == 1 else 'и'}:  стартовая масса = {launchMass:,.0f} кг")
        if launchMass < bestMass:
            bestMass = launchMass
            bestStages = stages
    
    print(f"\nОптимальное количество ступеней: {bestStages} (минимальная стартовая масса = {bestMass:,.0f} кг)")
    
    stagesList = [r[0] for r in results]
    massList = [r[1] for r in results]
    plt.figure(figsize=(10, 5))
    plt.plot(stagesList, massList, marker='o', linewidth=2, color='red')
    plt.title("Оптимизация: стартовая масса vs количество ступеней")
    plt.xlabel("Количество ступеней")
    plt.ylabel("Минимальная стартовая масса (кг)")
    plt.grid(True)
    plt.show()

def main():
    test()

if __name__ == "__main__":
    main()