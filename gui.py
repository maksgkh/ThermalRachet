# -*- coding: utf-8 -*-
"""
Графический интерфейс для расчёта теплопередачи
"""

import tkinter as tk
from tkinter import ttk, messagebox
from main import (
    HeatTransferInput, GasParams, PipeGeometry, 
    PipeMaterial, FlowConditions, BoundaryConditions
)
from calculate import calculate_heat_flow


class HeatTransferApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Расчёт теплопередачи от газа к трубе")
        self.root.geometry("750x800")
        self.root.resizable(True, True)
        
        # Создаём вкладки для группировки параметров
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаём вкладки
        self.create_gas_tab()      # Параметры газа
        self.create_pipe_tab()     # Параметры трубы
        self.create_flow_tab()     # Условия омывания
        self.create_boundary_tab() # Граничные условия
        self.create_result_tab()   # Результаты
        
        # Кнопка расчёта внизу окна
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
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к расчёту. Заполните параметры и нажмите кнопку.")
        self.status_bar = tk.Label(
            root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def create_gas_tab(self):
        """Вкладка: Параметры газа"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔥 Газ")
        
        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Тип газа
        tk.Label(frame, text="Тип газа:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.gas_type = ttk.Combobox(frame, values=["дымовые_газы", "воздух", "азот", "пропан", "пользовательский"], width=25)
        self.gas_type.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.gas_type.set("дымовые_газы")
        
        # Температура газа
        tk.Label(frame, text="Температура газа (°C):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.gas_temp = tk.Entry(frame, width=15)
        self.gas_temp.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.gas_temp.insert(0, "800")
        
        # Скорость газа
        tk.Label(frame, text="Скорость газа (м/с):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.gas_vel = tk.Entry(frame, width=15)
        self.gas_vel.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.gas_vel.insert(0, "5")
        
        # Флаг наличия H2O/CO2
        self.contains_h2o_co2 = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Содержит H2O и CO2 (для учёта излучения)", 
                      variable=self.contains_h2o_co2).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Разделитель
        ttk.Separator(frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # Пользовательские свойства (появляются при выборе "пользовательский")
        tk.Label(frame, text="Пользовательские свойства:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        tk.Label(frame, text="Теплопроводность λ (Вт/(м·К)):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.gas_lambda = tk.Entry(frame, width=15)
        self.gas_lambda.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        tk.Label(frame, text="Вязкость ν (м²/с × 10⁻⁶):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.gas_nu = tk.Entry(frame, width=15)
        self.gas_nu.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        tk.Label(frame, text="Число Прандтля Pr:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.gas_pr = tk.Entry(frame, width=15)
        self.gas_pr.grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # Подсказка
        tk.Label(frame, text="* Для пользовательского типа газа нужно заполнить свойства", 
                fg="gray", font=("Arial", 8)).grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=10)
    
    def create_pipe_tab(self):
        """Вкладка: Параметры трубы"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📏 Труба")
        
        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Диаметры
        tk.Label(frame, text="Наружный диаметр (мм):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pipe_outer = tk.Entry(frame, width=15)
        self.pipe_outer.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.pipe_outer.insert(0, "57")
        
        tk.Label(frame, text="Внутренний диаметр (мм):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pipe_inner = tk.Entry(frame, width=15)
        self.pipe_inner.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.pipe_inner.insert(0, "50")
        
        tk.Label(frame, text="Длина трубы (м):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pipe_length = tk.Entry(frame, width=15)
        self.pipe_length.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.pipe_length.insert(0, "1.0")
        
        # Разделитель
        ttk.Separator(frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # Материал трубы
        tk.Label(frame, text="Материал трубы:", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.material_type = ttk.Combobox(frame, values=["сталь_20", "нержавейка_12Х18Н10Т", "медь", "чугун", "пользовательский"], width=25)
        self.material_type.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.material_type.set("сталь_20")
        
        # Теплопроводность материала
        tk.Label(frame, text="Теплопроводность λ (Вт/(м·К)):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.pipe_lambda = tk.Entry(frame, width=15)
        self.pipe_lambda.grid(row=6, column=1, sticky=tk.W, pady=5)
        self.pipe_lambda.insert(0, "51.5")
        
        # Предустановленные значения
        tk.Label(frame, text="Значения для справки:", fg="blue", font=("Arial", 9)).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
        tk.Label(frame, text="• Сталь 20: 51.5 • Нержавейка: 16.0 • Медь: 390 • Чугун: 50", 
                fg="gray", font=("Arial", 8)).grid(row=8, column=0, columnspan=2, sticky=tk.W)
    
    def create_flow_tab(self):
        """Вкладка: Условия омывания"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💨 Омывание")
        
        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Тип обтекания
        tk.Label(frame, text="Тип обтекания:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.flow_type = ttk.Combobox(frame, values=["поперечное_одиночная", "поперечное_пучок", "продольное"], width=25)
        self.flow_type.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.flow_type.set("поперечное_одиночная")
        
        # Для пучка труб
        tk.Label(frame, text="Для пучка труб:", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        tk.Label(frame, text="Расположение:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tube_arrangement = ttk.Combobox(frame, values=["коридорный", "шахматный"], width=15)
        self.tube_arrangement.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.tube_arrangement.set("коридорный")
        
        tk.Label(frame, text="Количество рядов:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.rows_count = tk.Entry(frame, width=10)
        self.rows_count.grid(row=3, column=1, sticky=tk.W, pady=2)
        self.rows_count.insert(0, "5")
        
        # Подсказка
        tk.Label(frame, text="* Для одиночной трубы параметры пучка игнорируются", 
                fg="gray", font=("Arial", 8)).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
    
    def create_boundary_tab(self):
        """Вкладка: Граничные условия"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌡 Границы")
        
        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Способ задания
        tk.Label(frame, text="Способ задания граничных условий:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.boundary_method = tk.StringVar(value="wall_temp")
        tk.Radiobutton(frame, text="Задать температуру внутренней стенки", 
                      variable=self.boundary_method, value="wall_temp").grid(row=1, column=0, columnspan=2, sticky=tk.W)
        tk.Radiobutton(frame, text="Задать среду внутри трубы", 
                      variable=self.boundary_method, value="inner_fluid").grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Температура стенки
        tk.Label(frame, text="Температура внутренней стенки (°C):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.wall_temp = tk.Entry(frame, width=15)
        self.wall_temp.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.wall_temp.insert(0, "200")
        
        # Разделитель
        ttk.Separator(frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # Параметры внутренней среды
        tk.Label(frame, text="Параметры внутренней среды:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        tk.Label(frame, text="Тип среды:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.inner_fluid = ttk.Combobox(frame, values=["вода", "пар", "воздух", "масло"], width=15)
        self.inner_fluid.grid(row=6, column=1, sticky=tk.W, pady=2)
        self.inner_fluid.set("вода")
        
        tk.Label(frame, text="Температура среды (°C):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.inner_temp = tk.Entry(frame, width=15)
        self.inner_temp.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        tk.Label(frame, text="Скорость среды (м/с):").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.inner_vel = tk.Entry(frame, width=15)
        self.inner_vel.grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # Учёт излучения
        tk.Label(frame, text=" ", font=("Arial", 10, "bold")).grid(row=9, column=0, columnspan=2, pady=5)
        self.include_radiation = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Учитывать теплообмен излучением (рекомендуется для T > 300°C)", 
                      variable=self.include_radiation).grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def create_result_tab(self):
        """Вкладка: Результаты"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Результат")
        
        frame = tk.Frame(tab, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле для вывода результатов
        self.result_text = tk.Text(frame, wrap=tk.WORD, height=20, font=("Courier", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
        
        # Кнопка сохранения
        self.save_button = tk.Button(frame, text="💾 Сохранить результат в файл", 
                                     command=self.save_result, state=tk.DISABLED,
                                     bg="#2196F3", fg="white")
        self.save_button.pack(pady=10)
    
    def get_input_data(self):
        """Собирает данные из формы в объект HeatTransferInput"""
        try:
            # Газ
            gas = GasParams(
                temperature=float(self.gas_temp.get()),
                velocity=float(self.gas_vel.get()),
                gas_type=self.gas_type.get(),
                lambda_gas=float(self.gas_lambda.get()) if self.gas_lambda.get() else None,
                nu_gas=float(self.gas_nu.get()) / 1e6 if self.gas_nu.get() else None,
                Pr_gas=float(self.gas_pr.get()) if self.gas_pr.get() else None,
                contains_h2o_co2=self.contains_h2o_co2.get()
            )
            
            # Труба
            pipe_geom = PipeGeometry(
                outer_diameter_mm=float(self.pipe_outer.get()),
                inner_diameter_mm=float(self.pipe_inner.get()),
                length_m=float(self.pipe_length.get())
            )
            
            # Материал
            pipe_mat = PipeMaterial(
                material_name=self.material_type.get(),
                lambda_wall=float(self.pipe_lambda.get())
            )
            
            # Условия омывания
            flow = FlowConditions(
                flow_type=self.flow_type.get(),
                tube_arrangement=self.tube_arrangement.get() if self.flow_type.get() == "поперечное_пучок" else None,
                rows_count=int(self.rows_count.get()) if self.rows_count.get() else None
            )
            
            # Граничные условия
            if self.boundary_method.get() == "wall_temp":
                boundary = BoundaryConditions(
                    inner_wall_temperature=float(self.wall_temp.get())
                )
            else:
                boundary = BoundaryConditions(
                    inner_fluid_type=self.inner_fluid.get(),
                    inner_fluid_temperature=float(self.inner_temp.get()) if self.inner_temp.get() else None,
                    inner_fluid_velocity=float(self.inner_vel.get()) if self.inner_vel.get() else None
                )
            
            return HeatTransferInput(
                gas=gas,
                pipe_geometry=pipe_geom,
                pipe_material=pipe_mat,
                flow=flow,
                boundary=boundary,
                include_radiation=self.include_radiation.get(),
                verbose=False  # В GUI не выводим в консоль
            )
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректное числовое значение:\n{e}")
            return None
    
    def calculate(self):
        """Выполняет расчёт и отображает результат"""
        # Получаем данные
        input_data = self.get_input_data()
        if input_data is None:
            return
        
        # Выполняем расчёт
        try:
            self.status_var.set("Выполняется расчёт...")
            self.root.update()
            
            Q = calculate_heat_flow(input_data)
            
            # Формируем текст результата
            result_str = self.format_result(input_data, Q)
            
            # Выводим в текстовое поле
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_str)
            
            # Сохраняем результат для последующего сохранения в файл
            self.last_result = (input_data, Q)
            self.save_button.config(state=tk.NORMAL)
            
            self.status_var.set(f"Расчёт выполнен. Тепловой поток Q = {Q:.0f} Вт ({Q/1000:.3f} кВт)")
            
        except Exception as e:
            messagebox.showerror("Ошибка расчёта", str(e))
            self.status_var.set("Ошибка при расчёте")
    
    def format_result(self, input_data, Q):
        """Форматирует результат для отображения"""
        result = []
        result.append("="*60)
        result.append("РЕЗУЛЬТАТ РАСЧЁТА ТЕПЛОПЕРЕДАЧИ")
        result.append("="*60)
        result.append("")
        
        # Исходные данные
        result.append("ИСХОДНЫЕ ДАННЫЕ:")
        result.append("-"*40)
        result.append(f"Газ: {input_data.gas.gas_type}")
        result.append(f"  Температура: {input_data.gas.temperature} °C")
        result.append(f"  Скорость: {input_data.gas.velocity} м/с")
        result.append("")
        result.append(f"Труба:")
        result.append(f"  Наружный диаметр: {input_data.pipe_geometry.outer_diameter_mm} мм")
        result.append(f"  Внутренний диаметр: {input_data.pipe_geometry.inner_diameter_mm} мм")
        result.append(f"  Длина: {input_data.pipe_geometry.length_m} м")
        result.append(f"  Материал: {input_data.pipe_material.material_name}")
        result.append(f"  Теплопроводность стенки: {input_data.pipe_material.lambda_wall} Вт/(м·К)")
        result.append("")
        result.append(f"Условия омывания: {input_data.flow.flow_type}")
        if input_data.boundary.inner_wall_temperature:
            result.append(f"Температура стенки: {input_data.boundary.inner_wall_temperature} °C")
        result.append(f"Учёт излучения: {'Да' if input_data.include_radiation else 'Нет'}")
        result.append("")
        
        # Результат
        result.append("РЕЗУЛЬТАТЫ РАСЧЁТА:")
        result.append("-"*40)
        result.append(f"Тепловой поток Q = {Q:.0f} Вт")
        result.append(f"Тепловой поток Q = {Q/1000:.3f} кВт")
        result.append("")
        result.append("="*60)
        
        return "\n".join(result)
    
    def save_result(self):
        """Сохраняет результат в файл"""
        if hasattr(self, 'last_result'):
            input_data, Q = self.last_result
            
            # Формируем полный отчёт
            report = []
            report.append("="*60)
            report.append("РЕЗУЛЬТАТ РАСЧЁТА ТЕПЛОПЕРЕДАЧИ ОТ ГАЗА К ТРУБЕ")
            report.append("="*60)
            report.append("")
            
            # Исходные данные (подробно)
            report.append("ИСХОДНЫЕ ДАННЫЕ:")
            report.append("-"*40)
            report.append(f"Газ:")
            report.append(f"  Тип: {input_data.gas.gas_type}")
            report.append(f"  Температура: {input_data.gas.temperature} °C")
            report.append(f"  Скорость: {input_data.gas.velocity} м/с")
            if input_data.gas.lambda_gas:
                report.append(f"  Теплопроводность: {input_data.gas.lambda_gas} Вт/(м·К)")
            report.append(f"  Содержит H2O/CO2: {'Да' if input_data.gas.contains_h2o_co2 else 'Нет'}")
            report.append("")
            
            report.append(f"Труба:")
            report.append(f"  Наружный диаметр: {input_data.pipe_geometry.outer_diameter_mm} мм")
            report.append(f"  Внутренний диаметр: {input_data.pipe_geometry.inner_diameter_mm} мм")
            report.append(f"  Длина: {input_data.pipe_geometry.length_m} м")
            report.append(f"  Материал: {input_data.pipe_material.material_name}")
            report.append(f"  Теплопроводность стенки: {input_data.pipe_material.lambda_wall} Вт/(м·К)")
            report.append("")
            
            report.append(f"Условия омывания:")
            report.append(f"  Тип: {input_data.flow.flow_type}")
            if input_data.flow.tube_arrangement:
                report.append(f"  Расположение труб: {input_data.flow.tube_arrangement}")
            if input_data.flow.rows_count:
                report.append(f"  Количество рядов: {input_data.flow.rows_count}")
            report.append("")
            
            report.append(f"Граничные условия:")
            if input_data.boundary.inner_wall_temperature:
                report.append(f"  Температура стенки: {input_data.boundary.inner_wall_temperature} °C")
            else:
                report.append(f"  Среда внутри: {input_data.boundary.inner_fluid_type}")
                if input_data.boundary.inner_fluid_temperature:
                    report.append(f"    Температура: {input_data.boundary.inner_fluid_temperature} °C")
                if input_data.boundary.inner_fluid_velocity:
                    report.append(f"    Скорость: {input_data.boundary.inner_fluid_velocity} м/с")
            report.append(f"  Учёт излучения: {'Да' if input_data.include_radiation else 'Нет'}")
            report.append("")
            
            report.append("РЕЗУЛЬТАТЫ РАСЧЁТА:")
            report.append("-"*40)
            report.append(f"Тепловой поток Q: {Q:.0f} Вт")
            report.append(f"Тепловой поток Q: {Q/1000:.3f} кВт")
            report.append("")
            
            report.append("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
            report.append("-"*40)
            from datetime import datetime
            report.append(f"Дата и время расчёта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("="*60)
            
            # Сохраняем в файл
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(report))
            
            messagebox.showinfo("Сохранено", "Результат сохранён в файл result.txt")
            self.status_var.set("Результат сохранён в result.txt")


def main():
    root = tk.Tk()
    app = HeatTransferApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()