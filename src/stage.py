class Stage:
    def __init__(self, name: str, initialMass: float, fuelMass: float,
                 structuralMass: float, exhaustVelocity: float,
                 structuralFraction: float, interstagePenalty: float,
                 thrust: float):
        self.name = name
        self.initialMass = initialMass
        self.fuelMass = fuelMass
        self.structuralMass = structuralMass
        self.exhaustVelocity = exhaustVelocity
        self.structuralFraction = structuralFraction
        self.interstagePenalty = interstagePenalty
        self.thrust = thrust
