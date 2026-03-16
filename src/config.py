import json
import math

from .stage import Stage
from .rocket import Rocket
from .simulator import Simulator
from .atmosphere import Atmosphere
from .gravity import Gravity
from .aerodynamics import Aerodynamics

def _calculateStageMasses(payloadMass: float,
                          stageDeltaV: float,
                          exhaustVelocity: float,
                          structuralFraction: float):
    """Расчёт масс одной ступени при идеальных условиях (уравнение Циолковского)"""

    massRatio = math.exp(stageDeltaV / exhaustVelocity)

    if massRatio <= 1.0:
        raise ValueError("Mass ratio must be > 1")

    denominator = 1.0 - structuralFraction * massRatio
    if denominator <= 0:
        print("Structural fraction too large for given deltaV")
        propellantMass = 100000
        structuralMass = 100000
        initialMass = payloadMass + propellantMass + structuralMass
        return initialMass, propellantMass, structuralMass

    propellantMass = payloadMass * (massRatio - 1.0) * (1.0 - structuralFraction) / denominator
    structuralMass = (structuralFraction / (1.0 - structuralFraction)) * propellantMass

    initialMass = payloadMass + propellantMass + structuralMass
    
    return initialMass, propellantMass, structuralMass

def _calculateAllStageMasses(payloadMass: float,
                             stagesData: list,
                             requiredDeltaV: float):
    """Расчёт масс всех ступеней при идеальных условиях (уравнение Циолковского)"""

    if not stagesData:
        return []

    stageDeltaV = requiredDeltaV / len(stagesData)
    currentUpperMass = payloadMass
    results = []

    for stageData in stagesData:
        structuralFraction = stageData["structuralFraction"]
        exhaustVelocity = stageData["exhaustVelocity"]
        interstagePenalty = stageData.get("interstagePenalty", 0.0)

        initialMass, fuelMass, structuralMass = _calculateStageMasses(
            payloadMass=currentUpperMass,
            stageDeltaV=stageDeltaV,
            exhaustVelocity=exhaustVelocity,
            structuralFraction=structuralFraction
        )

        results.append({
            "name": stageData["name"],
            "initialMass": initialMass,
            "fuelMass": fuelMass,
            "structuralMass": structuralMass,
            "exhaustVelocity": exhaustVelocity,
            "structuralFraction": structuralFraction,
            "interstagePenalty": interstagePenalty,
            "thrust": stageData.get("thrust", 0.0)
        })

        currentUpperMass = initialMass + interstagePenalty

    return results

def loadConfiguration(rocketConfigPath: str = "configs/rocket/TestRocket.json",
                      simulationConfigPath: str = "configs/simulation/simulation.json",
                      planetConfigPath: str = "configs/planet/planet.json"):
    """Читает три отдельных JSON-конфига (ракета + симуляция + планета) и инициализирует все классы"""

    with open(rocketConfigPath, "r", encoding="utf-8") as file:
        rocketConfigData = json.load(file)

    with open(simulationConfigPath, "r", encoding="utf-8") as file:
        simulationConfigData = json.load(file)

    with open(planetConfigPath, "r", encoding="utf-8") as file:
        planetConfigData = json.load(file)

    rocketData = rocketConfigData["rocket"]
    stagesData = rocketData["stages"]

    calculatedStages = _calculateAllStageMasses(
        payloadMass=rocketData["payloadMass"],
        stagesData=stagesData,
        requiredDeltaV=simulationConfigData["target"]["velocity"] * 1.18
    )

    stagesList = []
    for calc in calculatedStages:
        stage = Stage(
            name=calc["name"],
            initialMass=calc["initialMass"],
            fuelMass=calc["fuelMass"],
            structuralMass=calc["structuralMass"],
            exhaustVelocity=calc["exhaustVelocity"],
            structuralFraction=calc["structuralFraction"],
            interstagePenalty=calc["interstagePenalty"],
            thrust=calc["thrust"]
        )
        stagesList.append(stage)

    rocket = Rocket(
        name=rocketData["name"],
        initialAltitude=rocketData["initialAltitude"],
        payloadMass=rocketData["payloadMass"],
        stages=stagesList
    )

    simulator = Simulator(
        targetAltitude=simulationConfigData["target"]["altitude"],
        targetVelocity=simulationConfigData["target"]["velocity"],
        timeStep=simulationConfigData["simulation"]["timeStep"],
        maxTime=simulationConfigData["simulation"]["maxTime"]
    )

    atmosphere = Atmosphere(
        seaLevelDensity=planetConfigData["atmosphere"]["seaLevelDensity"],
        scaleHeight=planetConfigData["atmosphere"]["scaleHeight"],
    )

    gravity = Gravity(
        standardGravity=planetConfigData["gravity"]["standardGravity"],
        planetRadius=planetConfigData["gravity"]["planetRadius"],
        planetMass=planetConfigData["gravity"]["planetMass"],
        gConstant=planetConfigData["gravity"]["gConstant"]
    )

    aerodynamics = Aerodynamics(
        dragCoefficient=rocketConfigData["aerodynamics"]["dragCoefficient"],
        referenceArea=rocketConfigData["aerodynamics"]["referenceArea"]
    )

    return {
        "rocket": rocket,
        "simulator": simulator,
        "atmosphere": atmosphere,
        "gravity": gravity,
        "aerodynamics": aerodynamics
    }
