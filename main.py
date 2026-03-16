import matplotlib.pyplot as plt

from src.config import loadConfiguration
from src.rocket import Rocket
from src.simulator import Simulator

def main():

    presets = [
        # "configs/rocket/OneStageRocket.json",
        "configs/rocket/TestRocket.json",
        "configs/rocket/ThreeStageRocket.json",
        "configs/rocket/FourStageRocket.json",
    ]

    print("=== Project Ascensus - сравнение многоступенчатых ракет ===\n")
    results = []
    allTrajectories = []

    for configPath in presets:
        configuration = loadConfiguration(configPath)
        rocket: Rocket = configuration["rocket"]
        simulator: Simulator = configuration["simulator"]

        print(f"\n  {rocket.name} ({len(rocket.stages)} ступеней)")
        print("   Ступени (массы рассчитаны автоматически):")
        for stage in rocket.stages:
            print(f"     → {stage.name}: "
                  f"топливо {stage.fuelMass:,.0f} кг | "
                  f"структура {stage.structuralMass:,.0f} кг | "
                  f"тяга {stage.thrust:,.0f} Н")
        print(f"   Стартовая масса ракеты: {rocket.getCurrentRocketMass():,.0f} кг\n")

        timeHistory, heightHistory, velocityHistory = simulator.runSimulation(
            rocket,
            configuration["gravity"],
            configuration["atmosphere"],
            configuration["aerodynamics"],
            plot=False
        )

        finalHeight = heightHistory[-1]
        finalVelocity = velocityHistory[-1]
        success = (finalHeight >= simulator.targetAltitude and
                   finalVelocity >= simulator.targetVelocity)

        results.append({
            "name": rocket.name,
            "stages": len(rocket.stages),
            "finalHeight": finalHeight,
            "finalVelocity": finalVelocity,
            "success": " Да" if success else " Нет",
            "startMass": rocket.getFullRocketMass()
        })

        allTrajectories.append((rocket.name, timeHistory, heightHistory, velocityHistory))

    print("=" * 100)
    print(f"{'Ракета':<18} {'Ступеней'} {'Старт. масса, кг':>12} {'Фин. высота, м':>15} "
          f"{'Фин. скорость, м/с':>18} {'Достигнута цель'}")
    print("=" * 100)
    for r in results:
        print(f"{r['name']:<18} {r['stages']:^8} {r['startMass']:>12,.0f} "
              f"{r['finalHeight']:>15,.0f} {r['finalVelocity']:>18,.1f} {r['success']:>15}")
    print("=" * 100)

    plt.figure(figsize=(12, 7))
    for name, timeH, heightH, velocityH in allTrajectories:
        plt.plot(timeH, heightH, label=f"{name} ({[s for s in results if s['name']==name][0]['stages']} ст.)", linewidth=2)
    
    plt.axhline(y=200000, color='red', linestyle='--', label='Цель 200 км')
    plt.xlabel("Время, с")
    plt.ylabel("Высота, м")
    plt.title("Сравнение траекторий")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    for name, timeH, heightH, velocityH in allTrajectories:
        plt.plot(timeH, velocityH, label=f"{name} ({[s for s in results if s['name']==name][0]['stages']} ст.)", linewidth=2)
    
    plt.axhline(y=7800, color='red', linestyle='--', label='Цель 7800 м/с')
    plt.xlabel("Время, с")
    plt.ylabel("Скорость, м")
    plt.title("Сравнение траекторий")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


    configuration = loadConfiguration(presets[0])
    rocket = configuration["rocket"]
    print(rocket.getFullRocketMass())

    rocket.reloadRocket()
    rocket.reloadRocket(resetHeight=False)

    fuelList = [40000.0, 300000.0]          # топливо для Stage2 и Stage1
    rocket.initializeMassesFromFuelMasses(fuelList)
    print("Новые массы инициализированы, ракета готова к запуску")

    simulator.runSimulation(
        rocket,
        configuration["gravity"],
        configuration["atmosphere"],
        configuration["aerodynamics"],
        plot=True
    )

if __name__ == "__main__":
    main()
