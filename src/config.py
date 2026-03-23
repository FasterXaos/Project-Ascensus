import json
import math
import os

from .stage import Stage
from .rocket import Rocket
from .simulator import Simulator
from .atmosphere import Atmosphere
from .gravity import Gravity
from .aerodynamics import Aerodynamics

def _calculateStageMasses(rocketName: str,
                          payloadMass: float,
                          stageDeltaV: float,
                          exhaustVelocity: float,
                          structuralFraction: float):
    """Расчёт масс одной ступени при идеальных условиях (уравнение Циолковского)"""

    massRatio = math.exp(stageDeltaV / exhaustVelocity)

    if massRatio <= 1.0:
        raise ValueError("Массовое соотношение > 1")

    denominator = 1.0 - structuralFraction * massRatio
    if denominator <= 0:
        print(f"Структурный коэффициент {rocketName} слишком большой для данной deltaV")
        print(f"Значение массы структуры и топливо установлены на 100000 кг.")
        propellantMass = 100_000
        structuralMass = 100_000
        initialMass = payloadMass + propellantMass + structuralMass
        return initialMass, propellantMass, structuralMass

    propellantMass = payloadMass * (massRatio - 1.0) * (1.0 - structuralFraction) / denominator
    structuralMass = (structuralFraction / (1.0 - structuralFraction)) * propellantMass

    initialMass = payloadMass + propellantMass + structuralMass
    
    return initialMass, propellantMass, structuralMass

def _calculateAllStageMasses(rocketName: str,
                             payloadMass: float,
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
            rocketName=rocketName,
            payloadMass=currentUpperMass,
            stageDeltaV=stageDeltaV,
            exhaustVelocity=exhaustVelocity,
            structuralFraction=structuralFraction
        )

        results.append({
            "name": stageData["name"],
            "fuelMass": fuelMass,
            "structuralMass": structuralMass,
            "exhaustVelocity": exhaustVelocity,
            "structuralFraction": structuralFraction,
            "interstagePenalty": interstagePenalty,
            "thrust": stageData.get("thrust", 0.0)
        })

        currentUpperMass = initialMass + interstagePenalty

    return results

def loadConfiguration(rocketConfigPath: str = "configs/rocket/TwoStageRocket.json",
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
    fuelMasses = rocketData.get("fuelMasses")

    calculatedStages = _calculateAllStageMasses(
        rocketName=rocketData["name"],
        payloadMass=rocketData["payloadMass"],
        stagesData=stagesData,
        requiredDeltaV=simulationConfigData["target"]["velocity"] * 1.18
    )

    if fuelMasses is not None:
        stagesList = []
        for stageData in stagesData:
            stage = Stage(
                name=stageData["name"],
                fuelMass=0.0,                    # временно
                structuralMass=0.0,              # временно
                exhaustVelocity=stageData["exhaustVelocity"],
                structuralFraction=stageData["structuralFraction"],
                interstagePenalty=stageData.get("interstagePenalty", 0.0),
                thrust=stageData.get("thrust", 0.0)
            )
            stagesList.append(stage)

        rocket = Rocket(
            name=rocketData["name"],
            initialAltitude=rocketData["initialAltitude"],
            payloadMass=rocketData["payloadMass"],
            stages=stagesList
        )

        rocket.initializeMassesFromFuelMasses(fuelMasses)

    else:
        calculatedStages = _calculateAllStageMasses(
            rocketName=rocketData["name"],
            payloadMass=rocketData["payloadMass"],
            stagesData=stagesData,
            requiredDeltaV=simulationConfigData["target"]["velocity"] * 1.18
        )

        stagesList = []
        for calc in calculatedStages:
            stage = Stage(
                name=calc["name"],
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
        targetVelocity=simulationConfigData["target"]["velocity"],
        timeStep=simulationConfigData["simulation"]["timeStep"],
        maxTime=simulationConfigData["simulation"]["maxTime"]
    )

    atmosphere = Atmosphere(
        seaLevelDensity=planetConfigData["atmosphere"]["seaLevelDensity"],
        scaleHeight=planetConfigData["atmosphere"]["scaleHeight"],
    )

    gravity = Gravity(
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

def saveRocketConfigurationToMyConfigs(rocket: Rocket,
                                       aerodynamics: Aerodynamics,
                                       fileName: str | None = None,
                                       saveDir: str = "myConfigs") -> str:
    """Сохраняет ракету (вместе с актуальными массами топлива) в папку saveDir."""

    if fileName is None:
        fileName = f"{rocket.name.replace(' ', '_')}.json"

    os.makedirs(saveDir, exist_ok=True)
    savePath = os.path.join(saveDir, fileName)

    rocketDict = {
        "name": rocket.name,
        "initialAltitude": rocket.initialAltitude,
        "payloadMass": rocket.payloadMass,
        "stages": [
            {
                "name": stage.name,
                "structuralFraction": stage.structuralFraction,
                "exhaustVelocity": stage.exhaustVelocity,
                "interstagePenalty": stage.interstagePenalty,
                "thrust": stage.thrust
            }
            for stage in rocket.stages
        ],
        "fuelMasses": [stage.fuelMass for stage in rocket.stages]
    }

    aerodynamicsDict = {
        "dragCoefficient": aerodynamics.dragCoefficient,
        "referenceArea": aerodynamics.referenceArea
    }

    fullConfig = {
        "rocket": rocketDict,
        "aerodynamics": aerodynamicsDict
    }

    with open(savePath, "w", encoding="utf-8") as file:
        json.dump(fullConfig, file, indent=4, ensure_ascii=False)

    print(f"Ракета успешно сохранена в myConfigs: {savePath}")
    return savePath
