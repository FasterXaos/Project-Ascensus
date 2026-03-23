import matplotlib.pyplot as plt

from src.config import loadConfiguration, saveRocketConfigurationToMyConfigs
from src.optimizer import RocketMassOptimizer
from src.rocket import Rocket
from src.simulator import Simulator

def main():

    presets = [
        "configs/rocket/OneStageRocket.json",
        "configs/rocket/TwoStageRocket.json",
        "configs/rocket/ThreeStageRocket.json",
        "configs/rocket/FourStageRocket.json",
    ]

    config = loadConfiguration(presets[2])
    rocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    optimizer = RocketMassOptimizer(rocket, simulator, atmosphere, gravity, aerodynamics)

    result = optimizer.optimize(
        bounds=None,
        targetVelocity=6000,
        maxiter=300
    )

    optimalFuelMasses = result["optimalFuelMasses"]
    rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
    rocket.reloadRocket()
    rocket.name = rocket.name + '-opt'

    idealSpeed = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)


    # resultBrute = optimizer.optimizeByBruteForce(
    # gridResolution=30,
    # finish=True
    # )

    # optimalFuelMasses = resultBrute["optimalFuelMasses"]
    # rocket.initializeMassesFromFuelMasses(optimalFuelMasses)
    # rocket.reloadRocket()
    # rocket.name = rocket.name + '-opt_brute'

    # idealSpeed = rocket.calculateIdealMaximumVelocity()
    # print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    # simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)

    # print("Сравнение масс:")
    # print("DE   :", result["optimalFuelMasses"])
    # print("Brute:", resultBrute["optimalFuelMasses"])


    config = loadConfiguration(presets[2])
    rocket = config["rocket"]
    simulator = config["simulator"]
    atmosphere = config["atmosphere"]
    gravity = config["gravity"]
    aerodynamics = config["aerodynamics"]

    idealSpeed = rocket.calculateIdealMaximumVelocity()
    print(f"Идеальная максимальная скорость (Циолковский): {idealSpeed:.1f} м/с")
    simulator.runSimulation(rocket, gravity, atmosphere, aerodynamics, plot=True, saveCSV=True, savePlot=True)
    print(f"Масса ракеты (Циолковский): {rocket.getFullRocketMass():.1f} м/с")

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
