import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from graphviz import Digraph
from PIL import Image, ImageTk
import os
import time

# ==============================
# Clase Paciente
# ==============================
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

# ==============================
# Clase Cola
# ==============================
class Cola:
    def __init__(self):
        self.items = []
        self.tiempo_total = 0

    def encolar(self, paciente):
        # Calcular tiempo de espera estimado
        paciente.calcular_tiempo_espera(self.tiempo_total)
        self.tiempo_total += paciente.tiempo
        self.items.append(paciente)

    def desencolar(self):
        if not self.esta_vacia():
            paciente = self.items.pop(0)
            self.tiempo_total -= paciente.tiempo
            # Actualizar tiempos de espera restantes
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

# ==============================
# Visualizador con Graphviz
# ==============================
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

