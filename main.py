# -*- coding: utf-8 -*-
"""
Начальные параметры для расчета теплопередачи от газа к трубе
"""

from dataclasses import dataclass
from typing import Literal, Optional

#Параметры газа
@dataclass
class GasParams:
    """Характеристики горячего газа"""
    
    # Основные
    temperature: float          # Температура газа, °C
    velocity: float             # Скорость потока газа, м/с
    
    # Тип газа (для автоматического подбора свойств)
    gas_type: Literal["дымовые_газы", "воздух", "азот", "пропан", "пользовательский"] = "дымовые_газы"
    
    # Если gas_type = "пользовательский" — нужно задать теплофизические свойства при средней температуре
    lambda_gas: Optional[float] = None   # Теплопроводность газа, Вт/(м·К)
    nu_gas: Optional[float] = None       # Кинематическая вязкость, м²/с
    Pr_gas: Optional[float] = None       # Число Прандтля (для газов ~0.7)
    
    # Для учета излучения (важно при T > 300°C)
    contains_h2o_co2: bool = True        # Содержит ли газ водяные пары и CO2?
    partial_pressure_h2o: Optional[float] = None  # Парциальное давление H2O, бар
    partial_pressure_co2: Optional[float] = None  # Парциальное давление CO2, бар
    emissivity_gas: Optional[float] = None        # Степень черноты газа (если известна)

# Параметры трубы
@dataclass
class PipeGeometry:
    """Геометрические размеры трубы"""
    
    outer_diameter_mm: float     # Наружный диаметр, мм
    inner_diameter_mm: float      # Внутренний диаметр, мм
    length_m: float               # Длина трубы, м


@dataclass
class PipeMaterial:
    """Материал стенки трубы"""
    
    material_name: Literal["сталь_20", "нержавейка_12Х18Н10Т", "медь", "чугун", "пользовательский"] = "сталь_20"
    lambda_wall: Optional[float] = None   # Коэффициент теплопроводности стенки, Вт/(м·К)
    # Для пользовательского материала нужно указать lambda_wall


# Условия истечения газа
@dataclass
class FlowConditions:
    """Как газ обтекает трубу"""
    
    # Ориентация потока
    flow_type: Literal["поперечное_одиночная", "поперечное_пучок", "продольное"] = "поперечное_одиночная"
    
    # Для пучка труб (если flow_type = "поперечное_пучок")
    tube_arrangement: Optional[Literal["коридорный", "шахматный"]] = None
    rows_count: Optional[int] = None          # Количество рядов труб по ходу газа
    relative_pitch_s1: Optional[float] = None  # Относительный поперечный шаг S1/d
    relative_pitch_s2: Optional[float] = None  # Относительный продольный шаг S2/d

# Граничные условия
@dataclass
class BoundaryConditions:
    """Условия на внутренней поверхности трубы"""
    
    # Вариант 1: известна температура внутренней стенки
    inner_wall_temperature: Optional[float] = None   # °C
    
    # Вариант 2: известна среда внутри трубы (тогда будет рассчитана стенка)
    inner_fluid_temperature: Optional[float] = None   # °C
    inner_fluid_velocity: Optional[float] = None      # м/с
    inner_fluid_type: Literal["вода", "пар", "воздух", "масло"] = "вода"


# ----------------------------------------------------------------------
# 5. Общая структура входных данных
# ----------------------------------------------------------------------
@dataclass
class HeatTransferInput:
    """Все начальные параметры для расчёта"""
    
    gas: GasParams
    pipe_geometry: PipeGeometry
    pipe_material: PipeMaterial
    flow: FlowConditions
    boundary: BoundaryConditions
    
    # Дополнительные флаги
    include_radiation: bool = True      # Учитывать излучение (рекомендуется для газов >300°C)
    verbose: bool = True                # Выводить промежуточные результаты


# ======================================================================
# Пример заполнения (конкретные числа)
# ======================================================================
if __name__ == "__main__":
    
    # Создаем объект с начальными параметрами
    input_data = HeatTransferInput(
        gas=GasParams(
            temperature=800.0,          # °C
            velocity=5.0,               # м/с
            gas_type="дымовые_газы",
            contains_h2o_co2=True
        ),
        pipe_geometry=PipeGeometry(
            outer_diameter_mm=57.0,
            inner_diameter_mm=50.0,
            length_m=1.0
        ),
        pipe_material=PipeMaterial(
            material_name="сталь_20",
            lambda_wall=51.5            # Вт/(м·К) для стали 20
        ),
        flow=FlowConditions(
            flow_type="поперечное_одиночная"
        ),
        boundary=BoundaryConditions(
            inner_wall_temperature=200.0   # °C (задаем температуру внутренней стенки)
        ),
        include_radiation=True,
        verbose=True
    )
    
    # Выведем структуру для проверки
    print("Начальные параметры загружены:")
    print(f"Газ: {input_data.gas.gas_type}, T={input_data.gas.temperature}°C, w={input_data.gas.velocity} м/с")
    print(f"Труба: Dнар={input_data.pipe_geometry.outer_diameter_mm} мм, Dвн={input_data.pipe_geometry.inner_diameter_mm} мм, L={input_data.pipe_geometry.length_m} м")
    print(f"Условия: {input_data.flow.flow_type}, учитывать излучение = {input_data.include_radiation}")
    
