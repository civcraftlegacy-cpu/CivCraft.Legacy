# -*- coding: utf-8 -*-
# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.
# Módulo: Árbol de Tecnología — Sistema de Nodos por Categoría

"""
ESTRUCTURA DE NODOS (estilo Rise of Kingdoms — basado en niveles acumulables):
  - id             : str único
  - nombre         : str visible en el árbol
  - descripcion    : descripción corta del efecto por nivel
  - max_nivel      : int — cuántas veces se puede subir el nodo
  - fila_col       : int — columna visual (0=izquierda, 1=centro, 2=derecha)
  - fila_row       : int — fila dentro de la columna (solo relevante en col 1)
  - requiere_niveles: dict {nodo_id: nivel_minimo} — requisitos previos
  - costes         : list[int] — coste en oro por cada nivel (longitud == max_nivel)
  - efecto_por_nivel: dict — efecto acumulado que se aplica a LogicaCiudad por cada nivel
  - icono_color    : tuple RGB — color del icono cuadrado (fallback sin sprite)
"""

# ──────────────────────────────────────────────────────────────────────────────
# ÁRBOL: ECONOMÍA  (diseño Rise of Kingdoms — 1 nodo izq → 3 centro → 1 dcha)
# ──────────────────────────────────────────────────────────────────────────────
ARBOL_ECONOMIA = {
    # ── col 0: puerta de entrada ───────────────────────────────────────────────
    "eco_mercado": {
        "nombre": "Mercado Laboral",
        "max_nivel": 5,
        "fila_col": 0, "fila_row": 0,
        "requiere_niveles": {},
        "pob_req_por_nivel": [150, 200, 250, 350, 500],
        "costes": [10_000, 20_000, 30_000, 50_000, 100_000],
        "efectos_por_nivel": [
            {"bonus_ingreso_pct": 0.01},
            {"bonus_ingreso_pct": 0.02},
            {"bonus_ingreso_pct": 0.05},
            {"bonus_ingreso_pct": 0.10},
            {"bonus_ingreso_pct": 0.20},
        ],
        "icono_color": (255, 200, 50),
    },
    # ── col 1: nodos centrales (requieren Mercado ≥ 1) ────────────────────────
    "eco_impuestos": {
        "nombre": "Subida de Impuestos",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 0,
        "requiere_niveles": {"eco_mercado": 1},
        "pob_req_por_nivel": [300, 500, 1_000, 2_000, 5_000],
        "costes": [20_000, 50_000, 100_000, 250_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_ingreso_pct": 0.01},
            {"bonus_ingreso_pct": 0.02},
            {"bonus_ingreso_pct": 0.05},
            {"bonus_ingreso_pct": 0.10},
            {"bonus_ingreso_pct": 0.20},
        ],
        "icono_color": (255, 235, 80),
    },
    "eco_mantenimiento": {
        "nombre": "Red. Mantenimiento",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 1,
        "requiere_niveles": {"eco_mercado": 1},
        "pob_req_por_nivel": [300, 500, 1_000, 2_000, 5_000],
        "costes": [20_000, 50_000, 100_000, 250_000, 1_000_000],
        "efectos_por_nivel": [
            {"descuento_mantenimiento": 0.01},
            {"descuento_mantenimiento": 0.02},
            {"descuento_mantenimiento": 0.05},
            {"descuento_mantenimiento": 0.10},
            {"descuento_mantenimiento": 0.20},
        ],
        "icono_color": (80, 200, 140),
    },
    "eco_comisiones": {
        "nombre": "Red. Comisiones",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 2,
        "requiere_niveles": {"eco_mercado": 1},
        "pob_req_por_nivel": [300, 500, 1_000, 2_000, 5_000],
        "costes": [20_000, 50_000, 100_000, 250_000, 1_000_000],
        "efectos_por_nivel": [
            {"descuento_edificios": 0.01},
            {"descuento_edificios": 0.02},
            {"descuento_edificios": 0.05},
            {"descuento_edificios": 0.10},
            {"descuento_edificios": 0.20},
        ],
        "icono_color": (170, 110, 255),
    },
    # ── col 2: nodo final (requiere los 3 centrales al máximo) ────────────────
    "eco_reserva": {
        "nombre": "Reserva Federal",
        "max_nivel": 5,
        "fila_col": 2, "fila_row": 0,
        "requiere_niveles": {
            "eco_impuestos":     5,
            "eco_mantenimiento": 5,
            "eco_comisiones":    5,
        },
        "pob_req_por_nivel": [1_000, 2_000, 5_000, 10_000, 20_000],
        "costes": [50_000, 250_000, 1_000_000, 5_000_000, 10_000_000],
        "efectos_por_nivel": [
            {"bonus_ingreso_pct": 0.01, "descuento_mantenimiento": 0.01, "descuento_edificios": 0.01},
            {"bonus_ingreso_pct": 0.02, "descuento_mantenimiento": 0.02, "descuento_edificios": 0.02},
            {"bonus_ingreso_pct": 0.05, "descuento_mantenimiento": 0.05, "descuento_edificios": 0.05},
            {"bonus_ingreso_pct": 0.10, "descuento_mantenimiento": 0.10, "descuento_edificios": 0.10},
            {"bonus_ingreso_pct": 0.20, "descuento_mantenimiento": 0.20, "descuento_edificios": 0.20},
        ],
        "icono_color": (255, 255, 80),
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# ÁRBOL: RECURSOS
# ──────────────────────────────────────────────────────────────────────────────
ARBOL_RECURSOS = {
    "rec_nucleo": {
        "nombre": "Núcleo de Almacenaje",
        "max_nivel": 5,
        "fila_col": 0, "fila_row": 0,
        "requiere_niveles": {},
        "pob_req_por_nivel": [150, 200, 250, 350, 500],
        "costes": [10_000, 20_000, 30_000, 50_000, 100_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_comida": 1000, "bonus_capacidad_agua": 1000, "bonus_capacidad_energia": 1000},
            {"bonus_capacidad_comida": 2000, "bonus_capacidad_agua": 2000, "bonus_capacidad_energia": 2000},
            {"bonus_capacidad_comida": 5000, "bonus_capacidad_agua": 5000, "bonus_capacidad_energia": 5000},
            {"bonus_capacidad_comida": 10000, "bonus_capacidad_agua": 10000, "bonus_capacidad_energia": 10000},
            {"bonus_capacidad_comida": 20000, "bonus_capacidad_agua": 20000, "bonus_capacidad_energia": 20000},
        ],
        "icono_color": (140, 220, 180),
    },
    "rec_comida": {
        "nombre": "Cadena Alimentaria",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 0,
        "requiere_niveles": {"rec_nucleo": 1},
        "pob_req_por_nivel": [300, 500, 1000, 2000, 5000],
        "costes": [20_000, 50_000, 100_000, 250_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_comida": 5000},
            {"bonus_capacidad_comida": 10000},
            {"bonus_capacidad_comida": 20000},
            {"bonus_capacidad_comida": 50000},
            {"bonus_capacidad_comida": 100000},
        ],
        "icono_color": (120, 220, 100),
    },
    "rec_agua": {
        "nombre": "Red Hidráulica",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 1,
        "requiere_niveles": {"rec_nucleo": 1},
        "pob_req_por_nivel": [300, 500, 1000, 2000, 5000],
        "costes": [20_000, 50_000, 100_000, 250_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_agua": 5000},
            {"bonus_capacidad_agua": 10000},
            {"bonus_capacidad_agua": 20000},
            {"bonus_capacidad_agua": 50000},
            {"bonus_capacidad_agua": 100000},
        ],
        "icono_color": (100, 180, 255),
    },
    "rec_energia": {
        "nombre": "Matriz Energética",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 2,
        "requiere_niveles": {"rec_nucleo": 1},
        "pob_req_por_nivel": [300, 500, 1000, 2000, 5000],
        "costes": [20_000, 50_000, 100_000, 250_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_energia": 5000},
            {"bonus_capacidad_energia": 10000},
            {"bonus_capacidad_energia": 20000},
            {"bonus_capacidad_energia": 50000},
            {"bonus_capacidad_energia": 100000},
        ],
        "icono_color": (255, 220, 90),
    },
    "rec_optimizacion": {
        "nombre": "Optimización Trinaria",
        "max_nivel": 5,
        "fila_col": 2, "fila_row": 0,
        "requiere_niveles": {
            "rec_comida": 3,
            "rec_agua": 3,
            "rec_energia": 3,
        },
        "pob_req_por_nivel": [1000, 5000, 10000, 50000, 100000],
        "costes": [50_000, 250_000, 500_000, 1_000_000, 5_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_comida": 10000, "bonus_capacidad_agua": 10000, "bonus_capacidad_energia": 10000},
            {"bonus_capacidad_comida": 20000, "bonus_capacidad_agua": 20000, "bonus_capacidad_energia": 20000},
            {"bonus_capacidad_comida": 50000, "bonus_capacidad_agua": 50000, "bonus_capacidad_energia": 50000},
            {"bonus_capacidad_comida": 100000, "bonus_capacidad_agua": 100000, "bonus_capacidad_energia": 100000},
            {"bonus_capacidad_comida": 1000000, "bonus_capacidad_agua": 1000000, "bonus_capacidad_energia": 1000000},
        ],
        "icono_color": (255, 255, 120),
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# ÁRBOL: TROPAS
# ──────────────────────────────────────────────────────────────────────────────
ARBOL_TROPAS = {
    "tro_guardia1": {
        "nombre": "Guardia Civil",
        "descripcion": "Desbloquea unidad Guardia (ataque 10)",
        "nivel": 1, "fila": 0,
        "coste_oro": 3000, "coste_madera": 200,
        "requiere": [],
        "efecto": {"desbloquea_unidad": "guardia"},
        "icono_color": (100, 150, 255),
    },
    "tro_milicia1": {
        "nombre": "Milicia Urbana",
        "descripcion": "Desbloquea unidad Milicia (ataque 20)",
        "nivel": 1, "fila": 2,
        "coste_oro": 5000, "coste_madera": 400,
        "requiere": [],
        "efecto": {"desbloquea_unidad": "milicia"},
        "icono_color": (150, 100, 255),
    },
    "tro_moral2": {
        "nombre": "Moral de Combate",
        "descripcion": "+25% daño todas las unidades",
        "nivel": 2, "fila": 0,
        "coste_oro": 12000, "coste_madera": 600,
        "requiere": ["tro_guardia1"],
        "efecto": {"bonus_ataque_global": 0.25},
        "icono_color": (200, 100, 255),
    },
    "tro_ejercito2": {
        "nombre": "Ejército Regular",
        "descripcion": "Desbloquea unidad Soldado (ataque 50)",
        "nivel": 2, "fila": 2,
        "coste_oro": 20000, "coste_madera": 1000,
        "requiere": ["tro_milicia1"],
        "efecto": {"desbloquea_unidad": "soldado"},
        "icono_color": (255, 80, 80),
    },
    "tro_defensa2": {
        "nombre": "Murallas",
        "descripcion": "+50% defensa ciudad",
        "nivel": 2, "fila": 4,
        "coste_oro": 15000, "coste_madera": 2000,
        "requiere": ["tro_guardia1"],
        "efecto": {"bonus_defensa_global": 0.50},
        "icono_color": (180, 180, 100),
    },
    "tro_elite3": {
        "nombre": "Fuerzas de Élite",
        "descripcion": "Desbloquea Élite (ataque 120) + +50% ataque",
        "nivel": 3, "fila": 2,
        "coste_oro": 80000, "coste_madera": 3000,
        "requiere": ["tro_moral2", "tro_ejercito2", "tro_defensa2"],
        "efecto": {
            "desbloquea_unidad": "elite",
            "bonus_ataque_global": 0.50,
        },
        "icono_color": (255, 50, 50),
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# ÁRBOL: AVANCES
# ──────────────────────────────────────────────────────────────────────────────
ARBOL_AVANCES = {
    "ava_comida": {
        "nombre": "Comida Sintética",
        "descripcion": "Capacidad de comida y edificios alimentarios avanzados",
        "max_nivel": 5,
        "fila_col": 0, "fila_row": 0,
        "requiere_niveles": {},
        "requiere_todos_nivel_prev": True,
        "pob_req_por_nivel": [150, 500, 1000, 5000, 10000],
        "costes": [10_000, 50_000, 100_000, 500_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_comida": 2500, "desbloquea_edificio": "Granja Ind."},
            {"bonus_capacidad_comida": 3500, "desbloquea_edificio": "Silo Gigante"},
            {"bonus_capacidad_comida": 5000, "desbloquea_edificio": "Sintetizador Comida"},
            {"bonus_capacidad_comida": 7000, "desbloquea_edificio": "Biofábrica"},
            {"bonus_capacidad_comida": 9000, "desbloquea_edificio": "Megagranja Vertical"},
        ],
        "icono_color": (120, 220, 100),
    },
    "ava_edificios": {
        "nombre": "Edificios Modulares",
        "descripcion": "Residencias superiores y descuentos de construcción",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 0,
        "requiere_niveles": {},
        "requiere_todos_nivel_prev": True,
        "pob_req_por_nivel": [150, 500, 1000, 5000, 10000],
        "costes": [10_000, 50_000, 100_000, 500_000, 1_000_000],
        "efectos_por_nivel": [
            {"descuento_edificios": 0.03, "desbloquea_edificio": "Bloque Pisos"},
            {"descuento_edificios": 0.04, "desbloquea_edificio": "Laboratorio Modular"},
            {"descuento_edificios": 0.05, "desbloquea_edificio": "Rascacielos"},
            {"descuento_edificios": 0.06, "descuento_mantenimiento": 0.03, "desbloquea_edificio": "Megaplex Urbano"},
            {"descuento_edificios": 0.07, "descuento_mantenimiento": 0.05, "desbloquea_edificio": "Torre Inteligente"},
        ],
        "icono_color": (220, 200, 120),
    },
    "ava_energia": {
        "nombre": "Energía Cuántica",
        "descripcion": "Capacidad eléctrica y centrales de nueva generación",
        "max_nivel": 5,
        "fila_col": 1, "fila_row": 2,
        "requiere_niveles": {},
        "requiere_todos_nivel_prev": True,
        "pob_req_por_nivel": [150, 500, 1000, 5000, 10000],
        "costes": [10_000, 50_000, 100_000, 500_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_energia": 2500, "desbloquea_edificio": "Central Térmica"},
            {"bonus_capacidad_energia": 3500, "desbloquea_edificio": "Parque Eólico"},
            {"bonus_capacidad_energia": 5000, "desbloquea_edificio": "Central Nuclear"},
            {"bonus_capacidad_energia": 7000, "desbloquea_edificio": "Reactor de Fusión"},
            {"bonus_capacidad_energia": 9000, "desbloquea_edificio": "Red de Antimateria"},
        ],
        "icono_color": (255, 220, 90),
    },
    "ava_agua": {
        "nombre": "Agua Purificada",
        "descripcion": "Capacidad hídrica y depuración avanzada",
        "max_nivel": 5,
        "fila_col": 2, "fila_row": 0,
        "requiere_niveles": {},
        "requiere_todos_nivel_prev": True,
        "pob_req_por_nivel": [150, 500, 1000, 5000, 10000],
        "costes": [10_000, 50_000, 100_000, 500_000, 1_000_000],
        "efectos_por_nivel": [
            {"bonus_capacidad_agua": 2500, "desbloquea_edificio": "Depuradora"},
            {"bonus_capacidad_agua": 3500, "desbloquea_edificio": "Planta Desalinizadora"},
            {"bonus_capacidad_agua": 5000, "desbloquea_edificio": "Extractor Atmosférico"},
            {"bonus_capacidad_agua": 7000, "desbloquea_edificio": "Planta de Ósmosis"},
            {"bonus_capacidad_agua": 9000, "desbloquea_edificio": "Precipitador Atmosférico"},
        ],
        "icono_color": (100, 180, 255),
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# MAPA DE CATEGORÍAS
# ──────────────────────────────────────────────────────────────────────────────
CATEGORIAS = {
    "ECONOMÍA":  {"arbol": ARBOL_ECONOMIA,  "color": (255, 200, 50),  "archivo_tarjeta": "targeta_economia.png"},
    "RECURSOS":  {"arbol": ARBOL_RECURSOS,  "color": (100, 220, 100), "archivo_tarjeta": "targeta_recursos.png"},
    "TROPAS":    {"arbol": ARBOL_TROPAS,    "color": (255, 100, 100), "archivo_tarjeta": "targeta_tropas.png"},
    "AVANCES":   {"arbol": ARBOL_AVANCES,   "color": (100, 180, 255), "archivo_tarjeta": "targeta_avances.png"},
}

# ──────────────────────────────────────────────────────────────────────────────
# UNIDADES (para el sistema de combate)
# ──────────────────────────────────────────────────────────────────────────────
UNIDADES_BASE = {
    "guardia": {
        "nombre": "Guardia Civil",
        "ataque": 10, "defensa": 5,
        "vida": 50, "coste_oro": 500,
        "coste_comida_turno": 2,
        "icono_color": (100, 150, 255),
    },
    "milicia": {
        "nombre": "Milicia Urbana",
        "ataque": 20, "defensa": 10,
        "vida": 80, "coste_oro": 1000,
        "coste_comida_turno": 4,
        "icono_color": (150, 100, 255),
    },
    "soldado": {
        "nombre": "Soldado Regular",
        "ataque": 50, "defensa": 25,
        "vida": 120, "coste_oro": 3000,
        "coste_comida_turno": 6,
        "icono_color": (255, 80, 80),
    },
    "elite": {
        "nombre": "Fuerza de Élite",
        "ataque": 120, "defensa": 60,
        "vida": 200, "coste_oro": 10000,
        "coste_comida_turno": 10,
        "icono_color": (255, 50, 50),
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# GESTOR DEL ÁRBOL (lógica pura, sin pygame)
# ──────────────────────────────────────────────────────────────────────────────
class GestorArboles:
    """
    Mantiene el estado de qué nodos están comprados en cada árbol.
    Se instancia UNA VEZ en LogicaCiudad y se serializa en guardar_partida.

    Bonificaciones acumuladas en self.bonos:
      "multiplicador_impuestos"       float  → +% sobre impuestos anuales
      "anos_deuda_extra"              int    → años más de tolerancia a deuda
      "ingreso_extra_edificio"        int    → oro extra por edificio/año
      "bonus_capacidad_comida"        int    → unidades extra de almacén comida
      "bonus_capacidad_agua"          int    → unidades extra de almacén agua
      "bonus_capacidad_energia"       int    → unidades extra de almacén energía
      "multiplicador_capacidad"       float  → multiplicador global capacidad (≥1)
      "reduccion_consumo_hab"         float  → fracción de reducción consumo (0‒1)
      "descuento_edificios"           float  → fracción de descuento en compras (0‒1)
      "descuento_mantenimiento"       float  → fracción de descuento en mant. (0‒1)
      "reduccion_tiempo_investigacion" float → fracción de reducción tiempo inv. (0‒1)
      "bonus_felicidad_global"        int    → puntos de felicidad extra
      "bonus_ataque_global"           float  → % extra de ataque
      "bonus_defensa_global"          float  → % extra de defensa
    """

    def __init__(self):
        self.comprados: set = set()
        self.bonos: dict = self._bonos_vacio()
        self.unidades_desbloqueadas: set = set()

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _bonos_vacio() -> dict:
        return {
            "multiplicador_impuestos": 0.0,
            "anos_deuda_extra": 0,
            "ingreso_extra_edificio": 0,
            "bonus_capacidad_comida": 0,
            "bonus_capacidad_agua": 0,
            "bonus_capacidad_energia": 0,
            "multiplicador_capacidad": 1.0,
            "reduccion_consumo_hab": 0.0,
            "descuento_edificios": 0.0,
            "descuento_mantenimiento": 0.0,
            "reduccion_tiempo_investigacion": 0.0,
            "bonus_felicidad_global": 0,
            "bonus_ataque_global": 0.0,
            "bonus_defensa_global": 0.0,
        }

    def _arbol_para(self, id_nodo: str) -> dict:
        """Devuelve el árbol que contiene el nodo dado."""
        for cat in CATEGORIAS.values():
            if id_nodo in cat["arbol"]:
                return cat["arbol"]
        return {}

    # ── API pública ───────────────────────────────────────────────────────────
    def puede_comprar(self, id_nodo: str, dinero_actual: int) -> tuple:
        """Devuelve (True, '') o (False, 'motivo')."""
        arbol = self._arbol_para(id_nodo)
        if not arbol:
            return False, "Nodo inexistente"
        if id_nodo in self.comprados:
            return False, "Ya comprado"
        datos = arbol[id_nodo]
        for req in datos["requiere"]:
            if req not in self.comprados:
                nombre_req = arbol.get(req, {}).get("nombre", req)
                return False, f"Requiere: {nombre_req}"
        if dinero_actual < datos["coste_oro"]:
            falta = datos["coste_oro"] - dinero_actual
            return False, f"Faltan ${falta:,} de oro"
        return True, ""

    def comprar(self, id_nodo: str, logica) -> tuple:
        """Compra el nodo, descuenta el oro y aplica efectos. Retorna (éxito, msg)."""
        ok, motivo = self.puede_comprar(id_nodo, logica.dinero)
        if not ok:
            return False, motivo

        arbol = self._arbol_para(id_nodo)
        datos = arbol[id_nodo]
        logica.dinero -= datos["coste_oro"]
        self.comprados.add(id_nodo)
        self._aplicar_efecto(datos["efecto"], logica)
        nombre = datos["nombre"]
        logica.noticias.append({"txt": f"¡Árbol: '{nombre}' desbloqueado!", "tipo": "LOGRO"})
        return True, f"'{nombre}' desbloqueado"

    def _aplicar_efecto(self, efecto: dict, logica):
        """Aplica el efecto a los bonos y propaga a la LogicaCiudad."""
        for clave, valor in efecto.items():
            if clave == "desbloquea_unidad":
                self.unidades_desbloqueadas.add(valor)
            elif clave == "multiplicador_capacidad":
                # Tomar el máximo, no acumular
                self.bonos[clave] = max(self.bonos[clave], valor)
            elif clave in self.bonos:
                self.bonos[clave] += valor

        # Propagación inmediata a los límites de almacén
        if hasattr(logica, "aplicar_bonos_arboles"):
            logica.aplicar_bonos_arboles(self.bonos)

    # ── Serialización ─────────────────────────────────────────────────────────
    def serializar(self) -> dict:
        return {
            "comprados": list(self.comprados),
            "unidades_desbloqueadas": list(self.unidades_desbloqueadas),
        }

    def deserializar(self, datos: dict):
        self.comprados = set(datos.get("comprados", []))
        self.unidades_desbloqueadas = set(datos.get("unidades_desbloqueadas", []))
        self._recalcular_bonos()

    def _recalcular_bonos(self):
        """Recalcula bonos desde cero sumando todos los nodos comprados."""
        self.bonos = self._bonos_vacio()
        for id_nodo in self.comprados:
            arbol = self._arbol_para(id_nodo)
            if id_nodo in arbol:
                efecto = arbol[id_nodo]["efecto"]
                for clave, valor in efecto.items():
                    if clave == "desbloquea_unidad":
                        self.unidades_desbloqueadas.add(valor)
                    elif clave == "multiplicador_capacidad":
                        self.bonos[clave] = max(self.bonos[clave], valor)
                    elif clave in self.bonos:
                        self.bonos[clave] += valor
