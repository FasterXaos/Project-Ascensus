from src.config import loadConfiguration

def main():
    """Главная функция — только загрузка конфига и проверка инициализации"""
    configuration = loadConfiguration()

    print("=== Project Ascensus — инициализация из configs/TestRocket.json ===")
    print(f"Ракета: {configuration['rocket'].name}")
    print(f"Полезная нагрузка: {configuration['rocket'].payloadMass} кг\n")

    print("Ступени (массы рассчитаны по структурным коэффициентам):")
    for stage in configuration['rocket'].stages:
        print(f"  → {stage.name}:")
        print(f"     Начальная масса         = {stage.initialMass:,.0f} кг")
        print(f"     Топливо                 = {stage.fuelMass:,.0f} кг")
        print(f"     Структура               = {stage.structuralMass:,.0f} кг")
        print(f"     Структурный коэффициент = {stage.structuralFraction}")
        print(f"     Скорость истечения      = {stage.exhaustVelocity} м/с")
        print(f"     Тяга                    = {stage.thrust:,.0f} Н")
        print(f"     Межступенчатый штраф = {stage.interstagePenalty} кг\n")

    print(f"Цель симуляции: высота {configuration['simulator'].targetAltitude} м, "
          f"скорость {configuration['simulator'].targetVelocity} м/с")
    print(f"Расчётная начальная масса для проектирования: {configuration['rocket'].stages[-1].initialMass} кг стартовая масса (оптимизировано)")

    print("\nВсе классы успешно инициализированы из конфига.")
    print(configuration['rocket'].getCurrentRocketMass())

    height, velocity = configuration["simulator"].runSimulation(
        configuration["rocket"],
        configuration["gravity"],
        configuration["atmosphere"],
        configuration["aerodynamics"],
        plot=True
    )

    print("\n=== RESULT ===")
    print(f"Final height: {height:.1f} m")
    print(f"Final velocity: {velocity:.1f} m/s")

    
if __name__ == "__main__":
    main()