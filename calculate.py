# -*- coding: utf-8 -*-
"""
Модуль расчёта теплопередачи от газа к трубе
"""

import math
from main import HeatTransferInput


def calculate_alpha_convection_gas(input_data: HeatTransferInput) -> float:
    """
    Рассчитывает коэффициент теплоотдачи конвекцией от газа к наружной стенке трубы
    Возвращает: alpha, Вт/(м²·К)
    """
    gas = input_data.gas
    pipe = input_data.pipe_geometry
    flow = input_data.flow
    
    # Средняя температура плёнки (газ + стенка) для определения свойств
    T_gas = gas.temperature
    T_wall_outer = input_data.boundary.inner_wall_temperature + 50  # Приближение
    
    T_film = (T_gas + T_wall_outer) / 2
    T_film_K = T_film + 273.15
    
    # Теплофизические свойства газа (упрощённые аппроксимации)
    if gas.gas_type == "дымовые_газы":
        # Свойства дымовых газов при температуре плёнки
        lambda_gas = 0.04 * (T_film_K / 273.15)**0.7  # Вт/(м·К)
        nu_gas = 15e-6 * (T_film_K / 273.15)**1.5     # м²/с
        Pr_gas = 0.65
    elif gas.gas_type == "воздух":
        lambda_gas = 0.026 * (T_film_K / 300)**0.8
        nu_gas = 15.9e-6 * (T_film_K / 273.15)**1.5
        Pr_gas = 0.71
    else:
        # Пользовательские свойства или значения по умолчанию
        lambda_gas = gas.lambda_gas or 0.05
        nu_gas = gas.nu_gas or 30e-6
        Pr_gas = gas.Pr_gas or 0.7
    
    d_outer_m = pipe.outer_diameter_mm / 1000
    
    # Число Рейнольдса
    Re = gas.velocity * d_outer_m / nu_gas
    
    # Выбор критериального уравнения в зависимости от типа обтекания
    if flow.flow_type == "поперечное_одиночная":
        # Одиночная труба в поперечном потоке
        if Re >= 1000:
            # Формула Жукаускаса
            Nu = 0.25 * Re**0.6 * Pr_gas**0.38
        else:
            Nu = 0.5 * Re**0.5 * Pr_gas**0.38
            
    elif flow.flow_type == "поперечное_пучок":
        # Пучок труб (коридорный или шахматный)
        if flow.tube_arrangement == "коридорный":
            C = 0.25
        else:  # шахматный
            C = 0.4
        Nu = C * Re**0.6 * Pr_gas**0.38
        
    else:  # продольное омывание
        if Re > 10000:
            Nu = 0.023 * Re**0.8 * Pr_gas**0.4
        else:
            Nu = 0.15 * Re**0.33 * Pr_gas**0.43 * (Re * Pr_gas * d_outer_m / input_data.pipe_geometry.length_m)**0.1
    
    alpha_conv = Nu * lambda_gas / d_outer_m
    
    if input_data.verbose:
        print(f"  [Расчёт] Re = {Re:.0f}, Nu = {Nu:.2f}, α_конв = {alpha_conv:.2f} Вт/(м²·К)")
    
    return alpha_conv


def calculate_alpha_radiation(input_data: HeatTransferInput) -> float:
    """
    Рассчитывает коэффициент теплоотдачи излучением
    Возвращает: alpha_rad, Вт/(м²·К)
    """
    if not input_data.include_radiation:
        return 0.0
    
    gas = input_data.gas
    T_gas = gas.temperature + 273.15
    T_wall_outer = input_data.boundary.inner_wall_temperature + 50 + 273.15  # Приближение
    
    # Постоянная Стефана-Больцмана
    sigma = 5.67e-8
    
    # Степень черноты для окисленной стали (приближённо)
    epsilon_wall = 0.8
    
    # Степень черноты газа (упрощённо)
    if gas.contains_h2o_co2 and gas.temperature > 300:
        epsilon_gas = 0.3  # Для дымовых газов при 800°C
    else:
        epsilon_gas = 0.1
    
    # Результирующий коэффициент теплоотдачи излучением
    alpha_rad = sigma * epsilon_wall * epsilon_gas * (T_gas**4 - T_wall_outer**4) / (T_gas - T_wall_outer)
    
    if input_data.verbose:
        print(f"  [Расчёт] α_изл = {alpha_rad:.2f} Вт/(м²·К)")
    
    return max(alpha_rad, 0.0)


def calculate_overall_coefficient(input_data: HeatTransferInput) -> float:
    """
    Рассчитывает общий линейный коэффициент теплопередачи K_l
    Возвращает: K_l, Вт/(м·К)
    """
    pipe = input_data.pipe_geometry
    material = input_data.pipe_material
    boundary = input_data.boundary
    
    d1 = pipe.inner_diameter_mm / 1000
    d2 = pipe.outer_diameter_mm / 1000
    delta_wall = (d2 - d1) / 2
    
    # Коэффициенты теплоотдачи снаружи (конвекция + излучение)
    alpha_conv = calculate_alpha_convection_gas(input_data)
    alpha_rad = calculate_alpha_radiation(input_data)
    alpha_out = alpha_conv + alpha_rad
    
    # Коэффициент теплоотдачи внутри (упрощённо, для стенки с заданной температурой → большое сопротивление)
    if boundary.inner_wall_temperature is not None:
        # Внутренняя стенка имеет фиксированную температуру → α_in стремится к бесконечности
        alpha_in = float('inf')
        R_in = 0
    else:
        # Если внутри течёт среда (упрощённый расчёт)
        alpha_in = 500  # Вт/(м²·К) для воды, для воздуха ~50
        R_in = 1 / (alpha_in * d1)
    
    # Термическое сопротивление стенки (цилиндрическая стенка)
    if d2/d1 > 1.5:
        R_wall = math.log(d2 / d1) / (2 * material.lambda_wall)
    else:
        # Тонкостенная труба - приближение плоской стенки
        R_wall = delta_wall / (material.lambda_wall)
    
    # Термическое сопротивление наружной теплоотдачи
    R_out = 1 / (alpha_out * d2)
    
    # Линейный коэффициент теплопередачи
    K_l = 1 / (R_in + R_wall + R_out)
    
    if input_data.verbose:
        print(f"\n  [Расчёт] α_нар = {alpha_out:.2f} Вт/(м²·К) (конв={alpha_conv:.1f} + изл={alpha_rad:.1f})")
        print(f"  [Расчёт] R_стенки = {R_wall:.5f} (м·К)/Вт")
        print(f"  [Расчёт] K_l = {K_l:.3f} Вт/(м·К)")
    
    return K_l


def calculate_heat_flow(input_data: HeatTransferInput) -> float:
    """
    Главная функция расчёта теплового потока
    Возвращает: Q, Вт
    """
    print("\n" + "="*60)
    print("РАСЧЁТ ТЕПЛОПЕРЕДАЧИ ОТ ГАЗА К ТРУБЕ")
    print("="*60)
    
    # Вывод исходных данных
    print(f"\n📊 Исходные данные:")
    print(f"  Газ: {input_data.gas.gas_type}, T = {input_data.gas.temperature}°C, w = {input_data.gas.velocity} м/с")
    print(f"  Труба: Dн = {input_data.pipe_geometry.outer_diameter_mm} мм, Dвн = {input_data.pipe_geometry.inner_diameter_mm} мм, L = {input_data.pipe_geometry.length_m} м")
    print(f"  Материал: {input_data.pipe_material.material_name}, λ = {input_data.pipe_material.lambda_wall} Вт/(м·К)")
    print(f"  Условия: {input_data.flow.flow_type}")
    
    if input_data.boundary.inner_wall_temperature:
        print(f"  Граничные условия: T_стенки = {input_data.boundary.inner_wall_temperature}°C")
    else:
        print(f"  Граничные условия: внутри течёт {input_data.boundary.inner_fluid_type}")
    
    print(f"  Учёт излучения: {'Да' if input_data.include_radiation else 'Нет'}")
    
    # Расчёт
    K_l = calculate_overall_coefficient(input_data)
    
    # Разность температур
    delta_T = input_data.gas.temperature - input_data.boundary.inner_wall_temperature
    
    # Линейный тепловой поток
    q_l = K_l * math.pi * delta_T
    
    # Полный тепловой поток
    Q = q_l * input_data.pipe_geometry.length_m
    
    print(f"\n📈 Результаты расчёта:")
    print(f"  Линейная плотность теплового потока q_l = {q_l:.1f} Вт/м")
    print(f"  Полный тепловой поток Q = {Q:.0f} Вт ({Q/1000:.2f} кВт)")
    print("="*60 + "\n")
    
    return Q


# Для тестирования модуля
if __name__ == "__main__":
    from main import get_input_data
    data = get_input_data()
    Q = calculate_heat_flow(data)