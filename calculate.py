# -*- coding: utf-8 -*-
"""
Модуль расчёта теплопередачи для различных сценариев
"""

import math
from main import HeatTransferInput, CaseType


# ---------- Вспомогательные функции для газ-труба (существующие) ----------
def calculate_alpha_convection_gas(input_data: HeatTransferInput) -> float:
    """Коэффициент конвекции от газа к трубе (старая реализация)"""
    gas = input_data.gas
    pipe = input_data.pipe_geometry
    flow = input_data.flow

    T_gas = gas.temperature
    T_wall_outer = input_data.boundary.inner_wall_temperature + 50  # приближение
    T_film = (T_gas + T_wall_outer) / 2
    T_film_K = T_film + 273.15

    if gas.gas_type == "дымовые_газы":
        lambda_gas = 0.04 * (T_film_K / 273.15) ** 0.7
        nu_gas = 15e-6 * (T_film_K / 273.15) ** 1.5
        Pr_gas = 0.65
    elif gas.gas_type == "воздух":
        lambda_gas = 0.026 * (T_film_K / 300) ** 0.8
        nu_gas = 15.9e-6 * (T_film_K / 273.15) ** 1.5
        Pr_gas = 0.71
    else:
        lambda_gas = gas.lambda_gas or 0.05
        nu_gas = gas.nu_gas or 30e-6
        Pr_gas = gas.Pr_gas or 0.7

    d_outer_m = pipe.outer_diameter_mm / 1000
    Re = gas.velocity * d_outer_m / nu_gas

    if flow.flow_type == "поперечное_одиночная":
        if Re >= 1000:
            Nu = 0.25 * Re ** 0.6 * Pr_gas ** 0.38
        else:
            Nu = 0.5 * Re ** 0.5 * Pr_gas ** 0.38
    elif flow.flow_type == "поперечное_пучок":
        C = 0.25 if flow.tube_arrangement == "коридорный" else 0.4
        Nu = C * Re ** 0.6 * Pr_gas ** 0.38
    else:  # продольное
        if Re > 10000:
            Nu = 0.023 * Re ** 0.8 * Pr_gas ** 0.4
        else:
            Nu = 0.15 * Re ** 0.33 * Pr_gas ** 0.43 * (Re * Pr_gas * d_outer_m / input_data.pipe_geometry.length_m) ** 0.1

    alpha_conv = Nu * lambda_gas / d_outer_m
    if input_data.verbose:
        print(f"  [Расчёт] Re = {Re:.0f}, Nu = {Nu:.2f}, α_конв = {alpha_conv:.2f} Вт/(м²·К)")
    return alpha_conv


def calculate_alpha_radiation_gas(input_data: HeatTransferInput) -> float:
    """Коэффициент излучения для газ-труба (старая реализация)"""
    if not input_data.include_radiation:
        return 0.0
    gas = input_data.gas
    T_gas = gas.temperature + 273.15
    T_wall_outer = input_data.boundary.inner_wall_temperature + 50 + 273.15
    sigma = 5.67e-8
    epsilon_wall = 0.8
    epsilon_gas = 0.3 if (gas.contains_h2o_co2 and gas.temperature > 300) else 0.1
    alpha_rad = sigma * epsilon_wall * epsilon_gas * (T_gas**4 - T_wall_outer**4) / (T_gas - T_wall_outer)
    if input_data.verbose:
        print(f"  [Расчёт] α_изл = {alpha_rad:.2f} Вт/(м²·К)")
    return max(alpha_rad, 0.0)


def calculate_overall_coefficient_gas_to_pipe(input_data: HeatTransferInput) -> float:
    """K_l для газ-труба (старая реализация)"""
    pipe = input_data.pipe_geometry
    material = input_data.pipe_material
    boundary = input_data.boundary

    d1 = pipe.inner_diameter_mm / 1000
    d2 = pipe.outer_diameter_mm / 1000
    delta_wall = (d2 - d1) / 2

    alpha_conv = calculate_alpha_convection_gas(input_data)
    alpha_rad = calculate_alpha_radiation_gas(input_data)
    alpha_out = alpha_conv + alpha_rad

    if boundary.inner_wall_temperature is not None:
        alpha_in = float('inf')
        R_in = 0
    else:
        alpha_in = 500  # упрощённо
        R_in = 1 / (alpha_in * d1)

    if d2 / d1 > 1.5:
        R_wall = math.log(d2 / d1) / (2 * material.lambda_wall)
    else:
        R_wall = delta_wall / material.lambda_wall

    R_out = 1 / (alpha_out * d2)
    K_l = 1 / (R_in + R_wall + R_out)

    if input_data.verbose:
        print(f"\n  [Расчёт] α_нар = {alpha_out:.2f} Вт/(м²·К) (конв={alpha_conv:.1f} + изл={alpha_rad:.1f})")
        print(f"  [Расчёт] R_стенки = {R_wall:.5f} (м·К)/Вт")
        print(f"  [Расчёт] K_l = {K_l:.3f} Вт/(м·К)")
    return K_l


# ---------- Новые расчётные функции ----------
def calculate_surface_radiation(input_data: HeatTransferInput) -> float:
    params = input_data.surface_radiation
    if not params:
        raise ValueError("Отсутствуют параметры излучения поверхностей")

    # Если одна из поверхностей идеально отражающая, теплообмена нет
    if params.epsilon1 == 0 or params.epsilon2 == 0:
        return 0.0
    
    sigma = 5.67e-8
    T1_K = params.T1 + 273.15
    T2_K = params.T2 + 273.15

    # Для двух серых тел, бесконечных параллельных пластин (при F12=1)
    # Общая формула: Q = sigma * (T1^4 - T2^4) / ( (1-eps1)/(eps1*A1) + 1/(A1*F12) + (1-eps2)/(eps2*A2) )
    # При A1 = A2 = A, F12=1:
    # Q = sigma * A * (T1^4 - T2^4) / (1/eps1 + 1/eps2 - 1)
    # Для общего случая с F12 и площадями:
    A1 = params.area
    # Предположим, что площади равны, если не задано иначе
    A2 = A1
    # Если площади разные, нужно передавать отдельно, но для простоты используем A1.
    # При A1 != A2 формула сложнее, но мы используем приближение с F12 и A1.
    # Q = sigma * (T1^4 - T2^4) / ( (1-eps1)/(eps1*A1) + 1/(A1*F12) + (1-eps2)/(eps2*A2) )
    # Если A2 не задано, считаем A2 = A1.
    denom = (1 - params.epsilon1) / (params.epsilon1 * A1) + 1 / (A1 * params.F12) + (1 - params.epsilon2) / (params.epsilon2 * A2)
    Q = sigma * (T1_K**4 - T2_K**4) / denom
    Q = max(Q, 0.0)  # тепло идёт от горячего к холодному

    if input_data.verbose:
        print(f"\n[Расчёт излучения] Q = {Q:.2f} Вт")
    return Q


def calculate_wall_transfer(input_data: HeatTransferInput) -> float:
    """
    Теплопередача через плоскую стенку с конвекцией с двух сторон.
    Возвращает Q, Вт.
    """
    params = input_data.wall_transfer
    if not params:
        raise ValueError("Отсутствуют параметры теплопередачи через стенку")

    # Защита от деления на ноль
    if params.h_hot == 0 or params.h_cold == 0:
        return 0.0  # нет теплоотдачи с одной из сторон

    # Термические сопротивления
    R_conv1 = 1 / (params.h_hot * params.area)
    R_wall = params.wall_thickness / (params.wall_lambda * params.area)
    R_conv2 = 1 / (params.h_cold * params.area)
    R_total = R_conv1 + R_wall + R_conv2

    delta_T = params.T_hot_fluid - params.T_cold_fluid
    Q = delta_T / R_total
    Q = max(Q, 0.0)

    if input_data.verbose:
        print(f"\n[Расчёт через стенку] R_total = {R_total:.4f} К/Вт, Q = {Q:.2f} Вт")
    return Q


def calculate_convection(input_data: HeatTransferInput) -> float:
    """
    Расчёт конвективного теплообмена (вынужденная или свободная конвекция).
    Возвращает тепловой поток Q, Вт.
    """
    params = input_data.convection
    if not params:
        raise ValueError("Отсутствуют параметры конвекции")
    
    if params.characteristic_length == 0:
        return 0.0  # нет характерного размера – нет теплообмена

    # Определяем свойства жидкости при температуре плёнки
    T_film = (params.T_fluid + params.T_surface) / 2
    T_film_K = T_film + 273.15

    # Приближённые зависимости для воздуха
    if params.fluid_type == "воздух":
        lambda_fluid = 0.026 * (T_film_K / 300) ** 0.8
        nu_fluid = 15.9e-6 * (T_film_K / 273.15) ** 1.5
        Pr_fluid = 0.71
    elif params.fluid_type == "вода":
        # Очень грубо
        lambda_fluid = 0.6
        nu_fluid = 1e-6
        Pr_fluid = 7
    else:
        lambda_fluid = params.lambda_fluid or 0.05
        nu_fluid = params.nu_fluid or 30e-6
        Pr_fluid = params.Pr_fluid or 0.7

    # Выбор критериального уравнения в зависимости от геометрии и скорости
    L = params.characteristic_length
    if params.velocity > 0:
        # Вынужденная конвекция
        Re = params.velocity * L / nu_fluid
        if params.geometry == "плоская_пластина":
            if Re < 5e5:
                Nu = 0.664 * Re ** 0.5 * Pr_fluid ** (1/3)
            else:
                Nu = 0.037 * Re ** 0.8 * Pr_fluid ** (1/3)
        elif params.geometry == "труба_внутри" or params.geometry == "труба_снаружи":
            if Re > 10000:
                Nu = 0.023 * Re ** 0.8 * Pr_fluid ** 0.4
            else:
                Nu = 0.15 * Re ** 0.33 * Pr_fluid ** 0.43 * (Re * Pr_fluid * L / 1) ** 0.1  # приближение
        else:  # сфера
            Nu = 2 + 0.6 * Re ** 0.5 * Pr_fluid ** (1/3)
    else:
        # Свободная конвекция
        beta = 1 / T_film_K  # термический коэффициент расширения для газов
        g = 9.81
        Gr = g * beta * (params.T_fluid - params.T_surface) * L ** 3 / (nu_fluid ** 2)
        Ra = Gr * Pr_fluid
        if params.geometry == "плоская_пластина":
            Nu = 0.59 * Ra ** 0.25 if Ra < 1e9 else 0.1 * Ra ** (1/3)
        elif params.geometry == "труба_снаружи" or params.geometry == "труба_внутри":
            Nu = (0.6 + 0.387 * Ra ** (1/6) / (1 + (0.559 / Pr_fluid) ** (9/16)) ** (8/27)) ** 2
        else:  # сфера
            Nu = 2 + 0.43 * Ra ** 0.25

    alpha = Nu * lambda_fluid / L
    Q = alpha * (params.T_fluid - params.T_surface) * L * L  # приближённо площадь = L^2 (для простоты)
    # Для более точного расчёта нужно знать площадь, но пока так.
    # Можно передавать площадь отдельно, но для простоты используем L^2 как характерную площадь.
    Q = max(Q, 0.0)

    if input_data.verbose:
        print(f"\n[Расчёт конвекции] Re = {Re if params.velocity > 0 else 0:.0f}, Nu = {Nu:.2f}, α = {alpha:.2f} Вт/(м²·К), Q = {Q:.2f} Вт")
    return Q


# ---------- Главная функция-диспетчер ----------
def calculate_heat_flow(input_data: HeatTransferInput) -> float:
    """
    Главная функция расчёта теплового потока в зависимости от типа задачи.
    Возвращает Q, Вт.
    """
    print("\n" + "=" * 60)
    print("РАСЧЁТ ТЕПЛОПЕРЕДАЧИ")
    print("=" * 60)
    print(f"Тип задачи: {input_data.case_type}")

    if input_data.case_type == CaseType.GAS_TO_PIPE:
        # Старый расчёт газ-труба
        # Вывод исходных данных (кратко)
        if input_data.verbose:
            print("\n📊 Исходные данные (газ-труба):")
            print(f"  Газ: {input_data.gas.gas_type}, T = {input_data.gas.temperature}°C, w = {input_data.gas.velocity} м/с")
            print(f"  Труба: Dн = {input_data.pipe_geometry.outer_diameter_mm} мм, Dвн = {input_data.pipe_geometry.inner_diameter_mm} мм, L = {input_data.pipe_geometry.length_m} м")
            print(f"  Материал: {input_data.pipe_material.material_name}, λ = {input_data.pipe_material.lambda_wall} Вт/(м·К)")
            print(f"  Условия: {input_data.flow.flow_type}")
            if input_data.boundary.inner_wall_temperature:
                print(f"  T_стенки = {input_data.boundary.inner_wall_temperature}°C")
            else:
                print(f"  Внутри: {input_data.boundary.inner_fluid_type}")
            print(f"  Учёт излучения: {'Да' if input_data.include_radiation else 'Нет'}")

        K_l = calculate_overall_coefficient_gas_to_pipe(input_data)
        delta_T = input_data.gas.temperature - input_data.boundary.inner_wall_temperature
        q_l = K_l * math.pi * delta_T
        Q = q_l * input_data.pipe_geometry.length_m

        if input_data.verbose:
            print(f"\n📈 Результат: Q = {Q:.0f} Вт ({Q/1000:.2f} кВт)")

    elif input_data.case_type == CaseType.SURFACE_TO_SURFACE:
        if input_data.verbose:
            params = input_data.surface_radiation
            print("\n📊 Исходные данные (излучение):")
            print(f"  T1 = {params.T1}°C, T2 = {params.T2}°C")
            print(f"  eps1 = {params.epsilon1}, eps2 = {params.epsilon2}, F12 = {params.F12}")
            print(f"  Площадь A1 = {params.area} м²")
        Q = calculate_surface_radiation(input_data)

    elif input_data.case_type == CaseType.WALL_TRANSFER:
        if input_data.verbose:
            params = input_data.wall_transfer
            print("\n📊 Исходные данные (стенка):")
            print(f"  Горячая жидкость: T = {params.T_hot_fluid}°C, h = {params.h_hot} Вт/(м²·К)")
            print(f"  Холодная жидкость: T = {params.T_cold_fluid}°C, h = {params.h_cold} Вт/(м²·К)")
            print(f"  Стенка: толщина = {params.wall_thickness} м, λ = {params.wall_lambda} Вт/(м·К), A = {params.area} м²")
        Q = calculate_wall_transfer(input_data)

    elif input_data.case_type == CaseType.CONVECTION_ONLY:
        if input_data.verbose:
            params = input_data.convection
            print("\n📊 Исходные данные (конвекция):")
            print(f"  Среда: {params.fluid_type}, T_fluid = {params.T_fluid}°C, T_surface = {params.T_surface}°C")
            print(f"  Скорость = {params.velocity} м/с, характерный размер = {params.characteristic_length} м")
            print(f"  Геометрия: {params.geometry}")
        Q = calculate_convection(input_data)

    else:
        raise ValueError(f"Неизвестный тип задачи: {input_data.case_type}")

    print("=" * 60 + "\n")
    return Q


# Для тестирования модуля
if __name__ == "__main__":
    from main import get_input_data_gas_to_pipe, get_input_data_surface_radiation, get_input_data_wall_transfer, get_input_data_convection

    print("Тест газ-труба:")
    data = get_input_data_gas_to_pipe()
    Q = calculate_heat_flow(data)

    print("\nТест излучение:")
    data2 = get_input_data_surface_radiation()
    Q2 = calculate_heat_flow(data2)

    print("\nТест стенка:")
    data3 = get_input_data_wall_transfer()
    Q3 = calculate_heat_flow(data3)

    print("\nТест конвекция:")
    data4 = get_input_data_convection()
    Q4 = calculate_heat_flow(data4)