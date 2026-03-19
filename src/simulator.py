import math
import csv
from datetime import datetime

import matplotlib.pyplot as plt

class Simulator:
    """Класс симуляции полета ракеты"""
    def __init__(self, targetVelocity: float, timeStep: float, maxTime: float):
        self.targetVelocity = targetVelocity
        self.timeStep = timeStep
        self.maxTime = maxTime

    def runSimulation(self, rocket, gravity, atmosphere,
                      aerodynamics, plot: bool = False,
                      saveCSV: bool = False):
        """Запускает 1D симуляцию полёта ракеты"""

        if saveCSV:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/simulation_{rocket.name}_{timestamp}.csv"

            csvFile = open(filename, mode='w', newline='')
            csvWriter = csv.writer(csvFile)

            csvWriter.writerow([
                "time",
                "height",
                "velocity",
                "mass",
                "thrust",
                "drag",
                "gravity",
                "stage",
                "fuelMass"
            ])

        currentTime = 0.0
        velocity = 0.0
        height = rocket.currentHeight

        timeHistory = []
        velocityHistory = []
        heightHistory = []

        while currentTime < self.maxTime:
            thrust = 0.0
            if rocket.activeStages:
                activeStage = rocket.activeStages[-1]
                if activeStage.currentFuelMass <= 0.0:
                    rocket.detachStage(-1)
                    continue

                thrust = activeStage.updateFuelMassOverTime(self.timeStep)

            else:
                break

            rocketMass = rocket.getCurrentRocketMass()

            g = gravity.getGravityAtHeight(height)
            airDensity = atmosphere.getAirDensityAtHeight(height)

            dragMagnitude = aerodynamics.calculateDragForce(velocity, airDensity)
            drag = math.copysign(dragMagnitude, velocity) if velocity != 0 else 0.0

            acceleration = (thrust - drag - rocketMass * g) / rocketMass

            velocity += acceleration * self.timeStep
            height += velocity * self.timeStep

            if height < 0.0:
                height = 0.0
                velocity = 0.0

            timeHistory.append(currentTime)
            velocityHistory.append(velocity)
            heightHistory.append(height)

            stageName = activeStage.name if rocket.activeStages else "None"
            fuelMass = activeStage.currentFuelMass if rocket.activeStages else 0.0

            if saveCSV:
                csvWriter.writerow([
                    currentTime,
                    height,
                    velocity,
                    rocketMass,
                    thrust,
                    drag,
                    g,
                    stageName,
                    fuelMass
                ])

            currentTime += self.timeStep

            if velocity >= self.targetVelocity:
                break

        rocket.currentHeight = height

        if saveCSV:
            csvFile.close()
            print(f"CSV сохранён: {filename}")

        if plot:
            rocketName = rocket.name
            self.plotResults(rocketName, timeHistory, heightHistory, velocityHistory)

        return timeHistory, heightHistory, velocityHistory

    def plotResults(self, rocketName: str, timeHistory: list, heightHistory: list, velocityHistory: list):
        """Кривые скорости и высоты от времени"""
        
        fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=False)
        fig.suptitle(f"Результаты 1D симуляции — {rocketName}", fontsize=16)

        axs[0].plot(timeHistory, heightHistory, linewidth=2, label='Altitude')
        axs[0].set_ylabel('Altitude (m)')
        axs[0].grid(True, alpha=0.3)
        axs[0].legend()

        axs[1].plot(timeHistory, velocityHistory, color='orange', linewidth=2, label='Velocity')
        axs[1].axhline(y=self.targetVelocity, color='red', linestyle='--', linewidth=1.5, label='Target Velocity')
        axs[1].set_ylabel('Velocity (m/s)')
        axs[1].grid(True, alpha=0.3)
        axs[1].legend()

        axs[2].plot(velocityHistory, heightHistory, color='green', linewidth=2, label='Trajectory')
        axs[2].axvline(x=self.targetVelocity, color='red', linestyle='--', linewidth=1.5, label='Target Velocity')
        axs[2].set_xlabel('Velocity (m/s)')
        axs[2].set_ylabel('Altitude (m)')
        axs[2].grid(True, alpha=0.3)
        axs[2].legend()

        plt.tight_layout()
        plt.show()
