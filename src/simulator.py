import math
import os
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
                      saveCSV: bool = False,
                      savePlot: bool = False):
        """Запускает 1D симуляцию полёта ракеты"""

        if saveCSV:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/csv/simulation_{rocket.name}_{timestamp}.csv"

            os.makedirs(os.path.dirname(filename), exist_ok=True)

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

            # if velocity >= self.targetVelocity:
            #     break

        rocket.currentHeight = height

        if saveCSV:
            csvFile.close()
            print(f"CSV сохранён: {filename}")

        if plot or savePlot:
            savePath = None
            if savePlot:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs("results/plots", exist_ok=True)
                savePath = f"results/plots/simulation_{rocket.name}_{timestamp}.png"
                print(f"График сохранён: {savePath}")

            self.plotResults(
                rocketName=rocket.name,
                timeHistory=timeHistory,
                heightHistory=heightHistory,
                velocityHistory=velocityHistory,
                savePath=savePath,
                show=plot
            )

        return timeHistory, heightHistory, velocityHistory

    def plotResults(self, rocketName: str, timeHistory: list, heightHistory: list,
                    velocityHistory: list, savePath=None, show=True):
        """Рисует кривые скорости и высоты от времени"""
        
        fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        fig.suptitle(f"Результаты 1D симуляции — {rocketName}", fontsize=16)

        axs[0].plot(timeHistory, heightHistory, linewidth=2, label='Высота')

        if heightHistory:
            maxheight = heightHistory[-1]
            maxTime = timeHistory[-1]

            axs[0].plot(maxTime, maxheight, 'g*', markersize=14, label=f'Макс. высота: {maxheight:.0f} м/с')
            axs[0].annotate(f'{maxheight:.0f}',
                            xy=(maxTime, maxheight),
                            xytext=(maxTime + maxTime * 0.01, maxheight + maxheight * 0.01),
                            fontsize=11, ha='left', color='green')
        
        axs[0].set_ylabel('Высота (м)')
        axs[0].grid(True, alpha=0.3)
        axs[0].legend()

        axs[1].plot(timeHistory, velocityHistory, color='orange', linewidth=2, label='Скорость')
        axs[1].axhline(y=self.targetVelocity, color='red', linestyle='--', linewidth=1.5,
                       label='Целевая скорость')

        if velocityHistory:
            maxVel = velocityHistory[-1]
            maxTime = timeHistory[-1]

            axs[1].plot(maxTime, maxVel, 'r*', markersize=14, label=f'Макс. скорость: {maxVel:.0f} м/с')
            axs[1].annotate(f'{maxVel:.0f}',
                            xy=(maxTime, maxVel),
                            xytext=(maxTime + maxTime * 0.01, maxVel + maxVel * 0.01),
                            fontsize=11, ha='left', color='red')

        axs[1].set_ylabel('Скорость (м/с)')
        axs[1].set_xlabel('Время (с)')
        axs[1].grid(True, alpha=0.3)
        axs[1].legend()

        plt.tight_layout()

        if savePath:
            plt.savefig(savePath, dpi=300, bbox_inches='tight')

        if show:
            plt.show()
        else:
            plt.close(fig)
