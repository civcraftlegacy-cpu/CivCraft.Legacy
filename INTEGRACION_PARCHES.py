# -*- coding: utf-8 -*-
# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.
# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRACION_PARCHES.py
# Guía de integración definitiva — 13 bloques numerados
#
# INSTRUCCIONES PARA LA IA LOCAL:
#   Cada PARCHE indica:
#     ARCHIVO     : el fichero a modificar
#     POSICIÓN    : función / línea de referencia donde insertar
#     ACCIÓN      : AÑADIR / MODIFICAR / REEMPLAZAR
#     CÓDIGO      : el fragmento exacto a insertar o sustituir
#
# REGLA DE ORO: ningún parche elimina funcionalidad existente.
# ═══════════════════════════════════════════════════════════════════════════════

"""
ÍNDICE DE PARCHES
─────────────────
[P01] logica_ciudad.py  — import GestorArboles y EjercitoCiudad
[P02] logica_ciudad.py  — instanciar gestor_arboles y ejercito en __init__
[P03] logica_ciudad.py  — método aplicar_bonos_arboles()
[P04] logica_ciudad.py  — guardar_partida(): serializar árbol y ejército
[P05] logica_ciudad.py  — cargar_partida(): deserializar árbol y ejército
[P06] logica_ciudad.py  — avanzar_ano(): aplicar bonus de impuestos
[P07] logica_ciudad.py  — aplicar_limites_dinamicos(): bonus capacidad
[P08] logica_ciudad.py  — comprar_edificio(): descuento de árbol
[P09] main.py           — import EscenaArbol y EscenaCombate
[P10] main.py           — __init__: instanciar escena_arbol y escena_combate
[P11] main.py           — ejecutar(): estados ARBOL_TECNICO y COMBATE
[P12] main.py           — ejecutar(): procesar retorno ('ARBOL', cat) del menu_inv
[P13] main.py           — dibujar_hud(): cargar y dibujar btn_ataque circular
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 01
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : al inicio del archivo, con los demás imports (antes de "class LogicaCiudad:")
# ACCIÓN    : AÑADIR estas dos líneas
# ═══════════════════════════════════════════════════════════════════════════════
P01_CODIGO = """
from arbol_tecnologico import GestorArboles
from sistema_combate import EjercitoCiudad
"""
# Ejemplo: busca la línea "from entidades import Ciudadano, Edificio"
# y justo debajo añade las dos líneas de arriba.


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 02
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : dentro de LogicaCiudad.__init__, al final de la sección
#             "# --- 1. DECLARACIÓN DE VARIABLES ---"
#             (después de self.intercambios_realizados = 0)
# ACCIÓN    : AÑADIR
# ═══════════════════════════════════════════════════════════════════════════════
P02_CODIGO = """
        # --- ÁRBOL TECNOLÓGICO Y EJÉRCITO ---
        self.gestor_arboles = GestorArboles()
        self.ejercito = EjercitoCiudad()
"""
# Inserta ANTES de la línea "self.poblacion_inicial = 100"


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 03
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : justo antes de def limite_negativo_recurso(…) o donde quieras
#             añadir un método nuevo en la clase
# ACCIÓN    : AÑADIR método completo
# ═══════════════════════════════════════════════════════════════════════════════
P03_CODIGO = """
    def aplicar_bonos_arboles(self, bonos: dict):
        \"\"\"
        Recalcula los límites de almacén sumando los bonos del árbol tecnológico.
        Se llama automáticamente desde GestorArboles._aplicar_efecto().
        \"\"\"
        # Los bonos de capacidad se reflejan en aplicar_limites_dinamicos();
        # simplemente volvemos a calcularlos con los valores actuales.
        self.aplicar_limites_dinamicos()

        # Bonus de felicidad global: se aplica una sola vez al promedio
        bonus_felic = bonos.get("bonus_felicidad_global", 0)
        if bonus_felic != 0:
            for hab in self.poblacion:
                hab.felicidad = max(0, min(100, hab.felicidad + bonus_felic))
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 04
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : dentro de guardar_partida(), en el dict datos_partida
# ACCIÓN    : AÑADIR dos claves al dict antes del cierre "}"
# ═══════════════════════════════════════════════════════════════════════════════
P04_CODIGO = """
            # Árbol tecnológico y ejército
            "gestor_arboles": self.gestor_arboles.serializar(),
            "ejercito": self.ejercito.serializar(),
"""
# Busca la línea:  "estado_inicio_capitulo": self._serializar_estado(…)
# y después de esa línea (antes del cierre '}' del dict) añade las dos de arriba.
# Hacer lo mismo en guardar_partida_con_nombre().


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 05
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : dentro de cargar_partida(), después de la línea
#             "self.aplicar_limites_dinamicos()"  (la última de la función)
# ACCIÓN    : AÑADIR
# ═══════════════════════════════════════════════════════════════════════════════
P05_CODIGO = """
            # Restaurar árbol tecnológico
            datos_arbol = partida_dict.get("gestor_arboles", {})
            if datos_arbol:
                self.gestor_arboles.deserializar(datos_arbol)
                self.gestor_arboles._recalcular_bonos()
                self.aplicar_limites_dinamicos()

            # Restaurar ejército
            datos_ejercito = partida_dict.get("ejercito", {})
            if datos_ejercito:
                self.ejercito.deserializar(datos_ejercito)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 06
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : dentro de avanzar_ano(), busca estas líneas:
#
#   dinero_por_persona = INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100)
#   impuestos_totales = n_pob * dinero_por_persona
#
# ACCIÓN    : REEMPLAZAR esas dos líneas por las de abajo
# ═══════════════════════════════════════════════════════════════════════════════
P06_CODIGO_VIEJO = """
        dinero_por_persona = INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100)
        impuestos_totales = n_pob * dinero_por_persona
"""

P06_CODIGO_NUEVO = """
        dinero_por_persona = INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100)
        # Bonus del árbol: +X% sobre los impuestos base
        mult_impuestos = 1.0 + self.gestor_arboles.bonos.get("multiplicador_impuestos", 0.0)
        impuestos_totales = n_pob * dinero_por_persona * mult_impuestos
        # Bono extra por edificio construido
        extra_por_edificio = self.gestor_arboles.bonos.get("ingreso_extra_edificio", 0)
        edificios_reales = [e for e in self.edificios if e.x >= 0 and e.y >= 0]
        impuestos_totales += extra_por_edificio * len(edificios_reales)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 07
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : dentro de aplicar_limites_dinamicos(), reemplaza el cálculo de
#             self.max_comida, self.max_agua, self.max_energia
# ACCIÓN    : REEMPLAZAR las tres líneas de cálculo por las de abajo
# ═══════════════════════════════════════════════════════════════════════════════
P07_CODIGO_VIEJO = """
        self.max_comida = (n_pob * CONSUMO_COMIDA_HAB * 20) + (almacenes_comida * 5000)
        self.max_agua = (n_pob * CONSUMO_AGUA_HAB * 20) + (almacenes_agua * 5000)
        self.max_energia = (n_pob * CONSUMO_ELEC_HAB * 20) + (almacenes_elec * 5000)
"""

P07_CODIGO_NUEVO = """
        bonos = self.gestor_arboles.bonos
        mult_cap = bonos.get("multiplicador_capacidad", 1.0)

        self.max_comida  = int(((n_pob * CONSUMO_COMIDA_HAB * 20) + (almacenes_comida * 5000)
                                + bonos.get("bonus_capacidad_comida", 0)) * mult_cap)
        self.max_agua    = int(((n_pob * CONSUMO_AGUA_HAB * 20) + (almacenes_agua * 5000)
                                + bonos.get("bonus_capacidad_agua", 0)) * mult_cap)
        self.max_energia = int(((n_pob * CONSUMO_ELEC_HAB * 20) + (almacenes_elec * 5000)
                                + bonos.get("bonus_capacidad_energia", 0)) * mult_cap)
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 08
# ARCHIVO   : logica_ciudad.py
# POSICIÓN  : dentro de comprar_edificio(), busca la línea:
#             "if self.dinero >= tipo_data[1]:"
# ACCIÓN    : AÑADIR el cálculo del descuento ANTES de esa línea
# ═══════════════════════════════════════════════════════════════════════════════
P08_CODIGO = """
        # Aplicar descuento del árbol de avances
        descuento = self.gestor_arboles.bonos.get("descuento_edificios", 0.0)
        coste_final = int(tipo_data[1] * (1.0 - min(descuento, 0.60)))
"""
# Después de añadir P08, sustituye en comprar_edificio:
#   "if self.dinero >= tipo_data[1]:"   →  "if self.dinero >= coste_final:"
#   "self.dinero -= tipo_data[1]"       →  "self.dinero -= coste_final"
#   (solo dentro de comprar_edificio)


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 09
# ARCHIVO   : main.py
# POSICIÓN  : al inicio, entre los imports existentes
#             (junto a "from investigacion import EscenaInvestigacion")
# ACCIÓN    : AÑADIR
# ═══════════════════════════════════════════════════════════════════════════════
P09_CODIGO = """
from investigacion import EscenaInvestigacion, EscenaArbol
from sistema_combate import EscenaCombate
"""
# Reemplaza la línea existente:
#   "from investigacion import EscenaInvestigacion"
# por la de arriba (añade EscenaArbol e importa EscenaCombate)


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 10
# ARCHIVO   : main.py
# POSICIÓN  : en Juego.__init__, después de:
#             "self.estado_actual = 'CIUDAD'"
# ACCIÓN    : AÑADIR
# ═══════════════════════════════════════════════════════════════════════════════
P10_CODIGO = """
        # Escenas del árbol tecnológico y combate (se crean bajo demanda)
        self.escena_arbol  = None   # EscenaArbol activa
        self.escena_combate = EscenaCombate(self.logica)  # mapa mundial
"""
# (EscenaArbol se crea dinámicamente en P12 cuando el usuario elige una categoría)


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 11
# ARCHIVO   : main.py
# POSICIÓN  : dentro del método async ejecutar(), justo ANTES o DESPUÉS del
#             bloque "if self.estado_actual == 'INVESTIGACION':"
# ACCIÓN    : AÑADIR dos nuevos bloques de estado
# ═══════════════════════════════════════════════════════════════════════════════
P11_CODIGO = """
            # ================================================================
            # ESTADO: ÁRBOL TECNOLÓGICO
            # ================================================================
            if self.estado_actual == 'ARBOL_TECNICO':
                if self.ciudad_surface:
                    self.pantalla.blit(self.ciudad_surface, (0, 0))
                else:
                    self.pantalla.fill(NEGRO)
                if self.escena_arbol:
                    self.escena_arbol.dibujar(self.pantalla)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        self.logica.guardar_partida()
                        self.corriendo = False
                    if self.escena_arbol:
                        resultado = self.escena_arbol.manejar_eventos(ev)
                        if resultado == 'INVESTIGACION':
                            self.estado_actual = 'INVESTIGACION'
                pygame.display.flip()
                self.reloj.tick(FPS)
                await asyncio.sleep(0)
                continue

            # ================================================================
            # ESTADO: COMBATE / MAPA MUNDIAL
            # ================================================================
            if self.estado_actual == 'COMBATE':
                if self.ciudad_surface:
                    self.pantalla.blit(self.ciudad_surface, (0, 0))
                else:
                    self.pantalla.fill(NEGRO)
                self.escena_combate.dibujar(self.pantalla)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        self.logica.guardar_partida()
                        self.corriendo = False
                    resultado = self.escena_combate.manejar_eventos(ev)
                    if resultado == 'CIUDAD':
                        self.estado_actual = 'CIUDAD'
                pygame.display.flip()
                self.reloj.tick(FPS)
                await asyncio.sleep(0)
                continue
"""
# Coloca este bloque ANTES de la línea:
#   "# ================================================================"
#   "# ESTADO: LABORATORIO DE INVESTIGACION"
#   (el bloque que empieza con "if self.estado_actual == 'INVESTIGACION':")


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 12
# ARCHIVO   : main.py
# POSICIÓN  : dentro del bloque "if self.estado_actual == 'INVESTIGACION':",
#             busca la línea:
#               "resultado = self.menu_inv.manejar_eventos(ev)"
#             y REEMPLAZA el bloque "if resultado == 'CIUDAD':" que le sigue
# ACCIÓN    : REEMPLAZAR
# ═══════════════════════════════════════════════════════════════════════════════
P12_CODIGO_VIEJO = """
                    resultado = self.menu_inv.manejar_eventos(ev)
                    if resultado == 'CIUDAD':
                        self.estado_actual = 'CIUDAD'
"""

P12_CODIGO_NUEVO = """
                    resultado = self.menu_inv.manejar_eventos(ev)
                    if resultado == 'CIUDAD':
                        self.estado_actual = 'CIUDAD'
                    elif isinstance(resultado, tuple) and resultado[0] == 'ARBOL':
                        cat = resultado[1]
                        gestor = getattr(self.logica, 'gestor_arboles', None)
                        if gestor:
                            self.escena_arbol = EscenaArbol(cat, gestor, self.logica)
                            self.estado_actual = 'ARBOL_TECNICO'
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PARCHE 13
# ARCHIVO   : main.py
# POSICIÓN  : dentro de dibujar_hud(), busca el bloque que dibuja btn_investigar
#             (alrededor de la línea self.btn_investigar = pygame.Rect(…))
#             y después de ese bloque AÑADE el botón de ataque
# ACCIÓN    : AÑADIR (cargar icono en __init__ y dibujar en dibujar_hud)
# ═══════════════════════════════════════════════════════════════════════════════

# En __init__ (junto a la carga de otros iconos), AÑADIR:
P13_CODIGO_INIT = """
        # Icono de ataque (botón de combate)
        ruta_atk = os.path.join(BASE_DIR, "assets", "imagenes", "ataque.png")
        if os.path.exists(ruta_atk):
            self.img_ataque_btn = pygame.image.load(ruta_atk).convert_alpha()
            self.img_ataque_btn = pygame.transform.scale(self.img_ataque_btn, (30, 30))
        else:
            self.img_ataque_btn = None

        # Rect del botón de ataque (junto al de investigar)
        self.btn_ataque = pygame.Rect(0, 0, 60, 60)
"""

# En dibujar_hud(), DESPUÉS del bloque que dibuja btn_investigar, AÑADIR:
P13_CODIGO_HUD = """
        # Botón ATAQUE (a la izquierda del botón Investigar)
        self.btn_ataque = pygame.Rect(ANCHO - 390, ALTO - 80, 60, 60)
        hover_atk = self.btn_ataque.collidepoint(mouse_pos) if hasattr(self, '_mouse_pos') else False
        pygame.draw.circle(self.pantalla, (70, 20, 20), self.btn_ataque.center, 30)
        pygame.draw.circle(self.pantalla, (200, 50, 50), self.btn_ataque.center, 30, 2)
        if self.img_ataque_btn:
            self.pantalla.blit(self.img_ataque_btn,
                               (self.btn_ataque.centerx - 15, self.btn_ataque.centery - 15))
        lbl_atk = self.fuente_p.render("Ataque", True, (220, 100, 100))
        self.pantalla.blit(lbl_atk,
                           (self.btn_ataque.centerx - lbl_atk.get_width() // 2,
                            self.btn_ataque.bottom + 5))
"""

# En el manejador de clicks del estado CIUDAD, AÑADIR la detección del btn_ataque:
P13_CODIGO_CLICK = """
            # Abrir mapa de combate
            if hasattr(self, 'btn_ataque') and self.btn_ataque.collidepoint(pos):
                self.ciudad_surface = self.pantalla.copy()
                self.escena_combate.logica = self.logica   # referencia actualizada
                self.estado_actual = 'COMBATE'
"""
# Añadir este bloque junto a los otros "if btn_X.collidepoint(pos):"
# que se procesan cuando el usuario hace clic en el HUD.


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICACIÓN FINAL
# ═══════════════════════════════════════════════════════════════════════════════
print("""
╔══════════════════════════════════════════════════════════════════╗
║         GUÍA DE INTEGRACIÓN — 13 PARCHES DISPONIBLES           ║
╠══════════════════════════════════════════════════════════════════╣
║  P01-P02  logica_ciudad.py  Imports + instancias en __init__    ║
║  P03      logica_ciudad.py  Método aplicar_bonos_arboles()      ║
║  P04-P05  logica_ciudad.py  Serialización guardar/cargar        ║
║  P06      logica_ciudad.py  Bonus impuestos en avanzar_ano()    ║
║  P07      logica_ciudad.py  Bonus capacidad en limites()        ║
║  P08      logica_ciudad.py  Descuento edificios en comprar()    ║
║  P09-P10  main.py           Imports + instancias nuevas         ║
║  P11      main.py           Estados ARBOL_TECNICO y COMBATE     ║
║  P12      main.py           Procesar ('ARBOL', cat) del menu    ║
║  P13      main.py           Botón Ataque en HUD                 ║
╚══════════════════════════════════════════════════════════════════╝
""")
