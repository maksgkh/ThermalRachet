# -*- coding: utf-8 -*-
"""
Графический интерфейс
"""

import tkinter as tk
from tkinter import ttk, messagebox
from main import (
    HeatTransferInput, GasParams, PipeGeometry, PipeMaterial,
    FlowConditions, BoundaryConditions, SurfaceRadiationParams,
    WallTransferParams, ConvectionParams, CaseType
)
from calculate import calculate_heat_flow


class HeatTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Универсальный расчёт теплопередачи")
        self.root.geometry("800x850")
        self.root.resizable(True, True)

        # Создаём вкладки для типов задач
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладки
        self.create_gas_tab()
        self.create_surface_tab()
        self.create_wall_tab()
        self.create_convection_tab()

        # Кнопка расчёта
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.calc_button = tk.Button(
            self.button_frame,
            text="▶ ВЫПОЛНИТЬ РАСЧЁТ",
            command=self.calculate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.calc_button.pack(fill=tk.X)

        # Статус
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к расчёту. Выберите тип задачи и заполните параметры.")
        self.status_bar = tk.Label(
            root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Поле результата (будет обновляться)
        self.result_text = None
        self.create_result_tab()

    # ---------- Вкладка "Газ-труба" (старая) ----------
    def create_gas_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Газ-труба")
        self.tab_gas = tab

        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Тип газа
        tk.Label(frame, text="Тип газа:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.gas_type = ttk.Combobox(frame, values=["дымовые_газы", "воздух", "азот", "пропан", "пользовательский"], width=25)
        self.gas_type.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.gas_type.set("дымовые_газы")

        tk.Label(frame, text="Температура газа (°C):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.gas_temp = tk.Entry(frame, width=15)
        self.gas_temp.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.gas_temp.insert(0, "800")

        tk.Label(frame, text="Скорость газа (м/с):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.gas_vel = tk.Entry(frame, width=15)
        self.gas_vel.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.gas_vel.insert(0, "5")

        self.contains_h2o_co2 = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Содержит H2O и CO2 (для излучения)",
                       variable=self.contains_h2o_co2).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        ttk.Separator(frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)

        tk.Label(frame, text="Пользовательские свойства газа:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        tk.Label(frame, text="λ (Вт/(м·К)):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.gas_lambda = tk.Entry(frame, width=15)
        self.gas_lambda.grid(row=6, column=1, sticky=tk.W, pady=2)
        tk.Label(frame, text="ν (м²/с × 10⁻⁶):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.gas_nu = tk.Entry(frame, width=15)
        self.gas_nu.grid(row=7, column=1, sticky=tk.W, pady=2)
        tk.Label(frame, text="Pr:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.gas_pr = tk.Entry(frame, width=15)
        self.gas_pr.grid(row=8, column=1, sticky=tk.W, pady=2)

        # Параметры трубы
        ttk.Separator(frame, orient='horizontal').grid(row=9, column=0, columnspan=2, sticky=tk.EW, pady=10)
        tk.Label(frame, text="Труба:", font=("Arial", 10, "bold")).grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=5)
        tk.Label(frame, text="Наружный диаметр (мм):").grid(row=11, column=0, sticky=tk.W, pady=2)
        self.pipe_outer = tk.Entry(frame, width=15)
        self.pipe_outer.grid(row=11, column=1, sticky=tk.W, pady=2)
        self.pipe_outer.insert(0, "57")
        tk.Label(frame, text="Внутренний диаметр (мм):").grid(row=12, column=0, sticky=tk.W, pady=2)
        self.pipe_inner = tk.Entry(frame, width=15)
        self.pipe_inner.grid(row=12, column=1, sticky=tk.W, pady=2)
        self.pipe_inner.insert(0, "50")
        tk.Label(frame, text="Длина (м):").grid(row=13, column=0, sticky=tk.W, pady=2)
        self.pipe_length = tk.Entry(frame, width=15)
        self.pipe_length.grid(row=13, column=1, sticky=tk.W, pady=2)
        self.pipe_length.insert(0, "1.0")

        # Материал
        tk.Label(frame, text="Материал:", font=("Arial", 10, "bold")).grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.material_type = ttk.Combobox(frame, values=["сталь_20", "нержавейка_12Х18Н10Т", "медь", "чугун", "пользовательский"], width=25)
        self.material_type.grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.material_type.set("сталь_20")
        tk.Label(frame, text="λ стенки (Вт/(м·К)):").grid(row=16, column=0, sticky=tk.W, pady=2)
        self.pipe_lambda = tk.Entry(frame, width=15)
        self.pipe_lambda.grid(row=16, column=1, sticky=tk.W, pady=2)
        self.pipe_lambda.insert(0, "51.5")

        # Условия омывания
        tk.Label(frame, text="Омывание:", font=("Arial", 10, "bold")).grid(row=17, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.flow_type = ttk.Combobox(frame, values=["поперечное_одиночная", "поперечное_пучок", "продольное"], width=25)
        self.flow_type.grid(row=18, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.flow_type.set("поперечное_одиночная")
        tk.Label(frame, text="Расположение пучка:").grid(row=19, column=0, sticky=tk.W, pady=2)
        self.tube_arrangement = ttk.Combobox(frame, values=["коридорный", "шахматный"], width=15)
        self.tube_arrangement.grid(row=19, column=1, sticky=tk.W, pady=2)
        self.tube_arrangement.set("коридорный")
        tk.Label(frame, text="Кол-во рядов:").grid(row=20, column=0, sticky=tk.W, pady=2)
        self.rows_count = tk.Entry(frame, width=10)
        self.rows_count.grid(row=20, column=1, sticky=tk.W, pady=2)
        self.rows_count.insert(0, "5")

        # Граничные условия
        tk.Label(frame, text="Граничные условия:", font=("Arial", 10, "bold")).grid(row=21, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.boundary_method = tk.StringVar(value="wall_temp")
        tk.Radiobutton(frame, text="Температура стенки", variable=self.boundary_method, value="wall_temp").grid(row=22, column=0, columnspan=2, sticky=tk.W)
        tk.Radiobutton(frame, text="Среда внутри", variable=self.boundary_method, value="inner_fluid").grid(row=23, column=0, columnspan=2, sticky=tk.W)
        tk.Label(frame, text="T стенки (°C):").grid(row=24, column=0, sticky=tk.W, pady=2)
        self.wall_temp = tk.Entry(frame, width=15)
        self.wall_temp.grid(row=24, column=1, sticky=tk.W, pady=2)
        self.wall_temp.insert(0, "200")
        tk.Label(frame, text="Тип среды внутри:").grid(row=25, column=0, sticky=tk.W, pady=2)
        self.inner_fluid = ttk.Combobox(frame, values=["вода", "пар", "воздух", "масло"], width=15)
        self.inner_fluid.grid(row=25, column=1, sticky=tk.W, pady=2)
        self.inner_fluid.set("вода")
        tk.Label(frame, text="T среды (°C):").grid(row=26, column=0, sticky=tk.W, pady=2)
        self.inner_temp = tk.Entry(frame, width=15)
        self.inner_temp.grid(row=26, column=1, sticky=tk.W, pady=2)
        tk.Label(frame, text="Скорость (м/с):").grid(row=27, column=0, sticky=tk.W, pady=2)
        self.inner_vel = tk.Entry(frame, width=15)
        self.inner_vel.grid(row=27, column=1, sticky=tk.W, pady=2)

        # Излучение
        self.include_radiation_gas = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Учитывать излучение (T>300°C)", variable=self.include_radiation_gas).grid(row=28, column=0, columnspan=2, sticky=tk.W, pady=5)

    # ---------- Вкладка "Излучение поверхностей" ----------
    def create_surface_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Излучение")
        self.tab_surface = tab

        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Параметры излучающих поверхностей", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(frame, text="Температура поверхности 1 (°C):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.surf_T1 = tk.Entry(frame, width=15)
        self.surf_T1.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.surf_T1.insert(0, "800")

        tk.Label(frame, text="Температура поверхности 2 (°C):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.surf_T2 = tk.Entry(frame, width=15)
        self.surf_T2.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.surf_T2.insert(0, "200")

        tk.Label(frame, text="Степень черноты ε1:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.surf_eps1 = tk.Entry(frame, width=15)
        self.surf_eps1.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.surf_eps1.insert(0, "0.8")

        tk.Label(frame, text="Степень черноты ε2:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.surf_eps2 = tk.Entry(frame, width=15)
        self.surf_eps2.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.surf_eps2.insert(0, "0.8")

        tk.Label(frame, text="Коэффициент облучения F12:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.surf_F12 = tk.Entry(frame, width=15)
        self.surf_F12.grid(row=5, column=1, sticky=tk.W, pady=5)
        self.surf_F12.insert(0, "1.0")

        tk.Label(frame, text="Площадь поверхности 1 (м²):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.surf_area = tk.Entry(frame, width=15)
        self.surf_area.grid(row=6, column=1, sticky=tk.W, pady=5)
        self.surf_area.insert(0, "1.0")

        # Пояснение
        tk.Label(frame, text="* Для параллельных пластин F12=1, площади равны", fg="gray").grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=10)

    # ---------- Вкладка "Теплопередача через стенку" ----------
    def create_wall_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Стенка")
        self.tab_wall = tab

        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Теплопередача через плоскую стенку", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(frame, text="Температура горячей жидкости (°C):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.wall_T_hot = tk.Entry(frame, width=15)
        self.wall_T_hot.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.wall_T_hot.insert(0, "800")

        tk.Label(frame, text="Температура холодной жидкости (°C):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.wall_T_cold = tk.Entry(frame, width=15)
        self.wall_T_cold.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.wall_T_cold.insert(0, "200")

        tk.Label(frame, text="Коэф. теплоотдачи h1 (Вт/(м²·К)):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.wall_h1 = tk.Entry(frame, width=15)
        self.wall_h1.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.wall_h1.insert(0, "100")

        tk.Label(frame, text="Коэф. теплоотдачи h2 (Вт/(м²·К)):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.wall_h2 = tk.Entry(frame, width=15)
        self.wall_h2.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.wall_h2.insert(0, "50")

        tk.Label(frame, text="Толщина стенки (м):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.wall_delta = tk.Entry(frame, width=15)
        self.wall_delta.grid(row=5, column=1, sticky=tk.W, pady=5)
        self.wall_delta.insert(0, "0.01")

        tk.Label(frame, text="Теплопроводность стенки (Вт/(м·К)):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.wall_lambda = tk.Entry(frame, width=15)
        self.wall_lambda.grid(row=6, column=1, sticky=tk.W, pady=5)
        self.wall_lambda.insert(0, "51.5")

        tk.Label(frame, text="Площадь стенки (м²):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.wall_area = tk.Entry(frame, width=15)
        self.wall_area.grid(row=7, column=1, sticky=tk.W, pady=5)
        self.wall_area.insert(0, "1.0")

    # ---------- Вкладка "Конвекция" ----------
    def create_convection_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Конвекция")
        self.tab_convection = tab

        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Конвективный теплообмен", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(frame, text="Тип жидкости:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.conv_fluid = ttk.Combobox(frame, values=["воздух", "вода", "масло", "пользовательский"], width=15)
        self.conv_fluid.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.conv_fluid.set("воздух")

        tk.Label(frame, text="Температура жидкости (°C):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.conv_Tf = tk.Entry(frame, width=15)
        self.conv_Tf.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.conv_Tf.insert(0, "800")

        tk.Label(frame, text="Температура поверхности (°C):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.conv_Ts = tk.Entry(frame, width=15)
        self.conv_Ts.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.conv_Ts.insert(0, "200")

        tk.Label(frame, text="Скорость потока (м/с) (0 - свободная конвекция):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.conv_vel = tk.Entry(frame, width=15)
        self.conv_vel.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.conv_vel.insert(0, "5")

        tk.Label(frame, text="Характерный размер (м):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.conv_L = tk.Entry(frame, width=15)
        self.conv_L.grid(row=5, column=1, sticky=tk.W, pady=5)
        self.conv_L.insert(0, "0.057")

        tk.Label(frame, text="Геометрия:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.conv_geom = ttk.Combobox(frame, values=["плоская_пластина", "труба_внутри", "труба_снаружи", "сфера"], width=18)
        self.conv_geom.grid(row=6, column=1, sticky=tk.W, pady=5)
        self.conv_geom.set("труба_снаружи")

        # Пользовательские свойства
        tk.Label(frame, text="Пользовательские свойства (опционально):", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=10)
        tk.Label(frame, text="λ (Вт/(м·К)):").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.conv_lambda = tk.Entry(frame, width=15)
        self.conv_lambda.grid(row=8, column=1, sticky=tk.W, pady=2)
        tk.Label(frame, text="ν (м²/с × 10⁻⁶):").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.conv_nu = tk.Entry(frame, width=15)
        self.conv_nu.grid(row=9, column=1, sticky=tk.W, pady=2)
        tk.Label(frame, text="Pr:").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.conv_pr = tk.Entry(frame, width=15)
        self.conv_pr.grid(row=10, column=1, sticky=tk.W, pady=2)

    # ---------- Вкладка "Результат" ----------
    def create_result_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Результат")
        self.tab_result = tab

        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(frame, wrap=tk.WORD, height=20, font=("Courier", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

        self.save_button = tk.Button(frame, text="💾 Сохранить результат в файл",
                                     command=self.save_result, state=tk.DISABLED,
                                     bg="#2196F3", fg="white")
        self.save_button.pack(pady=10)

    # ---------- Сбор данных ----------
    def get_input_data(self):
        """Создаёт HeatTransferInput в зависимости от активной вкладки"""
        current_tab = self.notebook.index(self.notebook.select())
        # Определяем тип по индексу: 0-газ, 1-излучение, 2-стенка, 3-конвекция, 4-результат
        if current_tab == 0:
            return self._get_gas_data()
        elif current_tab == 1:
            return self._get_surface_data()
        elif current_tab == 2:
            return self._get_wall_data()
        elif current_tab == 3:
            return self._get_convection_data()
        else:
            messagebox.showinfo("Информация", "Перейдите на вкладку с параметрами задачи.")
            return None

    def _get_gas_data(self):
        try:
            gas = GasParams(
                temperature=float(self.gas_temp.get()),
                velocity=float(self.gas_vel.get()),
                gas_type=self.gas_type.get(),
                lambda_gas=float(self.gas_lambda.get()) if self.gas_lambda.get() else None,
                nu_gas=float(self.gas_nu.get()) / 1e6 if self.gas_nu.get() else None,
                Pr_gas=float(self.gas_pr.get()) if self.gas_pr.get() else None,
                contains_h2o_co2=self.contains_h2o_co2.get()
            )
            pipe_geom = PipeGeometry(
                outer_diameter_mm=float(self.pipe_outer.get()),
                inner_diameter_mm=float(self.pipe_inner.get()),
                length_m=float(self.pipe_length.get())
            )
            pipe_mat = PipeMaterial(
                material_name=self.material_type.get(),
                lambda_wall=float(self.pipe_lambda.get())
            )
            flow = FlowConditions(
                flow_type=self.flow_type.get(),
                tube_arrangement=self.tube_arrangement.get() if self.flow_type.get() == "поперечное_пучок" else None,
                rows_count=int(self.rows_count.get()) if self.rows_count.get() else None
            )
            if self.boundary_method.get() == "wall_temp":
                boundary = BoundaryConditions(inner_wall_temperature=float(self.wall_temp.get()))
            else:
                boundary = BoundaryConditions(
                    inner_fluid_type=self.inner_fluid.get(),
                    inner_fluid_temperature=float(self.inner_temp.get()) if self.inner_temp.get() else None,
                    inner_fluid_velocity=float(self.inner_vel.get()) if self.inner_vel.get() else None
                )
            return HeatTransferInput(
                case_type=CaseType.GAS_TO_PIPE,
                gas=gas,
                pipe_geometry=pipe_geom,
                pipe_material=pipe_mat,
                flow=flow,
                boundary=boundary,
                include_radiation=self.include_radiation_gas.get(),
                verbose=False
            )
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректное значение: {e}")
            return None

    def _get_surface_data(self):
        try:
            params = SurfaceRadiationParams(
                T1=float(self.surf_T1.get()),
                T2=float(self.surf_T2.get()),
                epsilon1=float(self.surf_eps1.get()),
                epsilon2=float(self.surf_eps2.get()),
                F12=float(self.surf_F12.get()),
                area=float(self.surf_area.get())
            )
            return HeatTransferInput(
                case_type=CaseType.SURFACE_TO_SURFACE,
                surface_radiation=params,
                include_radiation=True,
                verbose=False
            )
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректное значение: {e}")
            return None

    def _get_wall_data(self):
        try:
            params = WallTransferParams(
                T_hot_fluid=float(self.wall_T_hot.get()),
                T_cold_fluid=float(self.wall_T_cold.get()),
                h_hot=float(self.wall_h1.get()),
                h_cold=float(self.wall_h2.get()),
                wall_thickness=float(self.wall_delta.get()),
                wall_lambda=float(self.wall_lambda.get()),
                area=float(self.wall_area.get())
            )
            return HeatTransferInput(
                case_type=CaseType.WALL_TRANSFER,
                wall_transfer=params,
                verbose=False
            )
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректное значение: {e}")
            return None

    def _get_convection_data(self):
        try:
            params = ConvectionParams(
                fluid_type=self.conv_fluid.get(),
                T_fluid=float(self.conv_Tf.get()),
                T_surface=float(self.conv_Ts.get()),
                velocity=float(self.conv_vel.get()),
                characteristic_length=float(self.conv_L.get()),
                geometry=self.conv_geom.get(),
                lambda_fluid=float(self.conv_lambda.get()) if self.conv_lambda.get() else None,
                nu_fluid=float(self.conv_nu.get()) / 1e6 if self.conv_nu.get() else None,
                Pr_fluid=float(self.conv_pr.get()) if self.conv_pr.get() else None
            )
            return HeatTransferInput(
                case_type=CaseType.CONVECTION_ONLY,
                convection=params,
                verbose=False
            )
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректное значение: {e}")
            return None

    # ---------- Расчёт и отображение ----------
    def calculate(self):
        input_data = self.get_input_data()
        if input_data is None:
            return

        try:
            self.status_var.set("Выполняется расчёт...")
            self.root.update()

            Q = calculate_heat_flow(input_data)

            # Формируем результат
            result_str = self.format_result(input_data, Q)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_str)
            self.save_button.config(state=tk.NORMAL)
            self.last_result = (input_data, Q)

            self.status_var.set(f"Расчёт выполнен. Q = {Q:.2f} Вт ({Q/1000:.3f} кВт)")
            # Переключиться на вкладку результата
            self.notebook.select(self.tab_result)
        except Exception as e:
            messagebox.showerror("Ошибка расчёта", str(e))
            self.status_var.set("Ошибка при расчёте")

    def format_result(self, input_data, Q):
        lines = []
        lines.append("=" * 60)
        lines.append("РЕЗУЛЬТАТ РАСЧЁТА ТЕПЛОПЕРЕДАЧИ")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Тип задачи: {input_data.case_type}")
        lines.append("")
        lines.append("ИСХОДНЫЕ ДАННЫЕ:")
        lines.append("-" * 40)

        if input_data.case_type == CaseType.GAS_TO_PIPE:
            lines.append(f"Газ: {input_data.gas.gas_type}, T={input_data.gas.temperature}°C, w={input_data.gas.velocity} м/с")
            lines.append(f"Труба: Dн={input_data.pipe_geometry.outer_diameter_mm} мм, Dвн={input_data.pipe_geometry.inner_diameter_mm} мм, L={input_data.pipe_geometry.length_m} м")
            lines.append(f"Материал: {input_data.pipe_material.material_name}, λ={input_data.pipe_material.lambda_wall} Вт/(м·К)")
            lines.append(f"Омывание: {input_data.flow.flow_type}")
            if input_data.boundary.inner_wall_temperature:
                lines.append(f"T_стенки = {input_data.boundary.inner_wall_temperature}°C")
            else:
                lines.append(f"Внутри: {input_data.boundary.inner_fluid_type}")
            lines.append(f"Излучение: {'Да' if input_data.include_radiation else 'Нет'}")
        elif input_data.case_type == CaseType.SURFACE_TO_SURFACE:
            p = input_data.surface_radiation
            lines.append(f"T1 = {p.T1}°C, T2 = {p.T2}°C")
            lines.append(f"ε1 = {p.epsilon1}, ε2 = {p.epsilon2}, F12 = {p.F12}")
            lines.append(f"Площадь A = {p.area} м²")
        elif input_data.case_type == CaseType.WALL_TRANSFER:
            p = input_data.wall_transfer
            lines.append(f"T_hot = {p.T_hot_fluid}°C, T_cold = {p.T_cold_fluid}°C")
            lines.append(f"h_hot = {p.h_hot} Вт/(м²·К), h_cold = {p.h_cold} Вт/(м²·К)")
            lines.append(f"Стенка: δ = {p.wall_thickness} м, λ = {p.wall_lambda} Вт/(м·К), A = {p.area} м²")
        elif input_data.case_type == CaseType.CONVECTION_ONLY:
            p = input_data.convection
            lines.append(f"Жидкость: {p.fluid_type}, Tf = {p.T_fluid}°C, Ts = {p.T_surface}°C")
            lines.append(f"Скорость = {p.velocity} м/с, L = {p.characteristic_length} м")
            lines.append(f"Геометрия: {p.geometry}")

        lines.append("")
        lines.append("РЕЗУЛЬТАТ:")
        lines.append("-" * 40)
        lines.append(f"Тепловой поток Q = {Q:.2f} Вт")
        lines.append(f"Тепловой поток Q = {Q/1000:.3f} кВт")
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def save_result(self):
        if hasattr(self, 'last_result'):
            input_data, Q = self.last_result
            lines = []
            lines.append("=" * 60)
            lines.append("ОТЧЁТ ПО РАСЧЁТУ ТЕПЛОПЕРЕДАЧИ")
            lines.append("=" * 60)
            lines.append("")
            lines.append(self.format_result(input_data, Q))
            lines.append("")
            from datetime import datetime
            lines.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("=" * 60)

            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Сохранено", "Результат сохранён в result.txt")
            self.status_var.set("Результат сохранён в result.txt")


def main():
    root = tk.Tk()
    app = HeatTransferApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()