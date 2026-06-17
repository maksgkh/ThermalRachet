# -*- coding: utf-8 -*-
"""
Начальные параметры для расчёта теплопередачи (обобщённый)
"""

from dataclasses import dataclass
from typing import Literal, Optional


# ----------------------------------------------------------------------
# Определение типов задач
# ----------------------------------------------------------------------
class CaseType:
    GAS_TO_PIPE = "gas_to_pipe"
    SURFACE_TO_SURFACE = "surface_to_surface"
    WALL_TRANSFER = "wall_transfer"
    CONVECTION_ONLY = "convection_only"


# ----------------------------------------------------------------------
# 1. Параметры газообразной среды (для газ-труба)
# ----------------------------------------------------------------------
@dataclass
class GasParams:
    temperature: float          # Температура газа, °C
    velocity: float             # Скорость потока газа, м/с
    gas_type: Literal["дымовые_газы", "воздух", "азот", "пропан", "пользовательский"] = "дымовые_газы"
    lambda_gas: Optional[float] = None   # Теплопроводность газа, Вт/(м·К)
    nu_gas: Optional[float] = None       # Кинематическая вязкость, м²/с
    Pr_gas: Optional[float] = None       # Число Прандтля
    contains_h2o_co2: bool = True        # Содержит ли газ водяные пары и CO2?


@dataclass
class PipeGeometry:
    outer_diameter_mm: float
    inner_diameter_mm: float
    length_m: float


@dataclass
class PipeMaterial:
    material_name: Literal["сталь_20", "нержавейка_12Х18Н10Т", "медь", "чугун", "пользовательский"] = "сталь_20"
    lambda_wall: Optional[float] = None   # Коэффициент теплопроводности стенки, Вт/(м·К)


@dataclass
class FlowConditions:
    flow_type: Literal["поперечное_одиночная", "поперечное_пучок", "продольное"] = "поперечное_одиночная"
    tube_arrangement: Optional[Literal["коридорный", "шахматный"]] = None
    rows_count: Optional[int] = None


@dataclass
class BoundaryConditions:
    inner_wall_temperature: Optional[float] = None   # °C
    inner_fluid_temperature: Optional[float] = None   # °C
    inner_fluid_velocity: Optional[float] = None      # м/с
    inner_fluid_type: Literal["вода", "пар", "воздух", "масло"] = "вода"


# ----------------------------------------------------------------------
# 2. Параметры для излучения между поверхностями
# ----------------------------------------------------------------------
@dataclass
class SurfaceRadiationParams:
    T1: float          # температура поверхности 1, °C
    T2: float          # температура поверхности 2, °C
    epsilon1: float    # степень черноты поверхности 1
    epsilon2: float    # степень черноты поверхности 2
    F12: float         # коэффициент облучения (доля энергии поверхности 1, попадающая на 2)
    area: float        # площадь поверхности 1, м² (или эффективная)


# ----------------------------------------------------------------------
# 3. Параметры теплопередачи через плоскую стенку
# ----------------------------------------------------------------------
@dataclass
class WallTransferParams:
    T_hot_fluid: float          # температура горячей жидкости, °C
    T_cold_fluid: float         # температура холодной жидкости, °C
    h_hot: float                # коэф. теплоотдачи с горячей стороны, Вт/(м²·К)
    h_cold: float               # коэф. теплоотдачи с холодной стороны, Вт/(м²·К)
    wall_thickness: float       # толщина стенки, м
    wall_lambda: float          # теплопроводность материала стенки, Вт/(м·К)
    area: float                 # площадь поверхности, м²


# ----------------------------------------------------------------------
# 4. Параметры конвективного теплообмена
# ----------------------------------------------------------------------
@dataclass
class ConvectionParams:
    fluid_type: str              # "воздух", "вода", "масло" и т.п.
    T_fluid: float              # температура жидкости, °C
    T_surface: float            # температура поверхности, °C
    velocity: float             # скорость потока, м/с (0 – свободная конвекция)
    characteristic_length: float  # характерный размер, м
    geometry: Literal["плоская_пластина", "труба_внутри", "труба_снаружи", "сфера"] = "плоская_пластина"
    # Дополнительные свойства (если не заданы, используются приближения)
    lambda_fluid: Optional[float] = None   # Вт/(м·К)
    nu_fluid: Optional[float] = None       # м²/с
    Pr_fluid: Optional[float] = None


# ----------------------------------------------------------------------
# 5. Общая структура ввода
# ----------------------------------------------------------------------
@dataclass
class HeatTransferInput:
    case_type: str = CaseType.GAS_TO_PIPE
    include_radiation: bool = True
    verbose: bool = True

    # Старые поля для газ-труба
    gas: Optional[GasParams] = None
    pipe_geometry: Optional[PipeGeometry] = None
    pipe_material: Optional[PipeMaterial] = None
    flow: Optional[FlowConditions] = None
    boundary: Optional[BoundaryConditions] = None

    # Новые поля
    surface_radiation: Optional[SurfaceRadiationParams] = None
    wall_transfer: Optional[WallTransferParams] = None
    convection: Optional[ConvectionParams] = None


# ======================================================================
# Пример данных для тестирования (газ-труба)
# ======================================================================
def get_input_data_gas_to_pipe():
    return HeatTransferInput(
        case_type=CaseType.GAS_TO_PIPE,
        gas=GasParams(temperature=800.0, velocity=5.0, gas_type="дымовые_газы", contains_h2o_co2=True),
        pipe_geometry=PipeGeometry(outer_diameter_mm=57.0, inner_diameter_mm=50.0, length_m=1.0),
        pipe_material=PipeMaterial(material_name="сталь_20", lambda_wall=51.5),
        flow=FlowConditions(flow_type="поперечное_одиночная"),
        boundary=BoundaryConditions(inner_wall_temperature=200.0),
        include_radiation=True,
        verbose=True
    )


# Пример для излучения
def get_input_data_surface_radiation():
    return HeatTransferInput(
        case_type=CaseType.SURFACE_TO_SURFACE,
        surface_radiation=SurfaceRadiationParams(
            T1=800.0, T2=200.0,
            epsilon1=0.8, epsilon2=0.8,
            F12=1.0, area=1.0
        ),
        include_radiation=True,
        verbose=True
    )


# Пример для стенки
def get_input_data_wall_transfer():
    return HeatTransferInput(
        case_type=CaseType.WALL_TRANSFER,
        wall_transfer=WallTransferParams(
            T_hot_fluid=800.0, T_cold_fluid=200.0,
            h_hot=100.0, h_cold=50.0,
            wall_thickness=0.01, wall_lambda=51.5,
            area=1.0
        ),
        verbose=True
    )


# Пример для конвекции
def get_input_data_convection():
    return HeatTransferInput(
        case_type=CaseType.CONVECTION_ONLY,
        convection=ConvectionParams(
            fluid_type="воздух",
            T_fluid=800.0, T_surface=200.0,
            velocity=5.0,
            characteristic_length=0.057,
            geometry="труба_снаружи"
        ),
        verbose=True
    )