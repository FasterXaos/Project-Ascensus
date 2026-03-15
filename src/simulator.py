class Simulator:
    def __init__(self, targetAltitude: float, targetVelocity: float,
                 timeStep: float, maxTime: float):
        self.targetAltitude = targetAltitude
        self.targetVelocity = targetVelocity
        self.timeStep = timeStep
        self.maxTime = maxTime
