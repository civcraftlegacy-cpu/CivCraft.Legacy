# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import pygame
import os

ANCHO = 1200
ALTO = 800
FPS = 60
NOMBRE_JUEGO = "City Simulator Tycoon Gold Edition"

# --- COL_X: COORDENADAS PARA ALINEAR EL MENÚ ---
COL_X = {
    "btn": 80,        # Botón a la izquierda
    "nombre": 160,    # Nombre del edificio
    "costo": 380,     # Dinero
    "mant": 490,      # Mantenimiento
    "comida": 600,
    "agua": 700,
    "elec": 800,
    "felic": 900,
    "salud": 1000     # Última columna
}

# --- COLORES ---
NEGRO = (20, 20, 20)
BLANCO = (245, 245, 245)
GRIS_OSCURO = (40, 40, 40)
GRIS_CLARO = (170, 170, 170)
VERDE = (34, 139, 34)
VERDE_BRILLANTE = (50, 205, 50)
ORO = (255, 215, 0)
ROJO = (220, 20, 60)
AZUL = (30, 144, 255)
CIAN = (0, 255, 255)
AMARILLO = (255, 255, 0)
NARANJA = (255, 140, 0)
VIOLETA = (138, 43, 226)
VERDE_PASTO = (34, 139, 34)
GRIS_CARRETERA = (50, 50, 50)
BLANCO_LINEA = (245, 245, 245)


# --- LISTA DE EDIFICIOS (8 datos por fila: perfecto para tus columnas) ---
# Formato: [Nombre, Costo, Mantenimiento, Comida, Agua, Elec, Felicidad, Salud]
EDIFICACIONES = [
    # --- NIVEL 1 (Básico - Desbloqueado al inicio) ---
    ["Casa", 5000, 50, -10, -40, -30, 2, 0],
    ["Granja", 20000, 300, 400, -60, -20, 1, 1],
    ["Planta Agua", 45000, 500, 0, 600, -60, 1, 1],
    ["Central Elec.", 60000, 1000, 0, -30, 600, -2, -2],
    ["Almacen de Comida", 30000, 200, 0, 0, -5, 1, 0],
    ["Almacen de Agua", 30000, 200, 0, 0, -5, 1, 0],
    ["Almacen de Energia", 40000, 300, 0, 0, -10, 2, 0],  # Ahora produce 2 dinero

    # --- NIVEL 2 (Requiere Investigación: "Tecnología Urbana") ---
    ["Bloque Pisos", 18000, 200, -40, -120, -100, 1, -1],
    ["Granja Ind.", 55000, 800, 1200, -200, -80, -2, -3],
    ["Depuradora", 95000, 1200, 0, 1500, -150, 2, 4],
    ["Central Térmica", 110000, 2000, 0, -80, 1400, -3, -4],
    ["Silo Gigante", 70000, 500, 0, 0, -15, 3, 1],  # Ahora produce 3 dinero y +1 felicidad

    # --- NIVEL 3 (Requiere Investigación: "Era Atómica / Futuro") ---
    ["Rascacielos", 120000, 1500, -200, -500, -400, 5, 2],
    ["Sintetizador Comida", 150000, 4000, 5000, -800, -1200, 0, -1],
    ["Extractor Atmosférico", 250000, 5000, 0, 6000, -1500, 3, 5],
    ["Central Nuclear", 400000, 10000, 0, -500, 12000, -5, -5],

    # --- NIVEL 4 (Requiere Investigación: "Tecnología del Mañana") ---
    ["Megaplex Urbano", 220000, 3000, -300, -800, -600, 8, 3],
    ["Biofábrica", 300000, 7000, 12000, -2000, -3000, -2, -2],
    ["Planta de Ósmosis", 360000, 8000, 0, 15000, -2500, 4, 8],
    ["Reactor de Fusión", 600000, 15000, 0, -1000, 25000, -8, -8],

    # --- NIVEL 5 (Requiere AVANCES nivel 6 — Metrópolis) ---
    # --- NIVEL 5 (Requiere AVANCES nivel 5) ---
    ["Megagranja Vertical", 800000, 20000, 30000, -5000, -8000, -3, -3],
    ["Torre Inteligente", 600000, 12000, -600, -2000, -1500, 15, 5],
    ["Red de Antimateria", 1200000, 30000, 0, -3000, 60000, -12, -12],
    ["Precipitador Atmosférico", 900000, 22000, 0, 40000, -5000, 5, 10],

    # --- INTERMEDIOS (desbloqueados en AVANCES nivel 2) ---
    ["Parque Eólico", 250000, 4500, 0, -50, 5000, 2, 2],
    ["Planta Desalinizadora", 180000, 3500, 0, 3500, -200, 2, 3],

    # --- EDIFICIOS ESPECIALES / RESERVA ---
    ["Laboratorio Modular", 90000, 1200, -20, -120, -180, 2, 4],
    ["Centro de Innovación", 180000, 2600, -40, -240, -420, 4, 6],
    ["Campus Tecnológico", 340000, 4800, -80, -480, -900, 8, 9],
]


# --- POBLACION (LISTAS COMPLETAS) ---
NOMBRES_BASE = ["Antonio", "Manuel", "Jose", "Francisco", "David", "Juan", "Jose Antonio", "Javier", "Jose Luis", "Daniel", "Francisco Javier", "Jesus", "Carlos", "Alejandro", "Miguel", "Jose Manuel", "Rafael", "Miguel Angel", "Pedro", "Angel", "Pablo", "Sergio", "Fernando", "Luis", "Jorge", "Alberto", "Alvaro", "Juan Carlos", "Adrian", "Diego", "Juan Jose", "Raul", "Ivan", "Juan Antonio", "Ruben", "Enrique", "Oscar", "Ramon", "Vicente", "Andres", "Maria Carmen", "Maria", "Carmen", "Ana Maria", "Josefa", "Maria Pilar", "Isabel", "Laura", "Maria Dolores", "Maria Teresa", "Ana", "Cristina", "Marta", "Maria Angeles", "Lucia", "Maria Isabel", "Maria Jose", "Francisca", "Antonia", "Dolores", "Sara", "Paula", "Elena", "Maria Luisa", "Raquel", "Rosa Maria", "Pilar", "Manuela", "Concepcion", "Maria Jesus", "Mercedes", "Julia", "Beatriz", "Nuria", "Silvia", "Rosario", "Juana", "Teresa", "Irene", "Encarnacion", "Hugo", "Mateo", "Leo", "Lucas", "Martin", "Santiago", "Izan", "Iker", "Gonzalo", "Marcos", "Valeria", "Alba", "Claudia", "Noelia", "Ines", "Rocio", "Ainhoa", "Gemma", "Lola", "Blanca"]
APELLIDOS_BASE = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Muñoz", "Alvarez", "Romero", "Alonso", "Gutierrez", "Navarro", "Torres", "Dominguez", "Vazquez", "Ramos", "Gil", "Ramirez", "Serrano", "Blanco", "Molina", "Morales", "Suarez", "Ortega", "Delgado", "Castro", "Ortiz", "Rubio", "Marin", "Sanz", "Nuñez", "Iglesias", "Medina", "Cortes", "Castillo", "Santos", "Lozano", "Guerrero", "Cano", "Prieto", "Mendez", "Cruz", "Calvo", "Gallego", "Vidal", "Leon", "Herrera", "Marquez", "Peña", "Flores", "Cabrera", "Campos", "Vega", "Diez", "Fuentes", "Carrasco", "Caballero", "Nieto", "Reyes", "Aguilar", "Pascual", "Herrero", "Santana", "Lorenzo", "Hidalgo", "Montero", "Ibañez", "Gimenez", "Ferrer", "Duran", "Vicente", "Benitez", "Mora", "Santiago", "Arias", "Vargas", "Carmona", "Crespo", "Roman", "Pastor", "Soto", "Saez", "Velasco", "Soler", "Moya", "Esteban", "Parra", "Bravo", "Gallardo", "Rojas", "Pardo"]
PROFESIONES_BASE = ["Abogado", "Medico", "Ingeniero", "Profesor", "Dependiente", "Camarero", "Enfermero", "Arquitecto", "Administrativo", "Contable", "Programador", "Diseñador", "Cocinero", "Fontanero", "Electricista", "Mecanico", "Psicologo", "Periodista", "Policia", "Bombero", "Carpintero", "Albañil", "Conductor", "Panadero", "Peluquero", "Veterinario", "Farmaceutico", "Economista", "Comercial", "Recepcionista", "Limpiador", "Guardia Civil", "Militar", "Agricultor", "Pescador", "Escritor", "Artista", "Musico", "Actor", "Fotógrafo", "Fisioterapeuta", "Odontólogo", "Científico", "Investigador", "Traductor", "Guía Turístico", "Azafata", "Piloto", "Marinero", "Jardinero", "Pintor", "Carnicero", "Pescadero", "Frutero", "Joyero", "Relojero", "Sastre", "Modista", "Zapatero", "Cartero", "Bibliotecario", "Arqueólogo", "Geólogo", "Biólogo", "Químico", "Matemático", "Físico", "Astrónomo", "Filósofo", "Sociólogo", "Antropólogo", "Historiador", "Político", "Juez", "Fiscal", "Notario", "Diplomático", "Empresario", "Consultor", "Analista", "Marketingero", "Publicista", "Relaciones Publicas", "Editor", "Corrector", "Ilustrador", "Animador", "Escultor", "Alfarero", "Herrero", "Cerrajero", "Soldador", "Montador", "Operario", "Almacenero", "Logista", "Vigilante", "Socorrista", "Entrenador", "Deportista"]

# --- CONSTANTES DE JUEGO ---
IMPUESTO_INICIAL = 20
INGRESO_BASE_HAB = 500
CONSUMO_COMIDA_HAB = 4
CONSUMO_AGUA_HAB = 5
CONSUMO_ELEC_HAB = 6
EDAD_MAXIMA = 120
UMBRAL_CRITICO = 30
DANO_HAMBRE = 10
DANO_SED = 10
DANO_SIN_LUZ_SALUD = 5
DANO_SIN_LUZ_FELIC = 5
DANO_SIN_TECHO_FELIC = 3



# --- NIVELES ---
NIVELES_CIUDAD = [
    {"pob_min": 0, "rango": "Aldea"},
    {"pob_min": 50, "rango": "Pueblo"},
    {"pob_min": 200, "rango": "Ciudad"},
    {"pob_min": 1000, "rango": "Metrópolis"},
    {"pob_min": 5000, "rango": "Megalópolis"},
]

# ✓ ARREGLO 3: Función para ordenar edificios por tipo de recurso
def obtener_edificios_ordenados_por_tipo():
    """
    Retorna los edificios ordenados por tipo de recurso:
    1. Residencial (Casa, Bloque Pisos, Rascacielos)
    2. Comida (productores + almacenes)
    3. Agua (productores + almacenes)
    4. Energía (productores + almacenes)
    """
    # Clasificación manual de cada edificio
    clasificacion = {
        # Residencial
        "Casa": ("residencial", 0),
        "Bloque Pisos": ("residencial", 1),
        "Rascacielos": ("residencial", 2),
        "Megaplex Urbano": ("residencial", 3),
        "Torre Inteligente": ("residencial", 4),

        # Investigación
        "Laboratorio Modular": ("investigacion", 0),
        "Centro de Innovación": ("investigacion", 1),
        "Campus Tecnológico": ("investigacion", 2),
        
        # Comida
        "Granja": ("comida", 0),
        "Granja Ind.": ("comida", 1),
        "Sintetizador Comida": ("comida", 2),
        "Biofábrica": ("comida", 3),
        "Megagranja Vertical": ("comida", 5),
        "Almacen de Comida": ("comida", 6),
        "Silo Gigante": ("comida", 2),
        
        # Agua
        "Planta Agua": ("agua", 0),
        "Depuradora": ("agua", 1),
        "Planta Desalinizadora": ("agua", 2),
        "Extractor Atmosférico": ("agua", 3),
        "Planta de Ósmosis": ("agua", 4),
        "Precipitador Atmosférico": ("agua", 5),
        "Almacen de Agua": ("agua", 6),
        "Almacen de Agua": ("agua", 6),
        
        # Energía
        "Central Elec.": ("energia", 0),
        "Central Térmica": ("energia", 1),
        "Parque Eólico": ("energia", 2),
        "Central Nuclear": ("energia", 3),
        "Reactor de Fusión": ("energia", 4),
        "Red de Antimateria": ("energia", 5),
        "Almacen de Energia": ("energia", 6),
    }
    
    # Orden de tipos
    orden_tipos = ["residencial", "investigacion", "comida", "agua", "energia"]
    
    # Agrupar edificios por tipo
    edificios_grupados = {tipo: [] for tipo in orden_tipos}
    
    for ed in EDIFICACIONES:
        nombre = ed[0]
        if nombre in clasificacion:
            tipo, prioridad = clasificacion[nombre]
            edificios_grupados[tipo].append((prioridad, ed))
    
    # Ordenar cada grupo y concatenar
    resultado = []
    for tipo in orden_tipos:
        grupo = edificios_grupados[tipo]
        grupo.sort(key=lambda x: x[0])  # Ordenar por prioridad
        resultado.extend([ed for _, ed in grupo])
    
    return resultado

def obtener_tipo_edificio(nombre_edificio):
    """Retorna el tipo (residencial, comida, agua, energia) de un edificio."""
    tipos_clasificacion = {
        # Residencial
        "Casa": "residencial",
        "Bloque Pisos": "residencial",
        "Rascacielos": "residencial",
        "Megaplex Urbano": "residencial",
        "Torre Inteligente": "residencial",

        # Investigación
        "Laboratorio Modular": "investigacion",
        "Centro de Innovación": "investigacion",
        "Campus Tecnológico": "investigacion",
        
        # Comida
        "Granja": "comida",
        "Granja Ind.": "comida",
        "Sintetizador Comida": "comida",
        "Biofábrica": "comida",
        "Megagranja Vertical": "comida",
        "Almacen de Comida": "comida",
        "Silo Gigante": "comida",
        
        # Agua
        "Planta Agua": "agua",
        "Depuradora": "agua",
        "Planta Desalinizadora": "agua",
        "Extractor Atmosférico": "agua",
        "Planta de Ósmosis": "agua",
        "Precipitador Atmosférico": "agua",
        "Almacen de Agua": "agua",
        
        # Energía
        "Central Elec.": "energia",
        "Central Térmica": "energia",
        "Parque Eólico": "energia",
        "Central Nuclear": "energia",
        "Reactor de Fusión": "energia",
        "Red de Antimateria": "energia",
        "Almacen de Energia": "energia",
    }
    return tipos_clasificacion.get(nombre_edificio, None)

def fmt_num(n):
    """Formatea un número entero con puntos como separadores de miles (estilo español: 1.000.000)."""
    return f"{int(n):,}".replace(",", ".")

RANGOS_FELICIDAD = {
    "EXCELENTE": {"min": 80, "color": VERDE_BRILLANTE, "msg": "¡La gente ama tu gestión!"},
    "NORMAL": {"min": 40, "color": BLANCO, "msg": "Vida tranquila."},
    "CRITICO": {"min": 0, "color": ROJO, "msg": "¡Hay disturbios!"}
}

# --- RUTAS Y GRID ---
BASE_DIR = os.path.dirname(__file__)
RUTA_PARTIDA = os.path.join(BASE_DIR, "partida.json")

TAMANO_TILE = 2
MARGEN_HUD_SUP = 70
MARGEN_HUD_INF = 130

COLUMNAS = ANCHO // TAMANO_TILE
FILAS = (ALTO - MARGEN_HUD_INF - MARGEN_HUD_SUP) // TAMANO_TILE

# --- ICONOS PARA INTERFAZ ---
ICONO_POB = "👥"
ICONO_DINERO = "💰"
ICONO_COMIDA = "🥩"
ICONO_AGUA = "💧"
ICONO_ELEC = "⚡"
ICONO_FELICIDAD = "😊"
ICONO_SALUD = "❤️"