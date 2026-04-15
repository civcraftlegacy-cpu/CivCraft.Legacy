# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import pygame
import random
import os
from configuracion import *
from entidades import Ciudadano, Edificio
import json

class LogicaCiudad:
    def _crear_poblacion_stats_vacia(self):
        return {
            "poblacion_total": 0,
            "rangos_etarios": {"Niños": 0, "Adultos": 0, "Ancianos": 0},
            "empleo": {"empleados": 0, "desempleados": 0},
            "vivienda": {"con_casa": 0, "sin_casa": 0},
            "promedios": {"salud_media": 80.0, "felicidad_media": 80.0},
        }

    def get_poblacion_total(self):
        return int(self.poblacion_stats.get("poblacion_total", 0))

    def get_felicidad_media(self):
        return float(self.poblacion_stats.get("promedios", {}).get("felicidad_media", 0.0))

    def get_salud_media(self):
        return float(self.poblacion_stats.get("promedios", {}).get("salud_media", 0.0))

    def normalizar_poblacion_stats(self):
        self.poblacion_stats.setdefault("rangos_etarios", {})
        self.poblacion_stats.setdefault("empleo", {})
        self.poblacion_stats.setdefault("vivienda", {})
        self.poblacion_stats.setdefault("promedios", {})

        rangos = self.poblacion_stats["rangos_etarios"]
        rangos.setdefault("Niños", 0)
        rangos.setdefault("Adultos", 0)
        rangos.setdefault("Ancianos", 0)

        rangos["Niños"] = max(0, int(rangos["Niños"]))
        rangos["Adultos"] = max(0, int(rangos["Adultos"]))
        rangos["Ancianos"] = max(0, int(rangos["Ancianos"]))

        total = rangos["Niños"] + rangos["Adultos"] + rangos["Ancianos"]
        self.poblacion_stats["poblacion_total"] = max(0, int(total))

        proms = self.poblacion_stats["promedios"]
        proms["salud_media"] = max(0.0, min(100.0, float(proms.get("salud_media", 80.0))))
        proms["felicidad_media"] = max(0.0, min(100.0, float(proms.get("felicidad_media", 80.0))))

        self._recalcular_estado_social()

    def _recalcular_estado_social(self):
        rangos = self.poblacion_stats.get("rangos_etarios", {})
        total = max(0, int(rangos.get("Niños", 0))) + max(0, int(rangos.get("Adultos", 0))) + max(0, int(rangos.get("Ancianos", 0)))
        self.poblacion_stats["poblacion_total"] = total
        adultos = max(0, int(rangos.get("Adultos", 0)))

        con_casa = min(total, max(0, int(self.capacidad_max_poblacion)))
        sin_casa = max(0, total - con_casa)

        puestos_trabajo = sum(
            15 for e in self.edificios
            if not getattr(e, "es_residencial", False) and e.nombre != "Parque"
        )
        empleados = min(adultos, puestos_trabajo)
        desempleados = max(0, total - empleados)

        self.poblacion_stats["vivienda"] = {"con_casa": int(con_casa), "sin_casa": int(sin_casa)}
        self.poblacion_stats["empleo"] = {"empleados": int(empleados), "desempleados": int(desempleados)}

    def generar_misiones_capitulo(self):
        self.misiones_capitulo = [
            {"id": f"cap{self.capitulo_actual}_{i}"} for i in range(10)
        ]

    def verificar_mision(self, idx):
        """Devuelve True si los requisitos de la misión idx están cumplidos."""
        pob = self.get_poblacion_total()
        avg_felic = self.get_felicidad_media()
        avg_salud = self.get_salud_media()
        edificios_reales = [e for e in self.edificios if e.x >= 0 and e.y >= 0]
        avances = self.niveles_arbol.get("AVANCES", {})
        nodos_av = ["ava_comida", "ava_edificios", "ava_energia", "ava_agua"]

        if self.capitulo_actual == 1:
            # ── CAPÍTULO 1 ──────────────────────────────────────────────────
            if idx == 0: return self.dinero >= 100000
            if idx == 1: return len(edificios_reales) >= 1
            if idx == 2: return self.intercambios_realizados >= 1
            if idx == 3: return any(v >= 10000 for v in self.recursos.values())
            if idx == 4: return any(avances.get(n, 0) >= 1 for n in nodos_av)
            if idx == 5: return avg_felic >= 90
            if idx == 6: return avg_salud >= 95
            if idx == 7: return pob >= 200
            if idx == 8: return all(v >= 10000 for v in self.recursos.values())
            if idx == 9:
                return (pob >= 250 and avg_felic >= 80 and avg_salud >= 80
                        and any(v >= 30000 for v in self.recursos.values()))

        elif self.capitulo_actual == 2:
            # ── CAPÍTULO 2 ──────────────────────────────────────────────────
            if idx == 0: return avg_felic >= 90 and avg_salud >= 90
            if idx == 1: return all(v >= 15000 for v in self.recursos.values())
            if idx == 2:
                nombres = [e.nombre for e in edificios_reales]
                return ("Almacen de Comida" in nombres and
                        "Almacen de Agua" in nombres and
                        "Almacen de Energia" in nombres)
            if idx == 3: return pob >= 350
            if idx == 4: return len(edificios_reales) >= 10
            if idx == 5: return pob >= 400
            if idx == 6: return all(v >= 20000 for v in self.recursos.values())
            if idx == 7:
                return any(avances.get(n, 0) >= 3 for n in nodos_av)
            if idx == 8:
                nivel3_edif = {"Sintetizador Comida", "Extractor Atmosférico", "Central Nuclear", "Rascacielos"}
                return any(e.nombre in nivel3_edif for e in edificios_reales)
            if idx == 9:
                return (self.dinero >= 200000 and
                        any(v >= 50000 for v in self.recursos.values()))

        elif self.capitulo_actual == 3:
            # ── CAPÍTULO 3 ──────────────────────────────────────────────────
            if idx == 0: return avg_felic >= 95 and avg_salud >= 95
            if idx == 1: return all(v >= 30000 for v in self.recursos.values())
            if idx == 2:
                nivel5_edif = {"Megaplex Urbano", "Biofábrica", "Planta de Ósmosis", "Reactor de Fusión"}
                return any(e.nombre in nivel5_edif for e in edificios_reales)
            if idx == 3: return pob >= 500
            if idx == 4: return len(edificios_reales) >= 20
            if idx == 5: return pob >= 600
            if idx == 6: return all(v >= 50000 for v in self.recursos.values())
            if idx == 7:
                return all(avances.get(n, 0) >= 3 for n in nodos_av)
            if idx == 8:
                return any(avances.get(n, 0) >= 5 for n in nodos_av)
            if idx == 9:
                return (self.dinero >= 500000 and
                        any(v >= 100000 for v in self.recursos.values()))

        elif self.capitulo_actual == 4:
            # ── CAPÍTULO 4 ──────────────────────────────────────────────────
            if idx == 0: return avg_felic >= 97 and avg_salud >= 97
            if idx == 1: return all(v >= 70000 for v in self.recursos.values())
            if idx == 2:
                nivel5_todos = {"Megaplex Urbano", "Biofábrica", "Planta de Ósmosis", "Reactor de Fusión"}
                nombres_edif = {e.nombre for e in edificios_reales}
                return nivel5_todos.issubset(nombres_edif)
            if idx == 3: return pob >= 700
            if idx == 4: return len(edificios_reales) >= 25
            if idx == 5: return pob >= 900
            if idx == 6: return all(v >= 120000 for v in self.recursos.values())
            if idx == 7:
                return all(avances.get(n, 0) >= 5 for n in nodos_av)
            if idx == 8: return self.nivel_tecnologico >= 4
            if idx == 9:
                return (self.dinero >= 3000000 and
                        any(v >= 300000 for v in self.recursos.values()))

        elif self.capitulo_actual == 5:
            # ── CAPÍTULO 5 (FINAL) ───────────────────────────────────────────
            if idx == 0: return avg_felic >= 99 and avg_salud >= 99
            if idx == 1: return all(v >= 150000 for v in self.recursos.values())
            if idx == 2:
                nivel6_edif = {"Torre Inteligente", "Megagranja Vertical", "Red de Antimateria", "Precipitador Atmosférico"}
                return any(e.nombre in nivel6_edif for e in edificios_reales)
            if idx == 3: return pob >= 1000
            if idx == 4: return len(edificios_reales) >= 35
            if idx == 5: return pob >= 1200
            if idx == 6: return all(v >= 250000 for v in self.recursos.values())
            if idx == 7:
                return all(avances.get(n, 0) >= 5 for n in nodos_av)
            if idx == 8: return self.dinero >= 5000000
            if idx == 9:
                return (self.dinero >= 10000000 and
                        all(v >= 500000 for v in self.recursos.values()))

    def __init__(self, juego_referencia, nombre_partida_inicial="Nueva Partida"):
        self.juego = juego_referencia
        self.nombre_partida_actual = nombre_partida_inicial 
        
        # --- 1. DECLARACIÓN DE VARIABLES (EL "ESCUDO") ---
        # Definimos TODO lo que el código pueda preguntar después
        self.game_over = False
        self.dinero = 100000
        self.poblacion_stats = self._crear_poblacion_stats_vacia()
        self.poblacion = []
        self.edificios = []
        self.noticias = []
        self.ano = 0
        self.rango_actual = "Aldea"
        self.anos_en_deuda = 0
        self.nivel_tecnologico = 1

        self.recursos = {"comida": 0, "agua": 0, "electricidad": 0}
        self.max_comida = 10000
        self.max_agua = 10000
        self.max_energia = 10000

        self.total_mantenimiento_anual = 0
        self.investigando_id = None
        self.tiempo_investigacion = 0
        self.tiempo_total_req = 300
        self.investigaciones_completadas = set()
        self.mostrar_popup_evento = False
        self.evento_actual = None

        # ── Bonificaciones del árbol tecnológico de Economía ──────────────────
        self.investigaciones_ano  = {}  # {inv_id: año en que fue completada}
        self.arbol_subidas_ano    = {}  # {"cat::nid": [año1, año2, ...]} — un año por nivel subido

        # ── Bonificaciones del árbol tecnológico de Economía ──────────────────
        self.bonus_ingreso_pct       = 0.0   # % extra sobre impuestos (acumulado)
        self.descuento_mantenimiento = 0.0   # % reducción en coste de mantenimiento
        self.descuento_edificios     = 0.0   # % reducción en precio de compra de edificios
        self.reduccion_tiempo_investigacion = 0.0
        self.niveles_arbol           = {}    # { categoria: { nod_id: nivel } } (serializable)
        self.bonus_capacidad_comida_inv = 0  # bonus de capacidad por investigaciones
        self.bonus_capacidad_agua_inv = 0
        self.bonus_capacidad_energia_inv = 0
        self.ultimo_resumen_investigacion = []
        self.ultimo_titulo_investigacion = ""

        # Misiones
        self.capitulo_actual = 1
        self.misiones_capitulo = []
        self.misiones_completadas = set()
        self.intercambios_realizados = 0
        self.estado_inicio_capitulo = None
        self.cofres_abiertos = set()  # Porcentajes ya reclamados: {20, 50, 100}
        self.mostrar_popup_bloqueo_capitulo = False
        self.mostrar_popup_nuevo_capitulo = False
        self.capitulo_avanzado_a = 0

        # IMPORTANTE: crear esto antes de cualquier lógica que lo use
        self.poblacion_inicial = 100
        self.capacidad_max_poblacion = 100


        # --- 2. LÓGICA DE INICIALIZACIÓN ---
        
        # Primero calculamos los límites reales (esto sobreescribirá los 10000 de arriba)
        self.aplicar_limites_dinamicos() 

        # Población inicial en formato agregado
        self.poblacion_stats["poblacion_total"] = 100
        self.poblacion_stats["rangos_etarios"] = {"Niños": 0, "Adultos": 100, "Ancianos": 0}
        self.poblacion_stats["promedios"] = {"salud_media": 80.0, "felicidad_media": 80.0}

        # Añadimos viviendas iniciales invisibles que no consumen recursos,
        # para que la partida empiece con capacidad para 100 ciudadanos.
        for _ in range(20):
            casa_inicial = Edificio(self._crear_data_edificio("Casa", es_inicial_gratis=True), -1000, -1000)
            self.edificios.append(casa_inicial)

        self.asignar_vivienda_y_empleo()

        cant_personas = self.get_poblacion_total()
        self.poblacion_inicial = cant_personas
        self.capacidad_max_poblacion = cant_personas


        # Ajustamos los recursos iniciales según la gente que entró
        self.recursos["comida"] = cant_personas * CONSUMO_COMIDA_HAB * 10
        self.recursos["agua"] = cant_personas * CONSUMO_AGUA_HAB * 10
        self.recursos["electricidad"] = cant_personas * CONSUMO_ELEC_HAB * 10 

        self.aplicar_limites_dinamicos()

        # --- 5. INVESTIGACIÓN Y EVENTOS ---
        self.investigando_id = None    
        self.tiempo_investigacion = 0  
        self.tiempo_total_req = 300    
        self.investigaciones_completadas = set()
        self.investigaciones_ano = {}
        self.arbol_subidas_ano = {}
        
        self.mostrar_popup_evento = False
        self.evento_actual = None
        
        self.eventos_posibles = [
            # --- EVENTOS BUENOS ---
            {
                "titulo": "¡AUGE TURÍSTICO!",
                "mensaje": "Un crucero de lujo ha atracado. ¿Invertir en marketing?",
                "opcion_a": "Campaña VIP (Cuesta 10%)",
                "opcion_b": "Dejar que exploren (Gratis)",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.10, 
                "efecto_a": {"dinero_extra": 0.30, "felicidad": 15},
                "efecto_b": {"dinero_extra": 0.05}
            },
            {
                "titulo": "¡INVERSOR ÁNGEL!",
                "mensaje": "Un magnate quiere abrir una sede. Pide beneficios fiscales.",
                "opcion_a": "Aceptar (Felicidad -10)",
                "opcion_b": "Cobrar impuestos normales",
                "tipo": "bueno",
                "efecto_a": {"dinero_extra": 0.40, "felicidad": -10},
                "efecto_b": {"dinero_extra": 0.15}
            },
            {
                "titulo": "¡COSECHA RÉCORD!",
                "mensaje": "El clima ha sido perfecto. Los graneros están llenos.",
                "opcion_a": "Exportar (Ganas 15% Dinero)",
                "opcion_b": "Repartir (Felicidad +30)",
                "tipo": "bueno",
                "efecto_a": {"dinero_extra": 0.15, "comida": -200},
                "efecto_b": {"comida": 800, "felicidad": 30}
            },
            {
                "titulo": "¡DÍA DEL ORGULLO LOCAL!",
                "mensaje": "La gente quiere un festival en la plaza central.",
                "opcion_a": "Financiar (Cuesta 5%)",
                "opcion_b": "Denegar permiso",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.05,
                "efecto_a": {"felicidad": 40},
                "efecto_b": {"felicidad": -15}
            },
            {
                "titulo": "¡HALLAZGO PETROLÍFERO!",
                "mensaje": "Se ha encontrado un pequeño pozo en las afueras.",
                "opcion_a": "Explotar (Dinero +25%)",
                "opcion_b": "Preservar (Felicidad +10)",
                "tipo": "bueno",
                "efecto_a": {"dinero_extra": 0.25, "felicidad": -15},
                "efecto_b": {"felicidad": 10}
            },
            {
                "titulo": "¡BECA TECNOLÓGICA!",
                "mensaje": "Una universidad ofrece mejorar tu red eléctrica gratis.",
                "opcion_a": "Aceptar mejora",
                "opcion_b": "Rechazar (Desconfianza)",
                "tipo": "bueno",
                "efecto_a": {"energia": 300, "felicidad": 5},
                "efecto_b": {"felicidad": -5}
            },
            {
                "titulo": "¡MARATÓN DE SALUD!",
                "mensaje": "La OMS ofrece vacunas subvencionadas.",
                "opcion_a": "Comprar lote (Cuesta 8%)",
                "opcion_b": "Solo las básicas (Gratis)",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.08,
                "efecto_a": {"salud": 50},
                "efecto_b": {"salud": 10}
            },
            {
                "titulo": "¡SISTEMA DE RECICLAJE!",
                "mensaje": "Una nueva ley podría reducir el consumo de recursos.",
                "opcion_a": "Implementar (Cuesta 12%)",
                "opcion_b": "Ignorar",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.12,
                "efecto_a": {"agua": 200, "energia": 200, "felicidad": 10},
                "efecto_b": {}
            },
            # --- EVENTOS MALOS ---
            {
                "titulo": "¡TERREMOTO!",
                "mensaje": "Un sismo ha sacudido la ciudad. Los daños son masivos.",
                "opcion_a": "Plan de Reconstrucción (Cuesta 30%)",
                "opcion_b": "Dejar escombros (Caos total)",
                "tipo": "malo",
                "porcentaje_coste_a": 0.30,
                "efecto_a": {"felicidad": -10},
                "efecto_b": {"felicidad": -50, "salud": -20, "poblacion_extra": -0.10}
            },
            {
                "titulo": "¡PANDEMIA GLOBAL!",
                "mensaje": "Un virus se propaga. Los hospitales no dan abasto.",
                "opcion_a": "Cuarentena Total (Cuesta 20% Dinero)",
                "opcion_b": "Inmunidad de grupo (Mueren ciudadanos)",
                "tipo": "malo",
                "porcentaje_coste_a": 0.20,
                "efecto_a": {"felicidad": -30, "salud": 10},
                "efecto_b": {"salud": -40, "poblacion_extra": -0.20, "felicidad": -10}
            }
        ]

        # --- 5. TIENDA E INVESTIGACIÓN ---
        self.edificios_desbloqueados = [
            "Casa", "Granja", "Planta Agua", "Central Elec.", 
            "Almacen de Comida", "Almacen de Agua", "Almacen de Energia"
        ]

        self.datos_investigacion = {
            # ── NIVEL 2 ───────────────────────────────────────────────────
            "comida_2":       {"nivel": 2, "titulo": "Comida Nivel 2",       "coste_dinero": 2500,  "pob_req": 200, "edificios_desbloquea": ["Granja Ind.", "Silo Gigante"],    "color": (100, 255, 100), "efecto": {"bonus_capacidad_comida": 2500}},
            "agua_2":         {"nivel": 2, "titulo": "Agua Nivel 2",         "coste_dinero": 3000,  "pob_req": 250, "edificios_desbloquea": ["Depuradora"],                      "color": (100, 100, 255), "efecto": {"bonus_capacidad_agua": 2500}},
            "energia_2":      {"nivel": 2, "titulo": "Energía Nivel 2",      "coste_dinero": 4000,  "pob_req": 300, "edificios_desbloquea": ["Central Térmica"],               "color": (255, 255, 100), "efecto": {"bonus_capacidad_energia": 2500}},
            "alojamiento_2":  {"nivel": 2, "titulo": "Alojamiento Nivel 2",  "coste_dinero": 200,   "pob_req": 150, "edificios_desbloquea": ["Bloque Pisos"],                  "color": (255, 200, 100), "efecto": {"bonus_ingreso_pct": 0.02}},
            # ── NIVEL 3 ───────────────────────────────────────────────────
            "comida_3":       {"nivel": 3, "titulo": "Comida Nivel 3",       "coste_dinero": 5000,  "pob_req": 500, "edificios_desbloquea": ["Sintetizador Comida"],           "color": (150, 255, 150), "efecto": {"bonus_capacidad_comida": 5000}},
            "agua_3":         {"nivel": 3, "titulo": "Agua Nivel 3",         "coste_dinero": 6000,  "pob_req": 550, "edificios_desbloquea": ["Extractor Atmosférico"],        "color": (150, 150, 255), "efecto": {"bonus_capacidad_agua": 5000}},
            "energia_3":      {"nivel": 3, "titulo": "Energía Nivel 3",      "coste_dinero": 8000,  "pob_req": 600, "edificios_desbloquea": ["Central Nuclear"],              "color": (255, 255, 150), "efecto": {"bonus_capacidad_energia": 5000}},
            "alojamiento_3":  {"nivel": 3, "titulo": "Alojamiento Nivel 3",  "coste_dinero": 4500,  "pob_req": 400, "edificios_desbloquea": ["Rascacielos"],                  "color": (255, 180, 80), "efecto": {"bonus_ingreso_pct": 0.03}},
            # ── NIVEL 4 ───────────────────────────────────────────────────
            "comida_4":       {"nivel": 4, "titulo": "Producción Avanzada",  "coste_dinero": 15000, "pob_req": 700, "edificios_desbloquea": ["Biofábrica"],                   "color": (180, 255, 180), "efecto": {"bonus_capacidad_comida": 8000, "descuento_mantenimiento": 0.02}},
            "agua_4":         {"nivel": 4, "titulo": "Hidráulica Avanzada",  "coste_dinero": 18000, "pob_req": 750, "edificios_desbloquea": ["Planta de Ósmosis"],           "color": (180, 180, 255), "efecto": {"bonus_capacidad_agua": 8000, "descuento_mantenimiento": 0.02}},
            "energia_4":      {"nivel": 4, "titulo": "Fusión Nuclear",       "coste_dinero": 25000, "pob_req": 800, "edificios_desbloquea": ["Reactor de Fusión"],           "color": (255, 255, 200), "efecto": {"bonus_capacidad_energia": 8000, "bonus_ingreso_pct": 0.05}},
            "alojamiento_4":  {"nivel": 4, "titulo": "Urbanismo Avanzado",   "coste_dinero": 12000, "pob_req": 650, "edificios_desbloquea": ["Megaplex Urbano"],             "color": (255, 220, 120), "efecto": {"bonus_ingreso_pct": 0.08, "descuento_edificios": 0.05}},
        }

        self.generar_misiones_capitulo()
        self.estado_inicio_capitulo = self.guardar_estado_completo()  

    def _formatear_efecto_investigacion(self, efecto):
        if not efecto:
            return []
        resumen = []
        for clave, valor in efecto.items():
            if clave == "bonus_ingreso_pct":
                resumen.append(f"Ingresos por impuestos: +{int(valor * 100)}%")
            elif clave == "descuento_mantenimiento":
                resumen.append(f"Mantenimiento: -{int(valor * 100)}%")
            elif clave == "descuento_edificios":
                resumen.append(f"Coste de edificios: -{int(valor * 100)}%")
            elif clave == "bonus_capacidad_comida":
                resumen.append(f"Capacidad comida: +{int(valor):,}")
            elif clave == "bonus_capacidad_agua":
                resumen.append(f"Capacidad agua: +{int(valor):,}")
            elif clave == "bonus_capacidad_energia":
                resumen.append(f"Capacidad energía: +{int(valor):,}")
            else:
                resumen.append(f"{clave}: {valor}")
        return resumen

    @staticmethod
    def _es_edificio_inicial_guardado(datos_guardados):
        return bool(datos_guardados.get("es_inicial_gratis", False)) or (
            datos_guardados.get("nombre") == "Casa"
            and datos_guardados.get("x", 0) < 0
            and datos_guardados.get("y", 0) < 0
        )

    def _crear_data_edificio(self, nombre_edificio, es_inicial_gratis=False):
        if es_inicial_gratis:
            return {
                'nombre': nombre_edificio,
                'costo': 0,
                'mantenimiento': 0,
                'comida': 0,
                'agua': 0,
                'elec': 0,
                'dinero': 0,
                'capacidad': 5,
                'felic': 0,
                'salud': 0,
                'color': VERDE,
                'es_inicial_gratis': True,
            }

        tipo = next((e for e in EDIFICACIONES if e[0] == nombre_edificio), None)
        if not tipo:
            return None

        return {
            'nombre': tipo[0],
            'costo': tipo[1],
            'mantenimiento': tipo[2],
            'comida': tipo[3],
            'agua': tipo[4],
            'elec': tipo[5],
            'dinero': tipo[6],
            'capacidad': 20,
            'felic': tipo[7],
            'salud': 0,
            'color': VERDE,
            'es_inicial_gratis': False,
        }

    def _aplicar_efectos_investigacion(self, efecto):
        if not efecto:
            return
        self.bonus_ingreso_pct += efecto.get("bonus_ingreso_pct", 0.0)
        self.descuento_mantenimiento += efecto.get("descuento_mantenimiento", 0.0)
        self.descuento_edificios += efecto.get("descuento_edificios", 0.0)
        self.bonus_capacidad_comida_inv += int(efecto.get("bonus_capacidad_comida", 0))
        self.bonus_capacidad_agua_inv += int(efecto.get("bonus_capacidad_agua", 0))
        self.bonus_capacidad_energia_inv += int(efecto.get("bonus_capacidad_energia", 0))

        self.normalizar_modificadores_economia()

    def normalizar_modificadores_economia(self):
        """Evita valores extremos: sin precios gratis ni mantenimiento negativo."""
        self.bonus_ingreso_pct = max(0.0, min(3.0, float(self.bonus_ingreso_pct)))
        self.descuento_mantenimiento = max(0.0, min(0.90, float(self.descuento_mantenimiento)))
        self.descuento_edificios = max(0.0, min(0.90, float(self.descuento_edificios)))

    def recalcular_bonos_investigacion(self):
        self.bonus_capacidad_comida_inv = 0
        self.bonus_capacidad_agua_inv = 0
        self.bonus_capacidad_energia_inv = 0

        for inv_id in self.investigaciones_completadas:
            datos = self.datos_investigacion.get(inv_id, {})
            efecto = datos.get("efecto", {})
            self.bonus_capacidad_comida_inv += int(efecto.get("bonus_capacidad_comida", 0))
            self.bonus_capacidad_agua_inv += int(efecto.get("bonus_capacidad_agua", 0))
            self.bonus_capacidad_energia_inv += int(efecto.get("bonus_capacidad_energia", 0))

    def recalcular_bonos_investigacion_completas(self):
        self.bonus_ingreso_pct = 0.0
        self.descuento_mantenimiento = 0.0
        self.descuento_edificios = 0.0
        self.reduccion_tiempo_investigacion = 0.0
        self.bonus_capacidad_comida_inv = 0
        self.bonus_capacidad_agua_inv = 0
        self.bonus_capacidad_energia_inv = 0

        for inv_id in self.investigaciones_completadas:
            datos = self.datos_investigacion.get(inv_id, {})
            self._aplicar_efectos_investigacion(datos.get("efecto", {}))

    def limite_negativo_recurso(self, recurso):
        """Retorna el límite negativo dinámico para un recurso dado."""
        limites_max = {
            "comida": self.max_comida,
            "agua": self.max_agua,
            "electricidad": self.max_energia
        }
        maximo = limites_max.get(recurso, 0)
        return -(maximo // 2)

    def completar_investigacion(self, id_investigacion):
        """Marca una investigación como completada y desbloquea sus edificios."""
        if id_investigacion not in self.datos_investigacion:
            return False, "Investigación no válida"
        
        if id_investigacion in self.investigaciones_completadas:
            return False, "Ya está completada"
        
        # Marcar como completada
        self.investigaciones_completadas.add(id_investigacion)
        self.investigaciones_ano[id_investigacion] = self.ano  # registrar año para reinicio selectivo
        
        # Desbloquear edificios
        datos_inv = self.datos_investigacion[id_investigacion]
        for edificio in datos_inv.get("edificios_desbloquea", []):
            if edificio not in self.edificios_desbloqueados:
                self.edificios_desbloqueados.append(edificio)

        # Aplicar bonificaciones permanentes de la investigación
        efecto = datos_inv.get("efecto", {})
        self._aplicar_efectos_investigacion(efecto)
        self.aplicar_limites_dinamicos()
        self.ultimo_resumen_investigacion = self._formatear_efecto_investigacion(efecto)
        desbloqueos = datos_inv.get("edificios_desbloquea", [])
        if desbloqueos:
            self.ultimo_resumen_investigacion.append(f"Desbloquea: {', '.join(desbloqueos)}")
        self.ultimo_titulo_investigacion = datos_inv.get("titulo", "")
        
        # Noticia
        titulo = datos_inv["titulo"]
        self.noticias.append({
            "txt": f"¡Investigación completada: {titulo}!",
            "tipo": "LOGRO"
        })
        
        # Verificar si completa todas nivel 2 para subir a nivel 3
        self._verificar_subida_nivel()
        
        return True, f"Investigación completada: {titulo}"
    
    def _verificar_subida_nivel(self):
        """Verifica si todas las investigaciones del nivel actual están completas."""
        if self.nivel_tecnologico == 1:
            nivel_2_reqs = ["comida_2", "agua_2", "energia_2", "alojamiento_2"]
            if all(inv_id in self.investigaciones_completadas for inv_id in nivel_2_reqs):
                self.nivel_tecnologico = 2
                self.noticias.append({"txt": "¡Tu ciudad ha avanzado a NIVEL 2!", "tipo": "LOGRO"})
        elif self.nivel_tecnologico == 2:
            nivel_3_reqs = ["comida_3", "agua_3", "energia_3", "alojamiento_3"]
            if all(inv_id in self.investigaciones_completadas for inv_id in nivel_3_reqs):
                self.nivel_tecnologico = 3
                self.noticias.append({"txt": "¡Tu ciudad ha avanzado a NIVEL 3!", "tipo": "LOGRO"})
        elif self.nivel_tecnologico == 3:
            nivel_4_reqs = ["comida_4", "agua_4", "energia_4", "alojamiento_4"]
            if all(inv_id in self.investigaciones_completadas for inv_id in nivel_4_reqs):
                self.nivel_tecnologico = 4
                self.noticias.append({"txt": "¡Tu ciudad ha alcanzado el NIVEL 4! ¡Tecnología del Mañana!", "tipo": "LOGRO"})
    
    def obtener_investigaciones_disponibles(self):
        """Devuelve investigaciones disponibles según nivel actual."""
        disponibles = {}
        for inv_id, datos in self.datos_investigacion.items():
            if inv_id in self.investigaciones_completadas:
                continue
            nivel_inv = datos["nivel"]
            if nivel_inv == 2 and self.nivel_tecnologico >= 1:
                disponibles[inv_id] = datos
            elif nivel_inv == 3 and self.nivel_tecnologico >= 2:
                disponibles[inv_id] = datos
            elif nivel_inv == 4 and self.nivel_tecnologico >= 3:
                disponibles[inv_id] = datos
        return disponibles
    
    def agregar_ciudadano(self):
        """Añade 1 adulto por defecto en formato agregado."""
        return self.agregar_ciudadanos(1, "Adultos")

    def agregar_ciudadanos(self, cantidad, rango="Adultos"):
        cantidad = max(0, int(cantidad))
        if cantidad == 0:
            return 0
        rangos = self.poblacion_stats["rangos_etarios"]
        if rango not in rangos:
            rango = "Adultos"
        rangos[rango] += cantidad
        self.poblacion_stats["poblacion_total"] = self.get_poblacion_total() + cantidad
        self._recalcular_estado_social()
        return cantidad

    def reducir_poblacion(self, cantidad):
        cantidad = max(0, int(cantidad))
        total = self.get_poblacion_total()
        if total <= 0 or cantidad <= 0:
            return 0
        quitar = min(cantidad, total)
        rangos = self.poblacion_stats["rangos_etarios"]

        quitar_anc = min(rangos["Ancianos"], quitar)
        rangos["Ancianos"] -= quitar_anc
        restante = quitar - quitar_anc

        quitar_adu = min(rangos["Adultos"], restante)
        rangos["Adultos"] -= quitar_adu
        restante -= quitar_adu

        quitar_nin = min(rangos["Niños"], restante)
        rangos["Niños"] -= quitar_nin

        self.poblacion_stats["poblacion_total"] = total - quitar
        self._recalcular_estado_social()
        return quitar

    def agregar_ciudadano_nacimiento(self):
        """Alias para usar al inicio del juego desde __init__."""
        return self.agregar_ciudadanos(1, "Niños")

    # Nota: esta definicion inicial de avanzar_ano se elimino porque existe una segunda version activa mas abajo.

    def actualizar_recursos_globales(self):
        limites_max = {
            "comida": self.max_comida,
            "agua": self.max_agua,
            "electricidad": self.max_energia
        }

        for res in self.recursos:
            # Máximo permitido
            if self.recursos[res] > limites_max[res]:
                self.recursos[res] = limites_max[res]
            # Sin límite mínimo: notificar escasez crítica cuando el recurso es negativo
            elif self.recursos[res] < 0 and self.ano % 2 == 0:
                self.noticias.append({"txt": f"¡ESCASEZ CRÍTICA DE {res.upper()}!", "tipo": "CRITICO"})

    def es_posicion_valida(self, x, y, ancho_edf=3, alto_edf=3):
        # 1. Verificar que no se salga del mapa
        if x + ancho_edf > COLUMNAS or y + alto_edf > FILAS:
            return False
        
        # 2. Revisar cada celda del área que ocupará el edificio
        for f in range(y, y + alto_edf):
            for c in range(x, x + ancho_edf):
                # Si la celda no es 0 (Pasto), entonces hay algo (Carretera o HUD)
                if self.juego.mapa_datos[f][c] != 0:
                    return False
                    
        # 3. Verificar si ya hay otro edificio ahí (usando tu lista de edificios)
        for edf in self.edificios:
            # Simplificado: si las coordenadas x,y coinciden o se solapan
            if abs(edf.x - x) < ancho_edf and abs(edf.y - y) < alto_edf:
                return False
                
        return True

    def actualizar_consumos_totales(self):
        # Reiniciamos los totales a 0 para volver a sumar
        self.total_comida_anual = 0
        self.total_agua_anual = 0
        self.total_luz_anual = 0
        self.total_mantenimiento_anual = 0

        # Sumamos lo que gasta cada edificio que hay en la ciudad
        for edf in self.edificios:
            self.total_comida_anual += edf.comida
            self.total_agua_anual += edf.agua
            self.total_luz_anual += edf.elec
            self.total_mantenimiento_anual += edf.mantenimiento

    def asignar_vivienda_y_empleo(self):
        """Calcula empleo y vivienda con estadísticas agregadas."""
        self._recalcular_estado_social()

    def aplicar_efectos_edificios(self):
        """Aplica el impacto de edificios a felicidad y salud de la poblacion."""
        edificios_no_casa = [e for e in self.edificios if e.nombre != "Casa"]
        if not edificios_no_casa:
            return

        total_felicidad = sum(e.felic_impacto for e in edificios_no_casa)
        total_salud = sum(e.salud_impacto for e in edificios_no_casa)
        promedio_felicidad = total_felicidad / max(1, len(edificios_no_casa))
        promedio_salud = total_salud / max(1, len(edificios_no_casa))

        proms = self.poblacion_stats["promedios"]
        proms["felicidad_media"] = max(0.0, min(100.0, proms.get("felicidad_media", 80.0) + promedio_felicidad))
        proms["salud_media"] = max(0.0, min(100.0, proms.get("salud_media", 80.0) + promedio_salud))

    def actualizar_capacidad_max_poblacion(self):
        """Calcula la capacidad maxima de poblacion basada en viviendas"""
        self.capacidad_max_poblacion = sum(
            getattr(e, "capacidad_max_vivienda", 0)
            for e in self.edificios
        )

    def gestionar_inmigracion(self):
        """Inmigración basada en % de recursos:
        - comida o agua al 0%  → nadie llega
        - ambos < 25%          → llega 1/10 del espacio libre
        - al menos uno ≥ 25%   → llega 1/5 del espacio libre
        """
        pob_actual = self.get_poblacion_total()
        if pob_actual >= self.capacidad_max_poblacion:
            return

        pct_comida = self.recursos["comida"] / self.max_comida if self.max_comida > 0 else 0
        pct_agua   = self.recursos["agua"]   / self.max_agua   if self.max_agua   > 0 else 0

        # Sin recursos: nadie llega
        if pct_comida <= 0 or pct_agua <= 0:
            return

        espacio_disponible = self.capacidad_max_poblacion - pob_actual
        if espacio_disponible <= 0:
            return

        # Fracción según nivel de recursos
        if pct_comida >= 0.25 and pct_agua >= 0.25:
            fraccion = 1 / 5
        else:
            fraccion = 1 / 10

        nuevos = max(1, int(espacio_disponible * fraccion))
        nuevos = min(nuevos, espacio_disponible)

        self.agregar_ciudadanos(nuevos, "Adultos")
        self.noticias.append({"txt": f"Nuevos colonos: +{nuevos}", "tipo": "AVISO"})

    def procesar_noticias(self, lista_notas):
        prioridad = {"CRITICO": 0, "MUERTE": 1, "AVISO": 2}
        lista_notas.sort(key=lambda x: prioridad.get(x["tipo"], 3))
        for n in lista_notas:
            if n not in self.noticias:
                self.noticias.append(n)
        self.noticias = self.noticias[:10]

    def verificar_rango_ciudad(self):
        pob_actual = self.get_poblacion_total()
        for nivel in reversed(NIVELES_CIUDAD):
            if pob_actual >= nivel["pob_min"]:
                if self.rango_actual != nivel["rango"]:
                    self.rango_actual = nivel["rango"]
                    self.noticias.append({"txt": f"Ciudad nivel: {self.rango_actual}", "tipo": "AVISO"})
                    if hasattr(self.juego, 'reproducir_sonido'):
                        self.juego.reproducir_sonido("nivel")
                break

    def comprar_edificio(self, tipo_data, x, y):
        # --- 1. Definir el tamaño del solar ---
        ancho_solar, alto_solar = 3, 3 

        # --- 2. Verificar límites ---
        if x + ancho_solar > COLUMNAS or y + alto_solar > FILAS:
            return False

        # --- 3. Revisar si hay carretera (tipo != 0) ---
        for f in range(y, y + alto_solar):
            for c in range(x, x + ancho_solar):
                if self.juego.mapa_datos[f][c] != 0:
                    print("Espacio ocupado por carretera")
                    return False

        # --- 4. Revisar si choca con otros edificios ---
        for edf in self.edificios:
            if abs(edf.x - x) < ancho_solar and abs(edf.y - y) < alto_solar:
                print("Espacio ocupado por otro edificio")
                return False

        # --- 5. COMPRA ---
        # Aplicar descuento de construcción del árbol tecnológico de Economía
        precio_efectivo = self.calcular_precio_efectivo_edificio(tipo_data)
        if self.dinero >= precio_efectivo:
            data_final = {
                'nombre': tipo_data[0],
                'costo': tipo_data[1],
                'mantenimiento': tipo_data[2],
                'comida': tipo_data[3],
                'agua': tipo_data[4],
                'elec': tipo_data[5],
                'dinero': tipo_data[6],  # ✓ CORRECCIÓN: usar dinero del array
                'capacidad': 20,
                'felic': tipo_data[7],   # ✓ CORRECCIÓN: era tipo_data[6]
                'salud': 0,              # ✓ Por defecto 0
                'color': random.choice([VERDE, AZUL, CIAN])
            }
            
            # Solo UNA VEZ esto:
            nuevo = Edificio(data_final, x, y)
            self.edificios.append(nuevo)
            self.dinero -= precio_efectivo
            
            # Actualizamos los totales para que el HUD se entere del nuevo consumo
            self.actualizar_consumos_totales()
            # NUEVO FASE 4: Recalcular capacidad por nueva vivienda
            self.actualizar_capacidad_max_poblacion()
            # ✓ ARREGLO 1: Recalcular límites dinámicos después de comprar almacén
            self.aplicar_limites_dinamicos()
            
            return {"exito": True, "razón": "compra_exitosa"}
        else:
            dinero_faltante = precio_efectivo - self.dinero
            return {"exito": False, "razón": "dinero_insuficiente", "faltante": dinero_faltante, "nombre": tipo_data[0]}

    def calcular_precio_efectivo_edificio(self, tipo_data):
        return max(0, int(tipo_data[1] * (1.0 - self.descuento_edificios)))
    
    def vender_edificios(self, nombre_edificio, cantidad):
        """Vende edificios del mismo tipo y devuelve el 50% del costo"""
        # Buscar el edificio en EDIFICACIONES
        edificio_data = None
        for ed in EDIFICACIONES:
            if ed[0] == nombre_edificio:
                edificio_data = ed
                break
        
        if not edificio_data:
            return False
        
        costo_original = edificio_data[1]
        precio_venta = costo_original // 2  # 50%
        
        # Eliminar los edificios del mapa (elimina los primeros 'cantidad' que encuentre)
        eliminados = 0
        for _ in range(cantidad):
            for i, edf in enumerate(self.edificios):
                if edf.nombre == nombre_edificio:
                    self.edificios.pop(i)
                    eliminados += 1
                    break
        
        if eliminados > 0:
            # Solo dar dinero por los que realmente se eliminaron
            self.dinero += precio_venta * eliminados
            # NUEVO FASE 4: Recalcular capacidad después de venta
            self.actualizar_capacidad_max_poblacion()
            # Recalcular consumos después de eliminar edificios
            self.actualizar_consumos_totales()
            return True
        
        return False
     
    def aplicar_limites_dinamicos(self):
        """Aplica limites: (Poblacion * Consumo * 20) + (Almacenes * 5000)"""
        n_pob = self.get_poblacion_total()
        
        # 1. Contar almacenes construidos (incluyendo silos y variantes)
        almacenes_comida = sum(1 for e in self.edificios if e.nombre in ["Almacen de Comida", "Silo Gigante"])
        almacenes_agua = sum(1 for e in self.edificios if e.nombre == "Almacen de Agua")
        almacenes_elec = sum(1 for e in self.edificios if e.nombre == "Almacen de Energia")

        # 2. Calcular Máximos (Base de 20 años + Almacenes)
        # ✓ ARREGLO 1: Cambiar de 4000 a 5000 por almacén
        # Comida: (población * 4 * 20) + (N almacenes * 5000)
        self.max_comida = (n_pob * CONSUMO_COMIDA_HAB * 20) + (almacenes_comida * 5000)
        
        # Agua: (población * 5 * 20) + (N almacenes * 5000)
        self.max_agua = (n_pob * CONSUMO_AGUA_HAB * 20) + (almacenes_agua * 5000)
        
        # Energía: (población * 6 * 20) + (N almacenes * 5000)
        self.max_energia = (n_pob * CONSUMO_ELEC_HAB * 20) + (almacenes_elec * 5000)

        # Bonos permanentes obtenidos en investigaciones de laboratorio
        self.max_comida += self.bonus_capacidad_comida_inv
        self.max_agua += self.bonus_capacidad_agua_inv
        self.max_energia += self.bonus_capacidad_energia_inv

        # 3. Solo aplicar el límite superior (máximo), sin límite negativo
        self.recursos["comida"] = min(self.recursos["comida"], self.max_comida)
        self.recursos["agua"] = min(self.recursos["agua"], self.max_agua)
        self.recursos["electricidad"] = min(self.recursos["electricidad"], self.max_energia)

    def realizar_intercambio(self, recurso_dar, recurso_recibir, cantidad):
        """Realiza intercambio de recursos con comisión del 10%"""
        if recurso_dar == recurso_recibir:
            return False, "No puedes intercambiar un recurso por sí mismo"
        
        # Mapeo de claves de recursos
        recurso_dar_key = "dinero" if recurso_dar == "dinero" else recurso_dar
        recurso_recibir_key = "dinero" if recurso_recibir == "dinero" else recurso_recibir
        
        # Obtener cantidad actual del recurso a dar
        if recurso_dar == "dinero":
            cantidad_actual = self.dinero
        else:
            cantidad_actual = self.recursos.get(recurso_dar, 0)
        
        # Verificar que hay suficiente
        if cantidad_actual < cantidad:
            return False, f"No tienes suficiente {recurso_dar} (necesitas {cantidad}, tienes {int(cantidad_actual)})"
        
        # Calcular comisión (10%)
        comision = int(cantidad * 0.10)
        cantidad_neta = cantidad - comision
        
        if cantidad_neta <= 0:
            return False, "La cantidad es muy pequeña después de la comisión"
        
        self.intercambios_realizados += 1
        
        # Realizar el intercambio
        # Restar lo que damos
        if recurso_dar == "dinero":
            self.dinero -= cantidad
        else:
            self.recursos[recurso_dar] -= cantidad
        
        # Sumar lo que recibimos (sin comisión)
        if recurso_recibir == "dinero":
            self.dinero += cantidad_neta
        else:
            self.recursos[recurso_recibir] += cantidad_neta
        
        # Crear noticia
        comision_txt = f" (-{comision} comisión)"
        msg = f"Intercambio: -{cantidad} {recurso_dar} +{cantidad_neta} {recurso_recibir}{comision_txt}"
        
        return True, msg

    def aplicar_efectos_evento(self, efectos, coste_dinero=0):
        # 1. Restar el coste de la opción elegida
        self.dinero -= coste_dinero

        for recurso, valor in efectos.items():
            # Usamos self.recursos porque asi lo tienes en avanzar_ano
            if recurso in self.recursos:
                self.recursos[recurso] += valor
                
            elif recurso == "felicidad":
                self.poblacion_stats["promedios"]["felicidad_media"] = max(
                    0.0,
                    min(100.0, self.get_felicidad_media() + float(valor))
                )
                    
            elif recurso == "habitantes":
                if valor > 0:
                    self.agregar_ciudadanos(int(valor), "Adultos")
                elif valor < 0:
                    self.reducir_poblacion(abs(int(valor)))

        # 2. Cerrar el popup después de aplicar
        self.mostrar_popup_evento = False
        self.evento_actual = None
        
        self.noticias.append({"txt": "Se han aplicado las consecuencias del evento", "tipo": "AVISO"})

    def guardar_partida(self):
        """Guarda la partida actual actualizando su nombre registrado"""
        # Usar el nombre de la partida guardado en LogicaCiudad
        nombre_guardado = self.nombre_partida_actual if self.nombre_partida_actual else f"Ano {self.ano}"
        
        datos_partida = {
            "nombre": nombre_guardado,
            "dinero": self.dinero,
            "ano": self.ano,
            "recursos": self.recursos,
            "poblacion": [],
            "poblacion_stats": self.poblacion_stats,
            "edificios": [
                {
                    "id_edificio": e.id_edificio,
                    "nombre": e.nombre, 
                    "x": e.x, 
                    "y": e.y,
                    "capacidad_max_vivienda": e.capacidad_max_vivienda,
                    "es_inicial_gratis": getattr(e, "es_inicial_gratis", False)
                }
                for e in self.edificios
            ],
            "capacidad_max_poblacion": self.capacidad_max_poblacion,
            "poblacion_inicial": self.poblacion_inicial,
            "nivel_tecnologico": self.nivel_tecnologico,
            "investigaciones_completadas": list(self.investigaciones_completadas),
            "capitulo_actual": self.capitulo_actual,
            "misiones_completadas": list(self.misiones_completadas),
            "cofres_abiertos": list(self.cofres_abiertos),
            "intercambios_realizados": self.intercambios_realizados,
            "estado_inicio_capitulo": self._serializar_estado(self.estado_inicio_capitulo),
            # ── Árbol tecnológico de Economía ──────────────────────────────────
            "niveles_arbol":           self.niveles_arbol,
            "bonus_ingreso_pct":       self.bonus_ingreso_pct,
            "descuento_mantenimiento": self.descuento_mantenimiento,
            "descuento_edificios":     self.descuento_edificios,
            "reduccion_tiempo_investigacion": self.reduccion_tiempo_investigacion,
            "bonus_capacidad_comida_inv": self.bonus_capacidad_comida_inv,
            "bonus_capacidad_agua_inv": self.bonus_capacidad_agua_inv,
            "bonus_capacidad_energia_inv": self.bonus_capacidad_energia_inv,
              "bonos_investigacion_version": 1,
              "investigaciones_ano": dict(self.investigaciones_ano),
              "arbol_subidas_ano": {k: list(v) for k, v in self.arbol_subidas_ano.items()},
        }

        ruta_partidas = self.juego.ruta_partida
        
        try:
            # Cargar partidas existentes
            partidas_guardadas = []
            if os.path.exists(ruta_partidas):
                try:
                    with open(ruta_partidas, "r", encoding="utf-8") as f:
                        datos_guardados = json.load(f)
                        # Si es un array, usarlo; si es un objeto, convertir a array
                        if isinstance(datos_guardados, list):
                            partidas_guardadas = datos_guardados
                        else:
                            partidas_guardadas = [datos_guardados]
                except:
                    partidas_guardadas = []
            
            # Buscar y actualizar partida con nombre actual
            partida_encontrada = False
            for i, p in enumerate(partidas_guardadas):
                if p.get("nombre") == nombre_guardado:
                    partidas_guardadas[i] = datos_partida
                    partida_encontrada = True
                    break
            
            if not partida_encontrada:
                partidas_guardadas.append(datos_partida)
            
            # Guardar todas las partidas como array
            with open(ruta_partidas, "w", encoding="utf-8") as f:
                json.dump(partidas_guardadas, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Error guardando partida: {e}")

    def guardar_partida_con_nombre(self, nombre_partida=""):

        """Guarda la partida con un nombre específico en un sistema de múltiples partidas"""
        datos_partida = {
            "nombre": nombre_partida,
            "dinero": self.dinero,
            "ano": self.ano,
            "recursos": self.recursos,
            "poblacion": [],
            "poblacion_stats": self.poblacion_stats,
            "edificios": [
                {
                    "id_edificio": e.id_edificio,
                    "nombre": e.nombre, 
                    "x": e.x, 
                    "y": e.y,
                    "capacidad_max_vivienda": e.capacidad_max_vivienda,
                    "es_inicial_gratis": getattr(e, "es_inicial_gratis", False)
                }
                for e in self.edificios
            ],
            "capacidad_max_poblacion": self.capacidad_max_poblacion,
            "poblacion_inicial": self.poblacion_inicial,
            "nivel_tecnologico": self.nivel_tecnologico,
            "investigaciones_completadas": list(self.investigaciones_completadas),
            "capitulo_actual": self.capitulo_actual,
            "misiones_completadas": list(self.misiones_completadas),
            "cofres_abiertos": list(self.cofres_abiertos),
            "intercambios_realizados": self.intercambios_realizados,
            "estado_inicio_capitulo": self._serializar_estado(self.estado_inicio_capitulo),
            # ── Árbol tecnológico de Economía ──────────────────────────────────
            "niveles_arbol":           self.niveles_arbol,
            "bonus_ingreso_pct":       self.bonus_ingreso_pct,
            "descuento_mantenimiento": self.descuento_mantenimiento,
            "descuento_edificios":     self.descuento_edificios,
            "bonus_capacidad_comida_inv": self.bonus_capacidad_comida_inv,
            "bonus_capacidad_agua_inv": self.bonus_capacidad_agua_inv,
            "bonus_capacidad_energia_inv": self.bonus_capacidad_energia_inv,
            "bonos_investigacion_version": 1,
        }

        # Guardar en archivo de partidas
        ruta_partidas = self.juego.ruta_partida
        
        try:
            # Cargar partidas existentes
            partidas_guardadas = []
            if os.path.exists(ruta_partidas):
                with open(ruta_partidas, "r", encoding="utf-8") as f:
                    partidas_guardadas = json.load(f)
            
            # Buscar si ya existe una partida con este nombre y agregar sufijo si es necesario
            nombre_base = nombre_partida
            contador = 1
            while any(p.get("nombre") == nombre_partida for p in partidas_guardadas):
                contador += 1
                nombre_partida = f"{nombre_base} ({contador})"
            
            if len(partidas_guardadas) >= 5:
                return {"exito": False, "error": "max_partidas"}
            datos_partida["nombre"] = nombre_partida
            partidas_guardadas.append(datos_partida)
            
            # Guardar todas las partidas
            with open(ruta_partidas, "w", encoding="utf-8") as f:
                json.dump(partidas_guardadas, f, ensure_ascii=False, indent=4)
            
            # Actualizar nombre de partida actual después de guardar
            self.nombre_partida_actual = nombre_partida
            return {"exito": True}
        except Exception as e:
            print(f"Error guardando partida con nombre: {e}")
            return {"exito": False, "error": "exception"}

    def cargar_partida(self, partida_dict=None):
        """Carga una partida. Si partida_dict es None, la crea nueva"""
        if partida_dict is None:
            # Nueva partida - ya está inicializada en __init__
            self.aplicar_limites_dinamicos()
            return True
        
        # Cargar partida existente
        try:
            self.dinero = partida_dict.get("dinero", 100000)
            self.ano = partida_dict.get("ano", 0)
            self.nombre_partida_actual = partida_dict.get("nombre", f"Ano {self.ano}")  # 🔧 RESTAURAR nombre
            self.recursos = partida_dict.get("recursos", self.recursos)
            self.capacidad_max_poblacion = partida_dict.get("capacidad_max_poblacion", 100)
            self.poblacion_inicial = partida_dict.get("poblacion_inicial", 100)
            
            # Cargar investigaciones, nivel tecnológico y sistema de capítulos
            self.nivel_tecnologico = partida_dict.get("nivel_tecnologico", 1)
            self.investigaciones_completadas = set(partida_dict.get("investigaciones_completadas", []))
            self.capitulo_actual = partida_dict.get("capitulo_actual", 1)
            self.misiones_completadas = set(partida_dict.get("misiones_completadas", []))
            self.cofres_abiertos = set(partida_dict.get("cofres_abiertos", []))
            self.intercambios_realizados = partida_dict.get("intercambios_realizados", 0)

            # ── Árbol tecnológico de Economía ──────────────────────────────────
            self.niveles_arbol           = partida_dict.get("niveles_arbol", {})
            self.bonus_ingreso_pct       = partida_dict.get("bonus_ingreso_pct", 0.0)
            self.descuento_mantenimiento = partida_dict.get("descuento_mantenimiento", 0.0)
            self.descuento_edificios     = partida_dict.get("descuento_edificios", 0.0)
            self.reduccion_tiempo_investigacion = partida_dict.get("reduccion_tiempo_investigacion", 0.0)
            self.bonus_capacidad_comida_inv = partida_dict.get("bonus_capacidad_comida_inv", 0)
            self.bonus_capacidad_agua_inv = partida_dict.get("bonus_capacidad_agua_inv", 0)
            self.bonus_capacidad_energia_inv = partida_dict.get("bonus_capacidad_energia_inv", 0)
            self.investigaciones_ano = partida_dict.get("investigaciones_ano", {})
            self.arbol_subidas_ano = {k: list(v) for k, v in partida_dict.get("arbol_subidas_ano", {}).items()}
            bonos_inv_version = partida_dict.get("bonos_investigacion_version", 0)

            # Regenerar lista de misiones para el capítulo correcto
            self.generar_misiones_capitulo()

            # Restaurar el checkpoint de inicio de capítulo desde el JSON guardado
            self.estado_inicio_capitulo = self._deserializar_estado(
                partida_dict.get("estado_inicio_capitulo", None)
            )

            # Reconstruir edificios_desbloqueados a partir de las investigaciones guardadas
            for inv_id in self.investigaciones_completadas:
                datos_inv = self.datos_investigacion.get(inv_id, {})
                for edificio in datos_inv.get("edificios_desbloquea", []):
                    if edificio not in self.edificios_desbloqueados:
                        self.edificios_desbloqueados.append(edificio)

            # Recalcular bonos de capacidad por si la partida guardada es antigua
            if ("bonus_capacidad_comida_inv" not in partida_dict or
                    "bonus_capacidad_agua_inv" not in partida_dict or
                    "bonus_capacidad_energia_inv" not in partida_dict):
                self.recalcular_bonos_investigacion()

            # Migración para partidas viejas: aplicar una sola vez efectos de investigación
            if bonos_inv_version < 1:
                for inv_id in self.investigaciones_completadas:
                    efecto = self.datos_investigacion.get(inv_id, {}).get("efecto", {})
                    efecto_migracion = {
                        "bonus_ingreso_pct": efecto.get("bonus_ingreso_pct", 0.0),
                        "descuento_mantenimiento": efecto.get("descuento_mantenimiento", 0.0),
                        "descuento_edificios": efecto.get("descuento_edificios", 0.0),
                    }
                    self._aplicar_efectos_investigacion(efecto_migracion)

            # --- Reconstruir edificios ---
            self.edificios = []
            for d in partida_dict.get("edificios", []):
                es_inicial_gratis = self._es_edificio_inicial_guardado(d)
                data_final = self._crear_data_edificio(d["nombre"], es_inicial_gratis)
                if data_final:
                    nuevo = Edificio(data_final, d["x"], d["y"])
                    # 🔧 RESTAURAR UUID
                    nuevo.id_edificio = d.get("id_edificio", nuevo.id_edificio)
                    self.edificios.append(nuevo)

            # --- Migrar/Cargar población agregada ---
            stats_guardadas = partida_dict.get("poblacion_stats", None)
            if isinstance(stats_guardadas, dict):
                self.poblacion_stats = stats_guardadas
                self.normalizar_poblacion_stats()
            else:
                pob_lista = partida_dict.get("poblacion", [])
                total = len(pob_lista)
                ninos = 0
                adultos = 0
                ancianos = 0
                con_casa = 0
                empleados = 0
                suma_salud = 0.0
                suma_felicidad = 0.0
                for c in pob_lista:
                    edad = int(c.get("edad", 25))
                    rango_txt = c.get("rango_etario", "Adulto")
                    if rango_txt in ("Niño", "Niños") or edad < 18:
                        ninos += 1
                    elif rango_txt == "Anciano" or edad >= 65:
                        ancianos += 1
                    else:
                        adultos += 1
                    if c.get("tiene_casa", False):
                        con_casa += 1
                    if c.get("tiene_empleo", False):
                        empleados += 1
                    suma_salud += float(c.get("salud", 80))
                    suma_felicidad += float(c.get("felicidad", 80))

                salud_media = (suma_salud / total) if total else 80.0
                felicidad_media = (suma_felicidad / total) if total else 80.0
                self.poblacion_stats = {
                    "poblacion_total": total,
                    "rangos_etarios": {"Niños": ninos, "Adultos": adultos, "Ancianos": ancianos},
                    "empleo": {"empleados": empleados, "desempleados": max(0, total - empleados)},
                    "vivienda": {"con_casa": con_casa, "sin_casa": max(0, total - con_casa)},
                    "promedios": {"salud_media": salud_media, "felicidad_media": felicidad_media},
                }
                self.normalizar_poblacion_stats()

            # 🔧 RECALCULAR capacidad de población y límites después de cargar TODO
            self.actualizar_capacidad_max_poblacion()
            self.aplicar_limites_dinamicos()

            return True

        except Exception as e:
            print(f"Error cargando partida: {e}")
            return False
        
    def avanzar_ano(self):
        if self.get_poblacion_total() <= 0:
            self.game_over = True
        
        self.ano += 1
        pob_inicial = self.get_poblacion_total()
        self.noticias = []

        self.actualizar_consumos_totales()

        n_pob = self.get_poblacion_total()

        # 10% de probabilidad anual de que se active un evento aleatorio
        if random.random() < 0.10:
            self.evento_actual = random.choice(self.eventos_posibles)
            self.mostrar_popup_evento = True
            self.noticias.append({
                "txt": f"Evento: {self.evento_actual.get('titulo', 'Evento Desconocido')}",
                "tipo": "EVENTO"
            })
            if hasattr(self.juego, 'reproducir_sonido'):
                self.juego.reproducir_sonido("evento")

        dinero_por_persona = INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100)
        impuestos_totales = n_pob * dinero_por_persona

        # Aplicar bonificación de impuestos del árbol tecnológico
        impuestos_totales = impuestos_totales * (1.0 + self.bonus_ingreso_pct)

        ingresos_edif = sum(getattr(e, 'produccion_dinero', 0) for e in self.edificios)

        # Aplicar descuento de mantenimiento del árbol tecnológico
        mantenimiento_efectivo = self.total_mantenimiento_anual * (
            1.0 - self.descuento_mantenimiento)

        balance_anual = (impuestos_totales + ingresos_edif) - mantenimiento_efectivo
        self.dinero += balance_anual

        if self.dinero < 0:
            self.anos_en_deuda += 1
            self.noticias.append({"txt": f"¡DEUDA! Ano {self.anos_en_deuda}/3", "tipo": "CRITICO"})
            if self.anos_en_deuda >= 3:
                self.game_over = True
                return
        else:
            self.anos_en_deuda = 0

        # RECURSOS
        self.actualizar_consumos_totales() 
        
        self.recursos["comida"] += self.total_comida_anual
        self.recursos["agua"] += self.total_agua_anual
        self.recursos["electricidad"] += self.total_luz_anual

        self.actualizar_recursos_globales()
        self.aplicar_limites_dinamicos()
        
        # POBLACION
        self.asignar_vivienda_y_empleo()
        
        # 🔥 CONSUMO GLOBAL CON LÍMITE
        consumo_comida = n_pob * CONSUMO_COMIDA_HAB
        consumo_agua = n_pob * CONSUMO_AGUA_HAB
        consumo_electricidad = n_pob * CONSUMO_ELEC_HAB

        # Restar consumo global de recursos
        self.recursos["comida"] -= consumo_comida
        self.recursos["agua"] -= consumo_agua
        self.recursos["electricidad"] -= consumo_electricidad
        
        energia_disponible = max(0, self.recursos["electricidad"] + consumo_electricidad)

        # Sin límite negativo: los recursos pueden caer sin tope

        noticias_sucias = []
        proms = self.poblacion_stats["promedios"]
        if self.recursos["comida"] < 0:
            proms["salud_media"] -= float(DANO_HAMBRE)
            noticias_sucias.append({"txt": "Hambre generalizada", "tipo": "CRITICO"})
        if self.recursos["agua"] < 0:
            proms["salud_media"] -= float(DANO_SED)

        sin_casa = self.poblacion_stats.get("vivienda", {}).get("sin_casa", 0)
        if n_pob > 0 and sin_casa > 0:
            fraccion = sin_casa / n_pob
            proms["felicidad_media"] -= float(DANO_SIN_TECHO_FELIC) * fraccion
            proms["salud_media"] -= 1.0 * fraccion

        # Aplicar balance unificado de felicidad/salud (igual que el panel de análisis)
        delta_felic, delta_salud = self.calcular_balance_anual_felic_salud()
        proms["felicidad_media"] = max(0.0, min(100.0, proms.get("felicidad_media", 80.0) + delta_felic))
        proms["salud_media"] = max(0.0, min(100.0, proms.get("salud_media", 80.0) + delta_salud))

        # Envejecimiento por grupos
        rangos = self.poblacion_stats["rangos_etarios"]
        paso_ninos_adultos = int(rangos["Niños"] * 0.06)
        paso_adultos_ancianos = int(rangos["Adultos"] * 0.025)
        rangos["Niños"] = max(0, rangos["Niños"] - paso_ninos_adultos)
        rangos["Adultos"] = max(0, rangos["Adultos"] + paso_ninos_adultos - paso_adultos_ancianos)
        rangos["Ancianos"] = max(0, rangos["Ancianos"] + paso_adultos_ancianos)

        # Mortalidad anual por grupos (ancianos con mayor riesgo)
        total_actual = self.get_poblacion_total()
        base_mortalidad = random.uniform(0.01, 0.03)
        ancianos = rangos["Ancianos"]
        otros = max(0, total_actual - ancianos)
        muertes_anc = min(ancianos, int(ancianos * min(0.35, base_mortalidad * 2.2)))
        muertes_otros = min(otros, int(otros * base_mortalidad))

        adultos = rangos["Adultos"]
        ninos = rangos["Niños"]
        base_otros = max(1, adultos + ninos)
        muertes_adultos = min(adultos, int(muertes_otros * (adultos / base_otros)))
        muertes_ninos = min(ninos, muertes_otros - muertes_adultos)

        rangos["Ancianos"] = max(0, rangos["Ancianos"] - muertes_anc)
        rangos["Adultos"] = max(0, rangos["Adultos"] - muertes_adultos)
        rangos["Niños"] = max(0, rangos["Niños"] - muertes_ninos)

        # Nacimientos basados en felicidad media
        total_post_mortalidad = rangos["Niños"] + rangos["Adultos"] + rangos["Ancianos"]
        tasa_natalidad = 0.005 + (self.get_felicidad_media() / 100.0) * 0.02
        nacimientos = max(0, int(total_post_mortalidad * tasa_natalidad))
        rangos["Niños"] += nacimientos

        self.poblacion_stats["poblacion_total"] = rangos["Niños"] + rangos["Adultos"] + rangos["Ancianos"]
        self.normalizar_poblacion_stats()

        pob_final = self.get_poblacion_total()
        muertos = pob_inicial - pob_final
        if muertos > 0:
            self.noticias.append({"txt": f"Han fallecido {muertos} ciudadanos", "tipo": "MUERTE"})
        if nacimientos > 0:
            self.noticias.append({"txt": f"Nacimientos: +{nacimientos}", "tipo": "AVISO"})

        self.procesar_noticias(noticias_sucias)
        self.gestionar_inmigracion()
        self.verificar_rango_ciudad()

        self.guardar_partida()

        # Verificar cambio de capítulo
        nuevo_capitulo = (self.ano // 100) + 1
        if nuevo_capitulo > self.capitulo_actual:
            if len(self.misiones_completadas) < len(self.misiones_capitulo):
                # Misiones no completadas: bloquear avance, volver al año 99 y mostrar popup
                self.ano = self.capitulo_actual * 100 - 1
                self.mostrar_popup_bloqueo_capitulo = True
            else:
                # Misiones completadas, avanzar capítulo
                self.capitulo_actual = nuevo_capitulo
                self.mostrar_popup_nuevo_capitulo = True
                self.capitulo_avanzado_a = nuevo_capitulo
                self.cofres_abiertos = set()  # Resetear cofres para el nuevo capítulo
                self.estado_inicio_capitulo = self.guardar_estado_completo()
                self.generar_misiones_capitulo()
                self.misiones_completadas = set()

    def _serializar_estado(self, estado):
        """Convierte un estado completo a formato JSON-serializable (sets → lists)"""
        if estado is None:
            return None
        s = estado.copy()
        s["investigaciones_completadas"] = list(s.get("investigaciones_completadas", set()))
        s["misiones_completadas"] = list(s.get("misiones_completadas", set()))
        s["cofres_abiertos"] = list(s.get("cofres_abiertos", set()))
        return s

    def _deserializar_estado(self, datos):
        """Restaura un estado desde JSON (lists → sets)"""
        if datos is None:
            return None
        e = datos.copy()
        e["investigaciones_completadas"] = set(e.get("investigaciones_completadas", []))
        e["misiones_completadas"] = set(e.get("misiones_completadas", []))
        e["cofres_abiertos"] = set(e.get("cofres_abiertos", []))
        return e

    def guardar_estado_completo(self):
        """Guarda el estado completo actual para reinicio de capítulo"""
        return {
            "dinero": self.dinero,
            "ano": self.ano,
            "recursos": self.recursos.copy(),
            "poblacion": [],
            "poblacion_stats": self.poblacion_stats,
            "edificios": [
                {
                    "id_edificio": e.id_edificio,
                    "nombre": e.nombre, 
                    "x": e.x, 
                    "y": e.y,
                    "capacidad_max_vivienda": e.capacidad_max_vivienda,
                    "es_inicial_gratis": getattr(e, "es_inicial_gratis", False)
                }
                for e in self.edificios
            ],
            "capacidad_max_poblacion": self.capacidad_max_poblacion,
            "poblacion_inicial": self.poblacion_inicial,
            "nivel_tecnologico": self.nivel_tecnologico,
            "investigaciones_completadas": self.investigaciones_completadas.copy(),
            "capitulo_actual": self.capitulo_actual,
            "misiones_completadas": self.misiones_completadas.copy(),
            "cofres_abiertos": self.cofres_abiertos.copy(),
            "niveles_arbol": dict(self.niveles_arbol),
            "bonus_ingreso_pct": self.bonus_ingreso_pct,
            "descuento_mantenimiento": self.descuento_mantenimiento,
            "descuento_edificios": self.descuento_edificios,
            "reduccion_tiempo_investigacion": self.reduccion_tiempo_investigacion,
            "bonus_capacidad_comida_inv": self.bonus_capacidad_comida_inv,
            "bonus_capacidad_agua_inv": self.bonus_capacidad_agua_inv,
            "bonus_capacidad_energia_inv": self.bonus_capacidad_energia_inv,
            "investigaciones_ano": dict(self.investigaciones_ano),
            "arbol_subidas_ano": {k: list(v) for k, v in self.arbol_subidas_ano.items()},
        }

    def cargar_estado_completo(self, estado):
        """Carga un estado completo guardado"""
        self.dinero = estado["dinero"]
        self.ano = estado["ano"]
        self.recursos = estado["recursos"]
        self.poblacion_stats = estado.get("poblacion_stats", self._crear_poblacion_stats_vacia())
        self.normalizar_poblacion_stats()
        
        self.edificios = []
        for d in estado["edificios"]:
            es_inicial_gratis = self._es_edificio_inicial_guardado(d)
            data_final = self._crear_data_edificio(d["nombre"], es_inicial_gratis)
            if data_final:
                nuevo = Edificio(data_final, d["x"], d["y"])
                nuevo.id_edificio = d.get("id_edificio", nuevo.id_edificio)
                self.edificios.append(nuevo)
        
        self.actualizar_capacidad_max_poblacion()
        self.poblacion_inicial = estado["poblacion_inicial"]
        self.nivel_tecnologico = estado["nivel_tecnologico"]
        self.investigaciones_completadas = set(estado["investigaciones_completadas"])
        self.capitulo_actual = estado["capitulo_actual"]
        self.misiones_completadas = set(estado["misiones_completadas"])
        self.cofres_abiertos = set(estado.get("cofres_abiertos", set()))
        self.niveles_arbol = dict(estado.get("niveles_arbol", {}))
        self.bonus_ingreso_pct = estado.get("bonus_ingreso_pct", 0.0)
        self.descuento_mantenimiento = estado.get("descuento_mantenimiento", 0.0)
        self.descuento_edificios = estado.get("descuento_edificios", 0.0)
        self.reduccion_tiempo_investigacion = estado.get("reduccion_tiempo_investigacion", 0.0)
        self.bonus_capacidad_comida_inv = estado.get("bonus_capacidad_comida_inv", 0)
        self.bonus_capacidad_agua_inv = estado.get("bonus_capacidad_agua_inv", 0)
        self.bonus_capacidad_energia_inv = estado.get("bonus_capacidad_energia_inv", 0)
        self.investigaciones_ano = dict(estado.get("investigaciones_ano", {}))
        self.arbol_subidas_ano = {k: list(v) for k, v in estado.get("arbol_subidas_ano", {}).items()}

        self.edificios_desbloqueados = [
            "Casa", "Granja", "Planta Agua", "Central Elec.",
            "Almacen de Comida", "Almacen de Agua", "Almacen de Energia"
        ]
        for inv_id in self.investigaciones_completadas:
            datos_inv = self.datos_investigacion.get(inv_id, {})
            for edificio in datos_inv.get("edificios_desbloquea", []):
                if edificio not in self.edificios_desbloqueados:
                    self.edificios_desbloqueados.append(edificio)
        
        self.aplicar_limites_dinamicos()

    def calcular_balance_anual_felic_salud(self):
        """Calcula el delta anual de felicidad y salud igual que el panel de análisis.
        Excluye sin_casa, hambre y sed porque ya los aplica actualizar_necesidades."""
        n_pob = self.get_poblacion_total()
        if n_pob == 0:
            return 0.0, 0.0

        # Impacto TOTAL de edificios (no promedio)
        counts = {}
        for e in self.edificios:
            counts[e.nombre] = counts.get(e.nombre, 0) + 1
        edificios_no_casa = [ed for ed in EDIFICACIONES if ed[0] != "Casa"]
        delta_felic = round(sum(ed[6] * counts.get(ed[0], 0) for ed in edificios_no_casa), 1)
        delta_salud = round(sum(ed[7] * counts.get(ed[0], 0) for ed in edificios_no_casa), 1)

        # Deuda / Prosperidad
        if self.dinero < 0:
            delta_felic -= 10.0
        elif self.dinero > 50000 and self.recursos.get('comida', 0) > 4000:
            delta_felic += 2.0

        # Sin electricidad (promediado)
        consumo_electricidad = n_pob * CONSUMO_ELEC_HAB
        energia_disp = max(0, self.recursos.get('electricidad', 0) + consumo_electricidad)
        sin_luz = max(0, n_pob - int(energia_disp // CONSUMO_ELEC_HAB))
        if sin_luz > 0:
            delta_felic += round(-5.0 * sin_luz / n_pob, 1)
            delta_salud += round(-float(DANO_SIN_LUZ_SALUD) * sin_luz / n_pob, 1)

        # Balances anuales negativos
        prod_comida = sum(e.comida for e in self.edificios if e.comida > 0)
        cons_comida = sum(abs(e.comida) for e in self.edificios if e.comida < 0) + (n_pob * CONSUMO_COMIDA_HAB)
        bal_comida = prod_comida - cons_comida

        prod_agua = sum(e.agua for e in self.edificios if e.agua > 0)
        cons_agua = sum(abs(e.agua) for e in self.edificios if e.agua < 0) + (n_pob * CONSUMO_AGUA_HAB)
        bal_agua = prod_agua - cons_agua

        prod_elec = sum(e.elec for e in self.edificios if e.elec > 0)
        cons_elec = sum(abs(e.elec) for e in self.edificios if e.elec < 0) + (n_pob * CONSUMO_ELEC_HAB)
        bal_elec = prod_elec - cons_elec

        dinero_por_persona = INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100)
        ingresos_edif = sum(getattr(e, 'produccion_dinero', 0) for e in self.edificios)
        bal_dinero = (n_pob * dinero_por_persona + ingresos_edif) - self.total_mantenimiento_anual

        if bal_comida < 0:
            delta_felic -= 2.0
            delta_salud -= 1.0
        if bal_agua < 0:
            delta_felic -= 2.0
            delta_salud -= 1.0
        if bal_elec < 0:
            delta_felic -= 2.0
            delta_salud -= 1.0
        if bal_dinero < 0:
            delta_felic -= 2.0
            delta_salud -= 1.0

        # Ciudad infeliz
        avg_felic = self.get_felicidad_media()
        if avg_felic < 20:
            delta_salud -= 3.0

        return round(delta_felic, 1), round(delta_salud, 1)

    def reiniciar_capitulo(self):
        if self.capitulo_actual == 1:
            # Reinicio total para capítulo 1
            self.__init__(self.juego, self.nombre_partida_actual)
            return

        capitulo_start_ano = (self.capitulo_actual - 1) * 100

        # ── Guardar tracking de años ANTES de restaurar el snapshot ──────────
        # (cargar_estado_completo puede sobreescribirlos con datos de la snapshot)
        inv_ano_actual     = dict(self.investigaciones_ano)
        arbol_ano_actual   = {k: list(v) for k, v in self.arbol_subidas_ano.items()}
        hay_tracking       = bool(inv_ano_actual or arbol_ano_actual)

        # ── Restaurar estado ciudad (dinero, año, recursos, población, edificios) ──
        if self.estado_inicio_capitulo:
            self.cargar_estado_completo(self.estado_inicio_capitulo)
        else:
            self.ano = capitulo_start_ano

        # ── Restauración quirúrgica del estado tecnológico ────────────────────
        if hay_tracking:
            # Laboratorio: mantener solo investigaciones de capítulos anteriores
            self.investigaciones_completadas = {
                inv_id for inv_id, ano in inv_ano_actual.items()
                if ano < capitulo_start_ano
            }
            self.investigaciones_ano = {
                inv_id: ano for inv_id, ano in inv_ano_actual.items()
                if ano < capitulo_start_ano
            }

            # Árbol: recalcular niveles contando solo subidas previas al capítulo
            self.arbol_subidas_ano = {}
            self.niveles_arbol = {}
            for key, anios in arbol_ano_actual.items():
                previos = [a for a in anios if a < capitulo_start_ano]
                if previos:
                    self.arbol_subidas_ano[key] = previos
                    cat, _, nid = key.partition("::")
                    self.niveles_arbol.setdefault(cat, {})[nid] = len(previos)

            # Reconstruir edificios_desbloqueados
            self.edificios_desbloqueados = [
                "Casa", "Granja", "Planta Agua", "Central Elec.",
                "Almacen de Comida", "Almacen de Agua", "Almacen de Energia"
            ]
            for inv_id in self.investigaciones_completadas:
                datos_inv = self.datos_investigacion.get(inv_id, {})
                for edif in datos_inv.get("edificios_desbloquea", []):
                    if edif not in self.edificios_desbloqueados:
                        self.edificios_desbloqueados.append(edif)

            # Recalcular nivel_tecnologico
            nivel = 1
            for nlvl, reqs in [
                (2, ["comida_2", "agua_2", "energia_2", "alojamiento_2"]),
                (3, ["comida_3", "agua_3", "energia_3", "alojamiento_3"]),
                (4, ["comida_4", "agua_4", "energia_4", "alojamiento_4"]),
            ]:
                if all(inv in self.investigaciones_completadas for inv in reqs):
                    nivel = nlvl
            self.nivel_tecnologico = nivel
        # Si no hay tracking (partida antigua): cargar_estado_completo ya restauró
        # el estado tech desde el snapshot, que es la mejor aproximación posible.

        self.misiones_completadas = set()
        self.cofres_abiertos = set()
        self.noticias.append({"txt": "Capítulo reiniciado.", "tipo": "INFO"})
