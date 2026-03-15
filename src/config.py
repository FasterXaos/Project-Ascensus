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
        raise ValueError("Structural fraction too large for given deltaV")

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

def loadConfiguration(configPath: str = "configs/TestRocket.json"):
    """Читает JSON и инициализирует все классы"""

    with open(configPath, "r", encoding="utf-8") as file:
        configData = json.load(file)

    rocketData = configData["rocket"]
    stagesData = rocketData["stages"]

    calculatedStages = _calculateAllStageMasses(
        payloadMass=rocketData["payloadMass"],
        stagesData=stagesData,
        requiredDeltaV=configData["target"]["velocity"] * 1.18
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
        targetAltitude=configData["target"]["altitude"],
        targetVelocity=configData["target"]["velocity"],
        timeStep=configData["simulation"]["timeStep"],
        maxTime=configData["simulation"]["maxTime"]
    )

    atmosphere = Atmosphere(
        seaLevelDensity=configData["atmosphere"]["seaLevelDensity"],
        scaleHeight=configData["atmosphere"]["scaleHeight"],
    )

    gravity = Gravity(
        standardGravity=configData["gravity"]["standardGravity"],
        planetRadius=configData["gravity"]["planetRadius"],
        planetMass=configData["gravity"]["planetMass"],
        gConstant=configData["gravity"]["gConstant"]
    )

    aerodynamics = Aerodynamics(
        dragCoefficient=configData["aerodynamics"]["dragCoefficient"],
        referenceArea=configData["aerodynamics"]["referenceArea"]
    )

    return {
        "rocket": rocket,
        "simulator": simulator,
        "atmosphere": atmosphere,
        "gravity": gravity,
        "aerodynamics": aerodynamics
    }