# -*- coding: utf-8 -*-
"""
Начальные параметры для расчета теплопередачи от газа к трубе
"""

from dataclasses import dataclass
from typing import Literal, Optional

# ----------------------------------------------------------------------
# 1. Параметры газообразной среды
# ----------------------------------------------------------------------
@dataclass
class GasParams:
    """Характеристики горячего газа"""
    temperature: float          # Температура газа, °C
    velocity: float             # Скорость потока газа, м/с
    gas_type: Literal["дымовые_газы", "воздух", "азот", "пропан", "пользовательский"] = "дымовые_газы"
    lambda_gas: Optional[float] = None   # Теплопроводность газа, Вт/(м·К)
    nu_gas: Optional[float] = None       # Кинематическая вязкость, м²/с
    Pr_gas: Optional[float] = None       # Число Прандтля
    contains_h2o_co2: bool = True        # Содержит ли газ водяные пары и CO2?

# ----------------------------------------------------------------------
# 2. Параметры трубы
# ----------------------------------------------------------------------
@dataclass
class PipeGeometry:
    """Геометрические размеры трубы"""
    outer_diameter_mm: float     # Наружный диаметр, мм
    inner_diameter_mm: float     # Внутренний диаметр, мм
    length_m: float              # Длина трубы, м

@dataclass
class PipeMaterial:
    """Материал стенки трубы"""
    material_name: Literal["сталь_20", "нержавейка_12Х18Н10Т", "медь", "чугун", "пользовательский"] = "сталь_20"
    lambda_wall: Optional[float] = None   # Коэффициент теплопроводности стенки, Вт/(м·К)

# ----------------------------------------------------------------------
# 3. Условия омывания
# ----------------------------------------------------------------------
@dataclass
class FlowConditions:
    """Как газ обтекает трубу"""
    flow_type: Literal["поперечное_одиночная", "поперечное_пучок", "продольное"] = "поперечное_одиночная"
    tube_arrangement: Optional[Literal["коридорный", "шахматный"]] = None
    rows_count: Optional[int] = None

# ----------------------------------------------------------------------
# 4. Граничные условия
# ----------------------------------------------------------------------
@dataclass
class BoundaryConditions:
    """Условия на внутренней поверхности трубы"""
    inner_wall_temperature: Optional[float] = None   # °C
    inner_fluid_temperature: Optional[float] = None   # °C
    inner_fluid_velocity: Optional[float] = None      # м/с
    inner_fluid_type: Literal["вода", "пар", "воздух", "масло"] = "вода"

# ----------------------------------------------------------------------
# 5. Общая структура
# ----------------------------------------------------------------------
@dataclass
class HeatTransferInput:
    """Все начальные параметры для расчёта"""
    gas: GasParams
    pipe_geometry: PipeGeometry
    pipe_material: PipeMaterial
    flow: FlowConditions
    boundary: BoundaryConditions
    include_radiation: bool = True
    verbose: bool = True


# ======================================================================
# КОНКРЕТНЫЕ ДАННЫЕ ДЛЯ РАСЧЁТА (меняйте здесь!)
# ======================================================================
def get_input_data():
    """Возвращает объект с начальными параметрами"""
    
    return HeatTransferInput(
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
            lambda_wall=51.5            # Вт/(м·К)
        ),
        flow=FlowConditions(
            flow_type="поперечное_одиночная"
        ),
        boundary=BoundaryConditions(
            inner_wall_temperature=200.0   # °C
        ),
        include_radiation=True,
        verbose=True
    )