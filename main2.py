import tkinter as tk
from tkinter import ttk, messagebox
from graphviz import Digraph
from PIL import Image, ImageTk

class Paciente:
    def __init__(self, nombre, edad, especialidad):
        self.nombre = nombre
        self.edad = edad
        self.especialidad = especialidad
        self.tiempo = self.asignar_tiempo()
        self.tiempo_espera_estimado = 0

    def asignar_tiempo(self):
        tiempos = {
            "Medicina General": 10,
            "Pediatría": 15,
            "Ginecología": 20,
            "Dermatología": 25
        }
        return tiempos.get(self.especialidad, 10)
    
    def calcular_tiempo_espera(self, tiempo_anterior):
        self.tiempo_espera_estimado = tiempo_anterior + self.tiempo
        return self.tiempo_espera_estimado

    def __str__(self):
        return f"{self.nombre} ({self.edad} años) - {self.especialidad} [{self.tiempo} min]"

class Cola:
    def __init__(self):
        self.items = []
        self.tiempo_total = 0

    def encolar(self, paciente):
        paciente.calcular_tiempo_espera(self.tiempo_total)
        self.tiempo_total += paciente.tiempo
        self.items.append(paciente)

    def desencolar(self):
        if not self.esta_vacia():
            paciente = self.items.pop(0)
            self.tiempo_total -= paciente.tiempo
            for p in self.items:
                p.tiempo_espera_estimado -= paciente.tiempo
            return paciente
        return None

    def esta_vacia(self):
        return len(self.items) == 0

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)
    
    def obtener_tiempo_total(self):
        return self.tiempo_total

def graficar_cola(cola):
    dot = Digraph(comment="Cola de Pacientes")
    dot.attr(rankdir="LR")
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
    
    if len(cola) == 0:
        dot.node("0", "COLA VACÍA\nNo hay pacientes en espera", shape='oval', fillcolor='lightgrey')
    else:
        for i, paciente in enumerate(cola):
            label = f"{paciente.nombre}\nEdad: {paciente.edad}\n{paciente.especialidad}\n{paciente.tiempo} min\nEspera: {paciente.tiempo_espera_estimado} min"
            dot.node(str(i), label)
            if i > 0:
                dot.edge(str(i - 1), str(i))

    dot.render("cola_pacientes", format="png", cleanup=True)
    return "cola_pacientes.png"

class SistemaTurnosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Turnos Médicos")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        self.cola = Cola()
        
        self.crear_interfaz()
        
        self.actualizar_interfaz()
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        titulo = ttk.Label(main_frame, text="Sistema de Turnos Médicos", style='Header.TLabel')
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        form_frame = ttk.LabelFrame(main_frame, text="Registrar Nuevo Paciente", padding="10")
        form_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Edad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.edad_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.edad_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Especialidad:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.especialidad_var = tk.StringVar()
        especialidades = ["Medicina General", "Pediatría", "Ginecología", "Dermatología"]
        especialidad_combo = ttk.Combobox(form_frame, textvariable=self.especialidad_var, 
                                         values=especialidades, state="readonly")
        especialidad_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="Registrar Paciente", command=self.registrar_paciente).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Atender Siguiente", command=self.atender_paciente).grid(row=0, column=1, padx=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="Información de la Cola", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Pacientes en espera:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pacientes_espera_var = tk.StringVar(value="0")
        ttk.Label(info_frame, textvariable=self.pacientes_espera_var).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_frame, text="Tiempo total de espera:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tiempo_espera_var = tk.StringVar(value="0 min")
        ttk.Label(info_frame, textvariable=self.tiempo_espera_var).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        cola_frame = ttk.LabelFrame(main_frame, text="Visualización de la Cola (Graphviz)", padding="10")
        cola_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        cola_frame.columnconfigure(0, weight=1)
        cola_frame.rowconfigure(0, weight=1)
        
        self.canvas_frame = ttk.Frame(cola_frame)
        self.canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        
        self.paciente_actual_frame = ttk.LabelFrame(main_frame, text="Paciente en Atención", padding="10")
        self.paciente_actual_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.paciente_actual_text = tk.StringVar(value="No hay pacientes en atención")
        ttk.Label(self.paciente_actual_frame, textvariable=self.paciente_actual_text, 
                 wraplength=600, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        main_frame.rowconfigure(3, weight=1)
    
    def registrar_paciente(self):
        nombre = self.nombre_var.get().strip()
        edad = self.edad_var.get().strip()
        especialidad = self.especialidad_var.get()
        
        if not nombre:
            messagebox.showerror("Error", "Por favor ingrese el nombre del paciente.")
            return
        
        if not edad or not edad.isdigit():
            messagebox.showerror("Error", "Por favor ingrese una edad válida.")
            return
        
        if not especialidad:
            messagebox.showerror("Error", "Por favor seleccione una especialidad.")
            return
        
        paciente = Paciente(nombre, int(edad), especialidad)
        self.cola.encolar(paciente)
        
        self.actualizar_interfaz()
        
        self.nombre_var.set("")
        self.edad_var.set("")
        self.especialidad_var.set("")
        
        messagebox.showinfo("Éxito", f"Paciente {nombre} registrado correctamente.")
    
    def atender_paciente(self):
        if self.cola.esta_vacia():
            messagebox.showinfo("Info", "No hay pacientes en espera.")
            self.paciente_actual_text.set("No hay pacientes en atención")
            return
        
        paciente = self.cola.desencolar()
        
        info_text = f"Atendiendo a: {paciente.nombre} (Edad: {paciente.edad}) - " \
                   f"Especialidad: {paciente.especialidad} - " \
                   f"Tiempo estimado: {paciente.tiempo} minutos"
        self.paciente_actual_text.set(info_text)
        
        self.actualizar_interfaz()
        
        messagebox.showinfo("Paciente Atendido", f"Atendiendo a {paciente.nombre}")
    
    def actualizar_interfaz(self):
        self.pacientes_espera_var.set(str(len(self.cola)))
        self.tiempo_espera_var.set(f"{self.cola.obtener_tiempo_total()} min")
        
        imagen_path = graficar_cola(self.cola)
        self.mostrar_imagen_cola(imagen_path)
    
    def mostrar_imagen_cola(self, filename):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        try:
            image = Image.open(filename)
            if image.width > 800 or image.height > 400:
                image = image.resize((800, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            label = ttk.Label(self.canvas_frame, image=photo)
            label.image = photo
            label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        except Exception as e:
            label = ttk.Label(self.canvas_frame, text=f"Error al cargar imagen: {str(e)}")
            label.grid(row=0, column=0)

def main():
    root = tk.Tk()
    app = SistemaTurnosApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()