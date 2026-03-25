import matplotlib.pyplot as plt

from src.config import loadConfiguration, saveRocketConfigurationToMyConfigs
from src.optimizer import RocketOptimizer
from src.rocket import Rocket
from src.simulator import Simulator

def main():

    presets = [
        "configs/rocket/OneStageRocket.json",
        "configs/rocket/TwoStageRocket.json",
        "configs/rocket/ThreeStageRocket.json",
        "configs/rocket/FourStageRocket.json",
    ]
    rocketIndex = 3

    config = loadConfiguration(presets[rocketIndex])
    rocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    optimizer = RocketOptimizer(rocket, simulator, atmosphere, gravity, aerodynamics)

    result = optimizer.optimize(
        bounds=None,
        maxiter=500
    )

    optimalFuelMasses = result["optimalFuelMasses"]
    rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
    rocket.reloadRocket()
    rocket.name = rocket.name + '-opt'

    idealSpeed = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)


    resultBrute = optimizer.optimizeByBruteForce(gridResolution=10)

    optimalFuelMasses = resultBrute["optimalFuelMasses"]
    rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
    rocket.reloadRocket()
    rocket.name = rocket.name + '-brute'

    idealSpeed = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)

    print("Сравнение масс:")
    print("DE   :", result["optimalFuelMasses"])
    print("Brute:", resultBrute["optimalFuelMasses"])


    config = loadConfiguration(presets[rocketIndex])
    rocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    idealSpeed = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)
    print(f"Масса ракеты (Циолковский): {rocket.getFullRocketMass():.1f} кг")

    # saveRocketConfigurationToMyConfigs(
    #     rocket=config["rocket"],
    #     aerodynamics=config["aerodynamics"],
    #     fileName="MySuperEfficientTwoStageRocket.json"
    # )

    # config = loadConfiguration("myConfigs/MySuperEfficientTwoStageRocket.json")
    # rocket = config["rocket"]
    # simulator = config["simulator"]
    # atmosphere = config["atmosphere"]
    # gravity = config["gravity"]
    # aerodynamics = config["aerodynamics"]

    # idealSpeed = rocket.calculateIdealMaximumVelocity()
    # print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    # simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)

if __name__ == "__main__":
    main()
