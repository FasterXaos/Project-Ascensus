import matplotlib.pyplot as plt
import math

class Simulator:
    """Класс симуляции полета ракеты"""

    def __init__(self, targetAltitude: float, targetVelocity: float,
                 timeStep: float, maxTime: float):
        self.targetAltitude = targetAltitude
        self.targetVelocity = targetVelocity
        self.timeStep = timeStep
        self.maxTime = maxTime

    def runSimulation(self, rocket, gravity, atmosphere, aerodynamics, plot: bool = False):
        """Запускает 1D симуляцию полёта ракеты с исправленной логикой ступеней,
        обработкой отрицательной высоты и coasting-фазой после выгорания всех ступеней."""

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

                activeStage.updateFuelMassOverTime(self.timeStep)
                thrust = activeStage.thrust

            rocketMass = rocket.getCurrentRocketMass()

            g = gravity.getGravityAtHeight(height)
            airDensity = atmosphere.getAirDensityAtHeight(height)

            dragMagnitude = aerodynamics.calculateDragForce(velocity, airDensity)
            drag = -math.copysign(dragMagnitude, velocity) if velocity != 0 else 0.0

            acceleration = (thrust - drag - rocketMass * g) / rocketMass

            velocity += acceleration * self.timeStep
            height += velocity * self.timeStep

            if height < 0.0:
                height = 0.0
                velocity = 0.0

            timeHistory.append(currentTime)
            velocityHistory.append(velocity)
            heightHistory.append(height)

            currentTime += self.timeStep

            if height >= self.targetAltitude and velocity >= self.targetVelocity:
                break

        rocket.currentHeight = height

        if plot:
            self.plotResults(timeHistory, heightHistory, velocityHistory)

        return height, velocity

    def plotResults(self, timeHistory: list, heightHistory: list, velocityHistory: list):
        """Кривые скорости и высоты от времени"""
        
        fig, axs = plt.subplots(3, 1, figsize=(12, 12), sharex=False)
        fig.suptitle("1D Simulation Results — Rocket Ascensus", fontsize=16, fontweight='bold')

        axs[0].plot(timeHistory, heightHistory, color='tab:blue', linewidth=2, label='Altitude')
        axs[0].axhline(y=self.targetAltitude, color='tab:red', linestyle='--', linewidth=1.5, label='Target Altitude')
        axs[0].set_ylabel('Altitude (m)')
        axs[0].grid(True, alpha=0.3)
        axs[0].legend()

        axs[1].plot(timeHistory, velocityHistory, color='tab:orange', linewidth=2, label='Velocity')
        axs[1].axhline(y=self.targetVelocity, color='tab:red', linestyle='--', linewidth=1.5, label='Target Velocity')
        axs[1].set_ylabel('Velocity (m/s)')
        axs[1].grid(True, alpha=0.3)
        axs[1].legend()

        axs[2].plot(velocityHistory, heightHistory, color='tab:green', linewidth=2, label='Trajectory')
        axs[2].axhline(y=self.targetAltitude, color='tab:red', linestyle='--', linewidth=1.5, label='Target Altitude')
        axs[2].axvline(x=self.targetVelocity, color='tab:red', linestyle='--', linewidth=1.5, label='Target Velocity')
        axs[2].set_xlabel('Velocity (m/s)')
        axs[2].set_ylabel('Altitude (m)')
        axs[2].grid(True, alpha=0.3)
        axs[2].legend()

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()