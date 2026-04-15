# -*- coding: utf-8 -*-
# Copyright (c) 2026 [Cayetano Tielas Fernandez]. Todos los derechos reservados.
# Módulo: Estado de Juego — Laboratorio de Investigación + Árbol Tecnológico

import pygame
import math
import os

from arbol_tecnologico import CATEGORIAS

BASE_DIR = os.path.dirname(__file__)

# Datos de las 4 tarjetas (orden visible)
TARJETAS_INFO = [
    {"nombre": "RECURSOS",  "cat": "ECONOMÍA"},
    {"nombre": "ECONOMÍA",  "cat": "RECURSOS"},
    {"nombre": "TROPAS",    "cat": "TROPAS"},
    {"nombre": "AVANCES",   "cat": "AVANCES"},
]

# Dimensiones del panel — se calculan en función de IMG_SIZE
_IMG_SIZE    = 560   # imagen completa (cuadrada)
_PADDING     = 12    # margen lateral entre imagen y borde del panel
_HEADER_H    = 62    # altura de la barra superior (título)
_FOOTER_H    = 10    # margen inferior

# Insets dentro de cada cuadrante (280×280) para ajustar al borde real de la carta
_CARD_ML, _CARD_MT = 32, 18   # margen izquierdo, margen superior
_CARD_MR, _CARD_MB = 32, 24   # margen derecho,   margen inferior

PANEL_ANCHO = _IMG_SIZE + _PADDING * 2
PANEL_ALTO  = _HEADER_H + _IMG_SIZE + _FOOTER_H

# Mapa de cuadrante → categoría (orden en spritesheet 2×2)
# (fila, col): top-left, top-right, bottom-left, bottom-right
_ZONAS_CAT = [
    "ECONOMÍA",   # (0,0)
    "RECURSOS",   # (0,1)
    "TROPAS",     # (1,0)
    "AVANCES",    # (1,1)
]


class EscenaInvestigacion:
    """Menú de laboratorio: muestra targetas.png completo sin cortes."""

    def __init__(self):
        self.fuente_titulo  = pygame.font.SysFont("Arial", 38, bold=True)
        self.fuente_cerrar  = pygame.font.SysFont("Arial", 18, bold=True)
        self.fuente_hint    = pygame.font.SysFont("Arial", 13)
        self.fuente_nivel   = pygame.font.SysFont("Arial", 18, bold=True)
        self.fuente_msg     = pygame.font.SysFont("Arial", 19, bold=True)

        # ── Imagen completa targetas.png ──────────────────────────────────────
        ruta_sheet = os.path.join(BASE_DIR, "assets", "imagenes", "targetas.png")
        if os.path.exists(ruta_sheet):
            raw = pygame.image.load(ruta_sheet).convert_alpha()
            self.img_sheet = pygame.transform.smoothscale(raw, (_IMG_SIZE, _IMG_SIZE))
        else:
            # Fallback: 4 cuadrantes de color
            self.img_sheet = pygame.Surface((_IMG_SIZE, _IMG_SIZE))
            colores = [(80,160,80),(180,140,30),(180,60,60),(60,100,180)]
            half = _IMG_SIZE // 2
            for idx, col in enumerate(colores):
                rx = (idx % 2) * half
                ry = (idx // 2) * half
                pygame.draw.rect(self.img_sheet, col, (rx, ry, half, half))

        # Rect del botón cerrar (se calcula en dibujar)
        self.rect_cerrar = None
        # Zona actualmente bajo el cursor (-1 = ninguna)
        self._hover_zona: int = -1
        # Rects de cada cuadrante en coordenadas de pantalla
        self._zonas_rects: list = []

        self.mensaje_texto  = ""
        self.mensaje_frames = 0

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _panel_rect(self, ancho, alto):
        px = ancho // 2 - PANEL_ANCHO // 2
        py = alto  // 2 - PANEL_ALTO  // 2
        return pygame.Rect(px, py, PANEL_ANCHO, PANEL_ALTO)

    def _imagen_origen(self, panel):
        """Coordenadas (x,y) de la esquina superior-izquierda de la imagen dentro del panel."""
        return panel.x + _PADDING, panel.y + _HEADER_H

    # ── Dibujar ───────────────────────────────────────────────────────────────
    def dibujar(self, pantalla, nivel_ciudad=1):
        ancho, alto = pantalla.get_size()
        panel = self._panel_rect(ancho, alto)
        mouse_pos = pygame.mouse.get_pos()
        img_x, img_y = self._imagen_origen(panel)
        half = _IMG_SIZE // 2

        # Calcular cuadrantes completos (solo para referencia interna)
        self._zonas_rects = []
        # Calcular rects ajustados a la carta real dentro de cada cuadrante
        self._card_rects = []
        for idx in range(4):
            qx = img_x + (idx % 2) * half
            qy = img_y + (idx // 2) * half
            self._zonas_rects.append(pygame.Rect(qx, qy, half, half))
            self._card_rects.append(pygame.Rect(
                qx + _CARD_ML,
                qy + _CARD_MT,
                half - _CARD_ML - _CARD_MR,
                half - _CARD_MT - _CARD_MB,
            ))

        # Detectar hover (solo sobre el área real de la carta)
        self._hover_zona = -1
        for idx, r in enumerate(self._card_rects):
            if r.collidepoint(mouse_pos):
                self._hover_zona = idx
                break

        # 1 — Overlay oscuro sobre la ciudad
        ov = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        pantalla.blit(ov, (0, 0))

        # 2 — Panel fondo azul oscuro
        pygame.draw.rect(pantalla, (8, 12, 30), panel, border_radius=14)

        # 3 — Borde del panel (azul-índigo fino)
        pygame.draw.rect(pantalla, (60, 85, 190), panel, 3, border_radius=14)

        # 4 — Barra de título (franja más oscura arriba)
        barra = pygame.Rect(panel.x + 3, panel.y + 3, PANEL_ANCHO - 6, _HEADER_H - 6)
        pygame.draw.rect(pantalla, (12, 16, 42), barra, border_radius=11)

        # 5 — Título "LABORATORIO"
        txt_t = self.fuente_titulo.render("LABORATORIO", True, (220, 230, 255))
        pantalla.blit(txt_t, (
            panel.centerx - txt_t.get_width() // 2,
            panel.y + (_HEADER_H - txt_t.get_height()) // 2,
        ))

        # 6 — Separador fino bajo el título
        sep_y = panel.y + _HEADER_H - 1
        pygame.draw.line(pantalla, (60, 85, 190), (panel.x + 3, sep_y), (panel.right - 3, sep_y), 1)

        # 7 — Botón X
        self.rect_cerrar = pygame.Rect(panel.right - 38, panel.y + 8, 30, 30)
        col_x = (210, 40, 40) if self.rect_cerrar.collidepoint(mouse_pos) else (140, 25, 25)
        pygame.draw.rect(pantalla, col_x, self.rect_cerrar, border_radius=6)
        tx = self.fuente_cerrar.render("X", True, (255, 255, 255))
        pantalla.blit(tx, (
            self.rect_cerrar.centerx - tx.get_width() // 2,
            self.rect_cerrar.centery - tx.get_height() // 2,
        ))

        # 8 — Imagen completa (sin cortes)
        pantalla.blit(self.img_sheet, (img_x, img_y))

        # 9 — Resaltar carta en hover: borde dorado ajustado a la carta real
        # if self._hover_zona >= 0:
        #     hz = self._card_rects[self._hover_zona]
        #     pygame.draw.rect(pantalla, (255, 215, 0), hz, 3, border_radius=8)

        # 10 — Hint
        txt_esc = self.fuente_hint.render("[ ESC ]  Cerrar", True, (80, 90, 120))
        pantalla.blit(txt_esc, (panel.x + 8, panel.bottom - 16))

        # 11 — Mensaje temporal
        if self.mensaje_frames > 0:
            alpha = min(255, self.mensaje_frames * 4)
            ms = self.fuente_msg.render(self.mensaje_texto, True, (255, 220, 80))
            ms.set_alpha(alpha)
            pantalla.blit(ms, (panel.centerx - ms.get_width() // 2,
                               panel.centery - ms.get_height() // 2))
            self.mensaje_frames -= 1

    # ── Eventos ───────────────────────────────────────────────────────────────
    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return 'CIUDAD'

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.rect_cerrar and self.rect_cerrar.collidepoint(pos):
                return 'CIUDAD'
            for idx, rect in enumerate(self._card_rects):
                if rect.collidepoint(pos):
                    return ('ARBOL', _ZONAS_CAT[idx])

        return None

# ══════════════════════════════════════════════════════════════════════════════
# ESCENA ÁRBOL TECNOLÓGICO
# ══════════════════════════════════════════════════════════════════════════════

# Constantes de layout
_NODO_W   = 150
_NODO_H   = 70
_GAP_X    = 30
_GAP_Y    = 20

_COLOR_BG          = (10, 12, 28)
_COLOR_BORDE_PANEL = (60, 90, 160)
_COLOR_NODO_BG     = (24, 30, 50)
_COLOR_COMPRADO    = (30, 90, 40)
_COLOR_DISPONIBLE  = (40, 60, 100)
_COLOR_BLOQUEADO   = (35, 35, 45)
_COLOR_POPUP_BG    = (15, 20, 40)


class EscenaArbol:
    """
    Visualizacion de un arbol tecnologico en cuadricula estilo RPG.

    Flujo devuelto por manejar_eventos():
      'INVESTIGACION' -> volver al menu de tarjetas
      None            -> sin cambio

    Parametros:
      categoria : clave en CATEGORIAS ('ECONOMIA', 'RECURSOS', ...)
      gestor    : instancia de GestorArboles (de logica_ciudad)
      logica    : instancia de LogicaCiudad
    """

    _PANEL_W = 980
    _PANEL_H = 620

    def __init__(self, categoria: str, gestor, logica):
        self.categoria = categoria
        self.gestor = gestor
        self.logica = logica

        cat_data = CATEGORIAS[categoria]
        self.arbol: dict = cat_data["arbol"]
        self.color_cat: tuple = cat_data["color"]

        self.fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_nodo   = pygame.font.SysFont("Arial", 12, bold=True)
        self.fuente_desc   = pygame.font.SysFont("Arial", 11)
        self.fuente_cerrar = pygame.font.SysFont("Arial", 18, bold=True)
        self.fuente_popup  = pygame.font.SysFont("Arial", 14)
        self.fuente_popup_b= pygame.font.SysFont("Arial", 14, bold=True)
        self.fuente_hint   = pygame.font.SysFont("Arial", 12)

        self.popup_nodo: str = None
        self.popup_msg: str  = ""
        self.popup_msg_frames: int = 0

        self.rect_cerrar = None
        self._rects_nodos: dict = {}
        self._rect_popup_comprar  = None
        self._rect_popup_cancelar = None

        self._posiciones: dict = self._calcular_posiciones()

    # -- Layout ---------------------------------------------------------------
    def _calcular_posiciones(self) -> dict:
        return {
            nid: (datos["nivel"] - 1, datos["fila"])
            for nid, datos in self.arbol.items()
        }

    def _nodo_rect(self, panel, col: int, fila: int):
        area_x = panel.x + 16
        area_y = panel.y + 56
        x = area_x + col * (_NODO_W + _GAP_X)
        y = area_y + fila * (_NODO_H + _GAP_Y)
        return pygame.Rect(x, y, _NODO_W, _NODO_H)

    def _panel_rect(self, ancho, alto):
        px = ancho // 2 - self._PANEL_W // 2
        py = alto  // 2 - self._PANEL_H // 2
        return pygame.Rect(px, py, self._PANEL_W, self._PANEL_H)

    # -- Dibujar --------------------------------------------------------------
    def dibujar(self, pantalla):
        ancho, alto = pantalla.get_size()
        panel = self._panel_rect(ancho, alto)
        mouse_pos = pygame.mouse.get_pos()

        # Overlay
        ov = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 190))
        pantalla.blit(ov, (0, 0))

        pygame.draw.rect(pantalla, _COLOR_BG, panel, border_radius=12)
        pygame.draw.rect(pantalla, self.color_cat, panel, 3, border_radius=12)

        txt_t = self.fuente_titulo.render(
            f"ARBOL: {self.categoria}   |   Oro: ${self.logica.dinero:,}",
            True, self.color_cat,
        )
        pantalla.blit(txt_t, (panel.x + 16, panel.y + 14))

        self.rect_cerrar = pygame.Rect(panel.right - 42, panel.y + 8, 34, 34)
        col_x = (220, 40, 40) if self.rect_cerrar.collidepoint(mouse_pos) else (150, 30, 30)
        pygame.draw.rect(pantalla, col_x, self.rect_cerrar, border_radius=6)
        tx = self.fuente_cerrar.render("X", True, (255, 255, 255))
        pantalla.blit(tx, (self.rect_cerrar.centerx - tx.get_width() // 2,
                           self.rect_cerrar.centery - tx.get_height() // 2))

        # -- Lineas conectoras ------------------------------------------------
        self._rects_nodos.clear()
        for nid, datos in self.arbol.items():
            col, fila = self._posiciones[nid]
            r_hijo = self._nodo_rect(panel, col, fila)
            for req in datos["requiere"]:
                if req in self._posiciones:
                    col_p, fila_p = self._posiciones[req]
                    r_padre = self._nodo_rect(panel, col_p, fila_p)
                    p1 = (r_padre.right, r_padre.centery)
                    p2 = (r_hijo.left,  r_hijo.centery)
                    col_l = self.color_cat if req in self.gestor.comprados else (60, 60, 80)
                    pygame.draw.line(pantalla, col_l, p1, p2, 2)

        # -- Nodos ------------------------------------------------------------
        for nid, datos in self.arbol.items():
            col, fila = self._posiciones[nid]
            rect = self._nodo_rect(panel, col, fila)
            self._rects_nodos[nid] = rect

            comprado   = nid in self.gestor.comprados
            ok, motivo = self.gestor.puede_comprar(nid, self.logica.dinero)
            disponible = ok and not comprado
            hover      = rect.collidepoint(mouse_pos) and not comprado

            if comprado:
                bg = _COLOR_COMPRADO
                borde = (80, 200, 80)
            elif disponible:
                bg = _COLOR_DISPONIBLE
                borde = self.color_cat if hover else (70, 100, 150)
            else:
                bg = _COLOR_BLOQUEADO
                borde = (50, 50, 65)

            pygame.draw.rect(pantalla, bg, rect, border_radius=8)
            pygame.draw.rect(pantalla, borde, rect, 2, border_radius=8)

            ic = datos.get("icono_color", (150, 150, 200))
            pygame.draw.rect(pantalla, ic, (rect.x + 6, rect.y + 6, 14, 14), border_radius=3)

            col_txt = (150, 240, 150) if comprado else ((240, 240, 240) if disponible else (110, 110, 130))
            txt_n = self.fuente_nodo.render(datos["nombre"], True, col_txt)
            pantalla.blit(txt_n, (rect.x + 24, rect.y + 6))

            col_desc = (160, 160, 180) if disponible else (90, 90, 110)
            desc_lines = self._wrap(datos["descripcion"], self.fuente_desc, _NODO_W - 10)
            for i, linea in enumerate(desc_lines[:2]):
                txt_d = self.fuente_desc.render(linea, True, col_desc)
                pantalla.blit(txt_d, (rect.x + 6, rect.y + 26 + i * 14))

            col_coste = (255, 215, 0) if disponible else (100, 100, 80)
            txt_c = self.fuente_desc.render(f"${datos['coste_oro']:,}", True, col_coste)
            pantalla.blit(txt_c, (rect.x + 6, rect.bottom - 17))

            if comprado:
                chk = self.fuente_nodo.render("OK", True, (100, 255, 100))
                pantalla.blit(chk, (rect.right - 22, rect.y + 4))
            elif not disponible:
                lk = self.fuente_desc.render("[BLQ]", True, (80, 80, 100))
                pantalla.blit(lk, (rect.right - 34, rect.y + 4))

        hint = self.fuente_hint.render(
            "Clic en nodo disponible para comprar  |  [ESC] Volver", True, (80, 80, 110)
        )
        pantalla.blit(hint, (panel.x + 16, panel.bottom - 22))

        if self.popup_nodo:
            self._dibujar_popup(pantalla, panel, mouse_pos)

        if self.popup_msg_frames > 0:
            alpha = min(255, self.popup_msg_frames * 5)
            msg_s = self.fuente_popup_b.render(self.popup_msg, True, (255, 220, 80))
            msg_s.set_alpha(alpha)
            pantalla.blit(msg_s, (panel.centerx - msg_s.get_width() // 2, panel.bottom - 46))
            self.popup_msg_frames -= 1

    def _dibujar_popup(self, pantalla, panel, mouse_pos):
        nid = self.popup_nodo
        if nid not in self.arbol:
            self.popup_nodo = None
            return
        datos = self.arbol[nid]
        pw, ph = 340, 190
        px = panel.centerx - pw // 2
        py = panel.centery - ph // 2

        pygame.draw.rect(pantalla, _COLOR_POPUP_BG, (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(pantalla, self.color_cat, (px, py, pw, ph), 2, border_radius=12)

        y = py + 14
        txt_n = self.fuente_popup_b.render(datos["nombre"], True, self.color_cat)
        pantalla.blit(txt_n, (px + pw // 2 - txt_n.get_width() // 2, y)); y += 26

        for linea in self._wrap(datos["descripcion"], self.fuente_popup, pw - 24):
            txt_d = self.fuente_popup.render(linea, True, (190, 190, 220))
            pantalla.blit(txt_d, (px + 12, y)); y += 18

        txt_c = self.fuente_popup_b.render(f"Coste: ${datos['coste_oro']:,} de oro", True, (255, 215, 0))
        pantalla.blit(txt_c, (px + 12, y)); y += 28

        bw, bh = 120, 34
        self._rect_popup_comprar  = pygame.Rect(px + 20, y, bw, bh)
        self._rect_popup_cancelar = pygame.Rect(px + pw - 140, y, bw, bh)

        col_c = (50, 160, 50) if self._rect_popup_comprar.collidepoint(mouse_pos) else (35, 100, 35)
        col_n = (160, 50, 50) if self._rect_popup_cancelar.collidepoint(mouse_pos) else (100, 35, 35)
        pygame.draw.rect(pantalla, col_c, self._rect_popup_comprar, border_radius=8)
        pygame.draw.rect(pantalla, col_n, self._rect_popup_cancelar, border_radius=8)

        lbl_c = self.fuente_popup_b.render("Comprar", True, (255, 255, 255))
        lbl_n = self.fuente_popup_b.render("Cancelar", True, (255, 255, 255))
        pantalla.blit(lbl_c, (self._rect_popup_comprar.centerx  - lbl_c.get_width() // 2,
                               self._rect_popup_comprar.centery  - lbl_c.get_height() // 2))
        pantalla.blit(lbl_n, (self._rect_popup_cancelar.centerx - lbl_n.get_width() // 2,
                               self._rect_popup_cancelar.centery - lbl_n.get_height() // 2))

    @staticmethod
    def _wrap(texto: str, fuente, max_w: int) -> list:
        palabras = texto.split()
        lineas, actual = [], ""
        for p in palabras:
            prueba = (actual + " " + p).strip()
            if fuente.size(prueba)[0] <= max_w:
                actual = prueba
            else:
                if actual:
                    lineas.append(actual)
                actual = p
        if actual:
            lineas.append(actual)
        return lineas

    # -- Eventos --------------------------------------------------------------
    def manejar_eventos(self, evento):
        """Devuelve 'INVESTIGACION' para volver, None en otro caso."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.popup_nodo:
                    self.popup_nodo = None
                else:
                    return 'INVESTIGACION'

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.rect_cerrar and self.rect_cerrar.collidepoint(pos):
                return 'INVESTIGACION'

            if self.popup_nodo:
                if self._rect_popup_comprar and self._rect_popup_comprar.collidepoint(pos):
                    ok, msg = self.gestor.comprar(self.popup_nodo, self.logica)
                    self.popup_msg = ("OK: " + msg) if ok else ("Error: " + msg)
                    self.popup_msg_frames = 90
                    self.popup_nodo = None
                elif self._rect_popup_cancelar and self._rect_popup_cancelar.collidepoint(pos):
                    self.popup_nodo = None
                return None

            for nid, rect in self._rects_nodos.items():
                if rect.collidepoint(pos):
                    if nid in self.gestor.comprados:
                        self.popup_msg = "Ya comprado"
                        self.popup_msg_frames = 60
                    else:
                        ok, motivo = self.gestor.puede_comprar(nid, self.logica.dinero)
                        if ok:
                            self.popup_nodo = nid
                        else:
                            self.popup_msg = motivo
                            self.popup_msg_frames = 90
                    break

        return None


# ══════════════════════════════════════════════════════════════════════════════
# GESTOR DE ÁRBOLES  —  rastrea niveles de todos los árboles de investigación
# ══════════════════════════════════════════════════════════════════════════════

class GestorArboles:
    """
    Gestiona el progreso (niveles) de todos los árboles tecnológicos.

    Estructura interna:
      niveles : dict { categoria_str -> { nodo_id -> nivel_actual (int) } }
    """

    def __init__(self, categorias: dict):
        self.categorias = categorias
        self.niveles: dict = {}

    # ── Consultas ─────────────────────────────────────────────────────────────
    def nivel(self, categoria: str, nid: str) -> int:
        return self.niveles.get(categoria, {}).get(nid, 0)

    def coste_siguiente(self, categoria: str, nid: str) -> int:
        arbol = self.categorias.get(categoria, {}).get("arbol", {})
        datos = arbol.get(nid, {})
        niv = self.nivel(categoria, nid)
        costes = datos.get("costes", [])
        if niv >= datos.get("max_nivel", len(costes)):
            return 0
        return costes[niv] if niv < len(costes) else (costes[-1] if costes else 0)

    @staticmethod
    def _efecto_en_nivel(datos: dict, niv: int) -> dict:
        """Retorna el efecto que se gana al subir al nivel (niv+1). Soporta schema nuevo y viejo."""
        if "efectos_por_nivel" in datos:
            lst = datos["efectos_por_nivel"]
            return lst[niv] if niv < len(lst) else {}
        # schema antiguo: efecto constante por nivel
        return datos.get("efecto_por_nivel", {})

    @staticmethod
    def _pob_req_en_nivel(datos: dict, niv: int) -> int:
        pobs = datos.get("pob_req_por_nivel", [])
        return pobs[niv] if niv < len(pobs) else 0

    def requisitos_niveles(self, categoria: str, nid: str) -> dict:
        arbol = self.categorias.get(categoria, {}).get("arbol", {})
        datos = arbol.get(nid, {})
        requisitos = dict(datos.get("requiere_niveles", {}))

        if datos.get("requiere_todos_nivel_prev", False):
            nivel_actual = self.nivel(categoria, nid)
            if nivel_actual >= 1:
                for otro_id in arbol:
                    if otro_id == nid:
                        continue
                    requisitos[otro_id] = max(requisitos.get(otro_id, 0), nivel_actual)

        return requisitos

    def cumple_requisitos_niveles(self, categoria: str, nid: str) -> bool:
        arbol = self.categorias.get(categoria, {}).get("arbol", {})
        for req_id, req_min in self.requisitos_niveles(categoria, nid).items():
            if req_id not in arbol:
                continue
            if self.nivel(categoria, req_id) < req_min:
                return False
        return True

    def puede_subir(self, categoria: str, nid: str, dinero: float, poblacion: int = 0):
        arbol = self.categorias.get(categoria, {}).get("arbol", {})
        datos = arbol.get(nid)
        if not datos:
            return False, "Nodo no encontrado"

        niv = self.nivel(categoria, nid)
        max_niv = datos.get("max_nivel", 5)
        if niv >= max_niv:
            return False, "Nivel máximo alcanzado"

        # Requisito de población
        pob_req = self._pob_req_en_nivel(datos, niv)
        if pob_req > 0 and poblacion < pob_req:
            return False, f"Necesitas {pob_req:,} habitantes (tienes {poblacion:,})"

        # Requisitos de nodos previos
        for req_id, req_min in self.requisitos_niveles(categoria, nid).items():
            if self.nivel(categoria, req_id) < req_min:
                req_nombre = arbol.get(req_id, {}).get("nombre", req_id)
                return False, f"Requiere '{req_nombre}' nivel {req_min}"

        coste = self.coste_siguiente(categoria, nid)
        if dinero < coste:
            return False, f"Oro insuficiente (faltan ${coste - dinero:,.0f})"

        return True, ""

    # ── Acción en dos pasos (pay → timer → apply) ─────────────────────────────
    def iniciar_subida(self, categoria: str, nid: str, logica) -> tuple:
        """Deduce el coste. El efecto se aplica luego con completar_subida()."""
        poblacion = len(getattr(logica, "poblacion", []))
        ok, msg = self.puede_subir(categoria, nid, logica.dinero, poblacion)
        if not ok:
            return False, msg
        coste = self.coste_siguiente(categoria, nid)
        logica.dinero -= coste
        return True, ""

    def completar_subida(self, categoria: str, nid: str, logica) -> tuple:
        """Aplica el efecto e incrementa el nivel. Llamar cuando expire el timer."""
        arbol = self.categorias[categoria]["arbol"]
        datos = arbol[nid]
        niv = self.nivel(categoria, nid)
        efecto = self._efecto_en_nivel(datos, niv)
        recalcular_limites = False
        for clave, valor in efecto.items():
            if clave == "desbloquea_edificio":
                if hasattr(logica, "edificios_desbloqueados") and valor not in logica.edificios_desbloqueados:
                    logica.edificios_desbloqueados.append(valor)
            elif clave == "bonus_capacidad_comida":
                logica.bonus_capacidad_comida_inv = getattr(logica, "bonus_capacidad_comida_inv", 0) + int(valor)
                recalcular_limites = True
            elif clave == "bonus_capacidad_agua":
                logica.bonus_capacidad_agua_inv = getattr(logica, "bonus_capacidad_agua_inv", 0) + int(valor)
                recalcular_limites = True
            elif clave == "bonus_capacidad_energia":
                logica.bonus_capacidad_energia_inv = getattr(logica, "bonus_capacidad_energia_inv", 0) + int(valor)
                recalcular_limites = True
            elif hasattr(logica, clave):
                setattr(logica, clave, getattr(logica, clave, 0.0) + valor)
        if hasattr(logica, "normalizar_modificadores_economia"):
            logica.normalizar_modificadores_economia()
        else:
            logica.bonus_ingreso_pct = max(0.0, min(3.0, getattr(logica, "bonus_ingreso_pct", 0.0)))
            logica.descuento_mantenimiento = max(0.0, min(0.90, getattr(logica, "descuento_mantenimiento", 0.0)))
            logica.descuento_edificios = max(0.0, min(0.90, getattr(logica, "descuento_edificios", 0.0)))
        if recalcular_limites and hasattr(logica, "aplicar_limites_dinamicos"):
            logica.aplicar_limites_dinamicos()
        self.niveles.setdefault(categoria, {})[nid] = niv + 1
        # Verificar avance de nivel de ciudad al subir nodos AVANCES
        if categoria == "AVANCES" and hasattr(logica, "nivel_tecnologico"):
            avances = self.niveles.get("AVANCES", {})
            nodos_avances = ["ava_comida", "ava_edificios", "ava_energia", "ava_agua"]
            if logica.nivel_tecnologico == 4:
                if all(avances.get(n, 0) >= 5 for n in nodos_avances):
                    logica.nivel_tecnologico = 5
                    if hasattr(logica, "noticias"):
                        logica.noticias.append({"txt": "¡Tu ciudad ha alcanzado el NIVEL 5! ¡Civilización Avanzada!", "tipo": "LOGRO"})
        # Registrar año para reinicio selectivo de capítulo
        if hasattr(logica, "arbol_subidas_ano"):
            key = f"{categoria}::{nid}"
            logica.arbol_subidas_ano.setdefault(key, []).append(logica.ano)
        return True, self._efecto_str_corto(efecto)

    @staticmethod
    def _efecto_str_corto(efecto: dict) -> str:
        partes = []
        for clave, valor in efecto.items():
            if clave == "bonus_ingreso_pct":
                partes.append(f"+{valor * 100:.0f}% ingresos")
            elif clave == "descuento_mantenimiento":
                partes.append(f"-{valor * 100:.0f}% mantenimiento")
            elif clave == "descuento_edificios":
                partes.append(f"-{valor * 100:.0f}% edificios")
            elif clave == "bonus_capacidad_comida":
                partes.append(f"+{int(valor):,} comida")
            elif clave == "bonus_capacidad_agua":
                partes.append(f"+{int(valor):,} agua")
            elif clave == "bonus_capacidad_energia":
                partes.append(f"+{int(valor):,} energía")
            elif clave == "reduccion_consumo_hab":
                partes.append(f"-{valor * 100:.0f}% consumo")
            elif clave == "reduccion_tiempo_investigacion":
                partes.append(f"-{valor * 100:.0f}% tiempo inv.")
            elif clave == "bonus_felicidad_global":
                partes.append(f"+{int(valor)} felicidad")
            elif clave == "bonus_ataque_global":
                partes.append(f"+{valor * 100:.0f}% ataque")
            elif clave == "bonus_defensa_global":
                partes.append(f"+{valor * 100:.0f}% defensa")
            elif clave == "desbloquea_unidad":
                partes.append(f"Desbloquea {valor}")
            elif clave == "desbloquea_edificio":
                partes.append(f"Nuevo edificio: {valor}")
            elif clave == "multiplicador_capacidad":
                partes.append(f"Capacidad x{valor:.1f}")
            else:
                partes.append(f"{clave}: {valor}")
        return "  ".join(partes) if partes else ""

    def subir_nivel(self, categoria: str, nid: str, logica):
        """Compat.: paga y aplica inmediatamente (sin timer)."""
        ok, msg = self.iniciar_subida(categoria, nid, logica)
        if not ok:
            return False, msg
        ok2, efecto_msg = self.completar_subida(categoria, nid, logica)
        nombre = self.categorias[categoria]["arbol"][nid].get("nombre", nid)
        return ok2, f"{nombre} → nivel {self.nivel(categoria, nid)}"

    # ── Persistencia ──────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {cat: dict(lvls) for cat, lvls in self.niveles.items()}

    def from_dict(self, data: dict):
        self.niveles = {
            cat: {k: int(v) for k, v in lvls.items()}
            for cat, lvls in data.items()
        }

    def recalcular_efectos(self, logica):
        """Re-aplica efectos acumulados desde los niveles guardados (útil al cargar partida)."""
        if hasattr(logica, "recalcular_bonos_investigacion_completas"):
            logica.recalcular_bonos_investigacion_completas()
        else:
            logica.bonus_ingreso_pct = 0.0
            logica.descuento_mantenimiento = 0.0
            logica.descuento_edificios = 0.0
            logica.reduccion_tiempo_investigacion = 0.0

        for cat, lvls in self.niveles.items():
            arbol = self.categorias.get(cat, {}).get("arbol", {})
            for nid, niv in lvls.items():
                datos = arbol.get(nid, {})
                if "efectos_por_nivel" in datos:
                    # Schema nuevo: cada nivel tiene su propio efecto (no constante)
                    for i in range(niv):
                        for clave, val in self._efecto_en_nivel(datos, i).items():
                            if clave == "desbloquea_edificio":
                                if hasattr(logica, "edificios_desbloqueados") and val not in logica.edificios_desbloqueados:
                                    logica.edificios_desbloqueados.append(val)
                            elif clave == "bonus_capacidad_comida":
                                logica.bonus_capacidad_comida_inv = getattr(logica, "bonus_capacidad_comida_inv", 0) + int(val)
                            elif clave == "bonus_capacidad_agua":
                                logica.bonus_capacidad_agua_inv = getattr(logica, "bonus_capacidad_agua_inv", 0) + int(val)
                            elif clave == "bonus_capacidad_energia":
                                logica.bonus_capacidad_energia_inv = getattr(logica, "bonus_capacidad_energia_inv", 0) + int(val)
                            elif hasattr(logica, clave):
                                setattr(logica, clave,
                                        getattr(logica, clave, 0.0) + val)
                else:
                    # Schema antiguo: efecto constante × niv
                    for clave, val in datos.get("efecto_por_nivel", {}).items():
                        if clave == "desbloquea_edificio":
                            if hasattr(logica, "edificios_desbloqueados") and val not in logica.edificios_desbloqueados:
                                logica.edificios_desbloqueados.append(val)
                        elif clave == "bonus_capacidad_comida":
                            logica.bonus_capacidad_comida_inv = getattr(logica, "bonus_capacidad_comida_inv", 0) + int(val * niv)
                        elif clave == "bonus_capacidad_agua":
                            logica.bonus_capacidad_agua_inv = getattr(logica, "bonus_capacidad_agua_inv", 0) + int(val * niv)
                        elif clave == "bonus_capacidad_energia":
                            logica.bonus_capacidad_energia_inv = getattr(logica, "bonus_capacidad_energia_inv", 0) + int(val * niv)
                        elif hasattr(logica, clave):
                            setattr(logica, clave,
                                    getattr(logica, clave, 0.0) + val * niv)

        if hasattr(logica, "normalizar_modificadores_economia"):
            logica.normalizar_modificadores_economia()
        else:
            logica.bonus_ingreso_pct = max(0.0, min(3.0, getattr(logica, "bonus_ingreso_pct", 0.0)))
            logica.descuento_mantenimiento = max(0.0, min(0.90, getattr(logica, "descuento_mantenimiento", 0.0)))
            logica.descuento_edificios = max(0.0, min(0.90, getattr(logica, "descuento_edificios", 0.0)))

        if hasattr(logica, "aplicar_limites_dinamicos"):
            logica.aplicar_limites_dinamicos()


# ══════════════════════════════════════════════════════════════════════════════
# ESCENA ÁRBOL TECNOLÓGICO  —  diseño Rise of Kingdoms (niveles acumulables)
# ══════════════════════════════════════════════════════════════════════════════

# Paleta
_COL_BG_PANEL = (8,  12, 30)
_COL_BD_PANEL = (50, 80, 180)
_COL_NODO_BG  = (16, 22, 46)
_COL_NODO_MAX = (20, 50, 22)
_COL_POPUP_BG = (12, 16, 38)

# Geometría (coords panel-relative)
_PANEL_W  = 980
_PANEL_H  = 620
_NODO_W   = 210
_NODO_H   = 105

_COL_X   = [55, 388, 720]          # x izquierdo de cada columna
_ROW_Y_3 = [130, 278, 426]        # y superior de cada fila en la columna triple
_ROW_Y_1 = 278                     # y para los nodos únicos (centrado = fila media)


class EscenaArbol:
    """
    Árbol tecnológico estilo Rise of Kingdoms.
    Diseño: 1 nodo izquierdo → 3 nodos centro → 1 nodo derecho.

    Flujo devuelto por manejar_eventos():
      'INVESTIGACION' → volver al menú de tarjetas
      None            → sin cambio
    """

    def __init__(self, categoria: str, gestor: "GestorArboles", logica):
        self.categoria  = categoria
        self.gestor     = gestor
        self.logica     = logica

        cat_data        = CATEGORIAS[categoria]
        self.arbol      = cat_data["arbol"]          # dict {nid -> datos}
        self.color_cat  = cat_data["color"]

        # Fuentes
        self.f_titulo   = pygame.font.SysFont("Arial", 36, bold=True)
        self.f_nodo_n   = pygame.font.SysFont("Arial", 15, bold=True)   # nombre nodo
        self.f_nodo_s   = pygame.font.SysFont("Arial", 12)              # subtexto nodo
        self.f_cerrar   = pygame.font.SysFont("Arial", 18, bold=True)
        self.f_popup    = pygame.font.SysFont("Arial", 13)
        self.f_popup_b  = pygame.font.SysFont("Arial", 14, bold=True)
        self.f_popup_sec= pygame.font.SysFont("Arial", 12, bold=True)
        self.f_hint     = pygame.font.SysFont("Arial", 11)
        self.f_centro   = pygame.font.SysFont("Arial", 22, bold=True)

        # Estado de UI
        self.rect_cerrar          = None
        self._rects_nodos: dict   = {}
        self.popup_nodo: str      = None
        self._rect_popup_subir    = None
        self._rect_popup_cancelar = None
        self.popup_msg: str       = ""
        self.popup_msg_frames: int = 0

        # Timer de mejora en curso
        self._timer_nid: str   = None
        self._timer_frames: int = 0
        self._TIMER_TOTAL       = 300   # 5 segundos a ~60 fps

    # ── Helpers de geometría ──────────────────────────────────────────────────
    def _panel_rect(self, ancho, alto):
        px = ancho // 2 - _PANEL_W // 2
        py = alto  // 2 - _PANEL_H // 2
        return pygame.Rect(px, py, _PANEL_W, _PANEL_H)

    def _nodo_rect(self, panel, nid: str) -> pygame.Rect:
        if self.categoria == "AVANCES":
            centro = self._centro_info_rect(panel)
            dx = 315
            dy = 150
            mapa = {
                "ava_comida": (-dx, 0),
                "ava_agua": (dx, 0),
                "ava_edificios": (0, -dy),
                "ava_energia": (0, dy),
            }
            ox, oy = mapa.get(nid, (0, 0))
            return pygame.Rect(centro.centerx + ox - _NODO_W // 2,
                               centro.centery + oy - _NODO_H // 2,
                               _NODO_W, _NODO_H)

        datos = self.arbol[nid]
        col   = datos.get("fila_col", 0)
        row   = datos.get("fila_row", 0)
        x     = panel.x + _COL_X[col]
        y     = panel.y + (_ROW_Y_3[row] if col == 1 else _ROW_Y_1)
        return pygame.Rect(x, y, _NODO_W, _NODO_H)

    def _centro_info_rect(self, panel) -> pygame.Rect:
        w = 210
        h = 105
        x = panel.centerx - w // 2
        y = panel.centery - h // 2 + 4
        return pygame.Rect(x, y, w, h)

    def _dibujar_centro_info(self, pantalla, panel, rect=None):
        if self.categoria != "AVANCES":
            return None

        rect = rect if rect is not None else self._centro_info_rect(panel)
        pygame.draw.rect(pantalla, (28, 34, 70), rect, border_radius=12)
        pygame.draw.rect(pantalla, (255, 215, 0), rect, 3, border_radius=12)

        rango = getattr(self.logica, "rango_actual", "Aldea")
        mapa_nivel = {
            "Aldea": 1,
            "Pueblo": 2,
            "Ciudad": 3,
            "Metrópolis": 4,
            "Megalópolis": 5,
        }
        nivel_ciudad = mapa_nivel.get(rango, 1)

        txt_centro = self.f_centro.render(f"CIUDAD NIVEL: {nivel_ciudad}", True, (255, 255, 255))
        pantalla.blit(txt_centro, (rect.centerx - txt_centro.get_width() // 2, rect.centery - txt_centro.get_height() // 2))
        return rect

    def _req_ok(self, nid: str) -> bool:
        """True si todos los requisitos del nodo están satisfechos."""
        return self.gestor.cumple_requisitos_niveles(self.categoria, nid)

    # ── Dibujo principal ─────────────────────────────────────────────────────
    def dibujar(self, pantalla):
        ancho, alto = pantalla.get_size()
        panel       = self._panel_rect(ancho, alto)
        mouse_pos   = pygame.mouse.get_pos()

        # ── Tick del timer de mejora ──────────────────────────────────────────
        if self._timer_frames > 0:
            self._timer_frames -= 1
            if self._timer_frames == 0 and self._timer_nid:
                ok, efecto_msg = self.gestor.completar_subida(
                    self.categoria, self._timer_nid, self.logica)
                if ok and efecto_msg:
                    self.popup_msg        = f"¡Mejora aplicada!  {efecto_msg}"
                    self.popup_msg_frames = 180
                self._timer_nid = None

        # Overlay oscuro sobre la ciudad
        ov = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        pantalla.blit(ov, (0, 0))

        # Panel fondo + borde
        pygame.draw.rect(pantalla, _COL_BG_PANEL, panel, border_radius=14)
        pygame.draw.rect(pantalla, self.color_cat,  panel, 3, border_radius=14)

        # ── Barra de título ──────────────────────────────────────────────────
        barra = pygame.Rect(panel.x + 3, panel.y + 3, _PANEL_W - 6, 66)
        pygame.draw.rect(pantalla, (12, 16, 45), barra, border_radius=12)

        txt_t = self.f_titulo.render(self.categoria, True, self.color_cat)
        pantalla.blit(txt_t, (panel.centerx - txt_t.get_width() // 2,
                              panel.y + 14))

        txt_oro = self.f_popup_b.render(
            f"Oro disponible: ${self.logica.dinero:,.0f}", True, (255, 215, 0))
        pantalla.blit(txt_oro, (panel.right - txt_oro.get_width() - 60,
                                panel.y + 22))

        sep_y = panel.y + 70
        pygame.draw.line(pantalla, self.color_cat,
                         (panel.x + 3, sep_y), (panel.right - 3, sep_y), 1)

        # ── Botón cerrar X ───────────────────────────────────────────────────
        self.rect_cerrar = pygame.Rect(panel.right - 46, panel.y + 8, 38, 38)
        col_x = (220, 40, 40) if self.rect_cerrar.collidepoint(mouse_pos) \
                              else (150, 30, 30)
        pygame.draw.rect(pantalla, col_x, self.rect_cerrar, border_radius=8)
        tx = self.f_cerrar.render("X", True, (255, 255, 255))
        pantalla.blit(tx, (self.rect_cerrar.centerx - tx.get_width()  // 2,
                           self.rect_cerrar.centery - tx.get_height() // 2))

        # ── Líneas conectoras ─────────────────────────────────────────────────
        rect_centro_info = self._centro_info_rect(panel) if self.categoria == "AVANCES" else None
        self._dibujar_lineas(pantalla, panel, rect_centro_info)

        # ── Nodos ─────────────────────────────────────────────────────────────
        self._rects_nodos.clear()
        for nid in self.arbol:
            rect = self._nodo_rect(panel, nid)
            self._rects_nodos[nid] = rect
            self._dibujar_nodo(pantalla, nid, rect, mouse_pos)

        if rect_centro_info is not None:
            self._dibujar_centro_info(pantalla, panel, rect_centro_info)

        # ── Popup de confirmación ─────────────────────────────────────────────
        if self.popup_nodo:
            self._dibujar_popup(pantalla, panel, mouse_pos)

        # ── Mensaje flotante ─────────────────────────────────────────────────
        if self.popup_msg_frames > 0:
            alpha  = min(255, self.popup_msg_frames * 6)
            ms     = self.f_popup_b.render(self.popup_msg, True, (255, 215, 0))
            ms.set_alpha(alpha)
            pantalla.blit(ms, (panel.centerx - ms.get_width() // 2,
                               panel.bottom - 40))
            self.popup_msg_frames -= 1

        # ── Hint inferior ─────────────────────────────────────────────────────
        hint = self.f_hint.render(
            "Clic en un cuadro para subir nivel  |  [ESC] Volver",
            True, (60, 70, 110))
        pantalla.blit(hint, (panel.x + 16, panel.bottom - 22))

    # ── Líneas conectoras entre nodos ────────────────────────────────────────
    def _dibujar_lineas(self, pantalla, panel, rect_centro_info=None):
        if self.categoria == "AVANCES" and rect_centro_info is not None:
            for nid in self.arbol:
                r_hijo = self._nodo_rect(panel, nid)
                if r_hijo.centerx < rect_centro_info.centerx:
                    p1 = (rect_centro_info.left, rect_centro_info.centery)
                    p2 = (r_hijo.right, r_hijo.centery)
                elif r_hijo.centerx > rect_centro_info.centerx:
                    p1 = (rect_centro_info.right, rect_centro_info.centery)
                    p2 = (r_hijo.left, r_hijo.centery)
                elif r_hijo.centery < rect_centro_info.centery:
                    p1 = (rect_centro_info.centerx, rect_centro_info.top)
                    p2 = (r_hijo.centerx, r_hijo.bottom)
                else:
                    p1 = (rect_centro_info.centerx, rect_centro_info.bottom)
                    p2 = (r_hijo.centerx, r_hijo.top)

                col_l = self.color_cat
                lw = 3

                if abs(p1[0] - p2[0]) < 4 or abs(p1[1] - p2[1]) < 4:
                    pygame.draw.line(pantalla, col_l, p1, p2, lw)
                else:
                    mid_x = (p1[0] + p2[0]) // 2
                    pygame.draw.lines(pantalla, col_l, False,
                                      [p1, (mid_x, p1[1]), (mid_x, p2[1]), p2], lw)

        for nid, datos in self.arbol.items():
            r_hijo = self._nodo_rect(panel, nid)
            for req_id, req_min in datos.get("requiere_niveles", {}).items():
                if req_id not in self.arbol:
                    continue
                r_padre = self._nodo_rect(panel, req_id)

                p1 = (r_padre.right,  r_padre.centery)
                p2 = (r_hijo.left,    r_hijo.centery)

                cumplido = self.gestor.nivel(self.categoria, req_id) >= req_min
                col_l = self.color_cat if cumplido else (40, 55, 110)
                lw    = 3 if cumplido else 2

                if abs(p1[1] - p2[1]) < 4:
                    # Línea recta horizontal
                    pygame.draw.line(pantalla, col_l, p1, p2, lw)
                else:
                    # Codo en L: derecha → vertical → derecha
                    mid_x = (p1[0] + p2[0]) // 2
                    pygame.draw.lines(pantalla, col_l, False,
                                      [p1, (mid_x, p1[1]),
                                       (mid_x, p2[1]), p2], lw)

    # ── Dibujo de un nodo individual ─────────────────────────────────────────
    def _dibujar_nodo(self, pantalla, nid, rect, mouse_pos):
        datos      = self.arbol[nid]
        cat        = self.categoria
        niv_actual = self.gestor.nivel(cat, nid)
        max_niv    = datos.get("max_nivel", 5)
        es_max     = niv_actual >= max_niv
        ic_color   = datos.get("icono_color", (100, 110, 200))
        en_progreso = (nid == self._timer_nid)

        # Comprobar si se puede comprar (con población)
        poblacion   = len(getattr(self.logica, "poblacion", []))
        ok_subir, _ = self.gestor.puede_subir(cat, nid, self.logica.dinero, poblacion)
        req_cadena  = self._req_ok(nid)             # requisito de nodos previos
        hover       = rect.collidepoint(mouse_pos) and not self.popup_nodo

        # ── Colores de fondo y borde ──────────────────────────────────────────
        if en_progreso:
            bg, borde = (10, 30, 50), (255, 200, 0)
        elif es_max:
            bg, borde = _COL_NODO_MAX, (60, 200, 60)
        elif ok_subir:
            bg    = (22, 32, 65) if hover else _COL_NODO_BG
            borde = self.color_cat if hover else (55, 85, 160)
        elif req_cadena:
            # Puede ver, no puede comprar (oro o población)
            bg, borde = (18, 24, 48), (40, 60, 130)
        else:
            # Nodo bloqueado por cadena (nodos previos no listos) — visible pero dim
            bg, borde = (14, 18, 36), (30, 40, 80)

        pygame.draw.rect(pantalla, bg,    rect, border_radius=10)
        pygame.draw.rect(pantalla, borde, rect, 2, border_radius=10)

        # ── Acento de color: línea vertical izquierda ──────────────────────────
        acento = pygame.Rect(rect.x + 2, rect.y + 6, 4, rect.height - 12)
        pygame.draw.rect(pantalla, ic_color if req_cadena else (40, 50, 80),
                         acento, border_radius=2)

        # ── Nombre del nodo ───────────────────────────────────────────────────
        col_n = (240, 250, 255) if req_cadena else (120, 130, 155)
        if en_progreso:
            col_n = (255, 220, 60)
        txt_n = self.f_nodo_n.render(datos["nombre"], True, col_n)
        pantalla.blit(txt_n, (rect.x + 14, rect.y + 8))

        # ── Etiqueta nivel ────────────────────────────────────────────────────
        if es_max:
            lbl_niv = self.f_nodo_s.render("MAX", True, (80, 220, 80))
        elif en_progreso:
            lbl_niv = self.f_nodo_s.render("EN CURSO...", True, (255, 200, 0))
        else:
            lbl_niv = self.f_nodo_s.render(f"Niv. {niv_actual}/{max_niv}", True,
                                            (160, 180, 220))
        pantalla.blit(lbl_niv, (rect.right - lbl_niv.get_width() - 8, rect.y + 10))

        # ── Barra de progreso de nivel ────────────────────────────────────────
        bar_x = rect.x + 14
        bar_y = rect.y + 54
        bar_w = rect.width - 28
        bar_h = 10
        pygame.draw.rect(pantalla, (18, 22, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        if max_niv > 0 and niv_actual > 0:
            fill_w   = int(bar_w * niv_actual / max_niv)
            col_fill = (60, 200, 60) if es_max else ic_color
            pygame.draw.rect(pantalla, col_fill,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(pantalla, (40, 55, 100), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        # ── Barra de timer (si está en progreso) ──────────────────────────────
        if en_progreso and self._timer_frames > 0:
            ty = bar_y + 13
            pygame.draw.rect(pantalla, (30, 20, 0), (bar_x, ty, bar_w, 8), border_radius=4)
            ratio     = self._timer_frames / self._TIMER_TOTAL
            fill_t    = int(bar_w * ratio)
            pygame.draw.rect(pantalla, (255, 180, 0), (bar_x, ty, fill_t, 8), border_radius=4)
            pygame.draw.rect(pantalla, (180, 120, 0), (bar_x, ty, bar_w, 8), 1, border_radius=4)

        # ── Coste / estado inferior ───────────────────────────────────────────
        if es_max:
            txt_st = self.f_nodo_s.render("MÁXIMO", True, (80, 220, 80))
            pantalla.blit(txt_st, (rect.centerx - txt_st.get_width() // 2, rect.bottom - 18))
        elif en_progreso:
            pass  # La barra ya ocupa ese espacio
        else:
            coste   = self.gestor.coste_siguiente(cat, nid)
            col_c   = (255, 215, 0) if ok_subir else (100, 90, 60)
            txt_c   = self.f_nodo_s.render(f"${coste:,}", True, col_c)
            pantalla.blit(txt_c, (rect.centerx - txt_c.get_width() // 2, rect.bottom - 17))

    # ── Popup de confirmación de subida de nivel ─────────────────────────────
    def _dibujar_popup(self, pantalla, panel, mouse_pos):
        nid = self.popup_nodo
        if nid not in self.arbol:
            self.popup_nodo = None
            return

        datos      = self.arbol[nid]
        cat        = self.categoria
        niv_actual = self.gestor.nivel(cat, nid)
        max_niv    = datos.get("max_nivel", 5)
        coste      = self.gestor.coste_siguiente(cat, nid)
        ic_color   = datos.get("icono_color", (100, 110, 200))
        poblacion  = len(getattr(self.logica, "poblacion", []))

        ok_subir, motivo_no = self.gestor.puede_subir(
            cat, nid, self.logica.dinero, poblacion)
        es_max = niv_actual >= max_niv

        pw, ph = 440, 370
        px     = panel.centerx - pw // 2
        py     = panel.centery - ph // 2

        ORO   = (255, 215,   0)

        # Fondo y borde dorado estilo tienda
        pygame.draw.rect(pantalla, _COL_POPUP_BG, (px, py, pw, ph), border_radius=14)
        pygame.draw.rect(pantalla, ORO,           (px, py, pw, ph), 3, border_radius=14)

        # ── Cabecera con banda de color ───────────────────────────────────────
        barra_top = pygame.Rect(px + 3, py + 3, pw - 6, 48)
        pygame.draw.rect(pantalla, ic_color, barra_top, border_radius=10)
        txt_n = self.f_popup_b.render(datos["nombre"].upper(), True, (10, 10, 20))
        pantalla.blit(txt_n, (px + pw // 2 - txt_n.get_width() // 2, py + 13))
        if not es_max:
            lv_str = self.f_popup.render(
                f"Nivel  {niv_actual}  →  {niv_actual + 1}  /  {max_niv}",
                True, (30, 30, 50))
            pantalla.blit(lv_str, (px + pw // 2 - lv_str.get_width() // 2, py + 34))

        sep_y = py + 58
        pygame.draw.line(pantalla, (35, 45, 90), (px + 14, sep_y), (px + pw - 14, sep_y), 1)
        y = sep_y + 10

        # ── REQUISITOS ────────────────────────────────────────────────────────
        pantalla.blit(self.f_popup_sec.render("REQUISITOS", True, (215, 175, 50)), (px + 14, y))
        y += 22

        pob_reqs = datos.get("pob_req_por_nivel", [])
        sin_reqs = True
        if pob_reqs and niv_actual < len(pob_reqs):
            sin_reqs   = False
            pob_req_niv = pob_reqs[niv_actual]
            cumple_pob  = poblacion >= pob_req_niv
            col_r = (80, 215, 80) if cumple_pob else (220, 70, 70)
            sim   = "✓" if cumple_pob else "✗"
            lbl = self.f_popup.render(
                f"  {sim}  {pob_req_niv:,} habitantes  (tienes {poblacion:,})", True, col_r)
            pantalla.blit(lbl, (px + 14, y)); y += 18

        for req_id, req_min in self.gestor.requisitos_niveles(cat, nid).items():
            sin_reqs = False
            req_nombre  = self.arbol.get(req_id, {}).get("nombre", req_id)
            req_niv_act = self.gestor.nivel(cat, req_id)
            cumple      = req_niv_act >= req_min
            col_r = (80, 215, 80) if cumple else (220, 70, 70)
            sim   = "✓" if cumple else "✗"
            lbl = self.f_popup.render(
                f"  {sim}  {req_nombre}  nivel {req_min}  ({req_niv_act}/{req_min})", True, col_r)
            pantalla.blit(lbl, (px + 14, y)); y += 18

        if sin_reqs:
            pantalla.blit(self.f_popup.render("  Sin requisitos previos", True, (120, 130, 155)),
                          (px + 14, y)); y += 18

        y += 4
        pygame.draw.line(pantalla, (35, 45, 90), (px + 14, y), (px + pw - 14, y), 1)
        y += 10

        # ── BENEFICIOS ────────────────────────────────────────────────────────
        pantalla.blit(self.f_popup_sec.render("BENEFICIOS (este nivel)", True, (80, 215, 120)),
                      (px + 14, y)); y += 22

        _NOMBRES_EFECTO = {
            "bonus_ingreso_pct":       "+{v:.0f}%  en ingresos fiscales",
            "descuento_mantenimiento": "-{v:.0f}%  en costes de mantenimiento",
            "descuento_edificios":     "-{v:.0f}%  en precio de edificios",
            "bonus_capacidad_comida":  "+{v:.0f} capacidad de comida",
            "bonus_capacidad_agua":    "+{v:.0f} capacidad de agua",
            "bonus_capacidad_energia": "+{v:.0f} capacidad de energía",
            "bonus_felicidad_global":  "+{v:.0f} felicidad global",
            "reduccion_tiempo_investigacion": "-{v:.0f}% tiempo de investigación",
            "desbloquea_edificio":     "Desbloquea edificio: {v}",
        }
        efecto = GestorArboles._efecto_en_nivel(datos, niv_actual) if not es_max else {}
        if efecto:
            for clave, valor in efecto.items():
                if clave in {"bonus_ingreso_pct", "descuento_mantenimiento", "descuento_edificios", "reduccion_tiempo_investigacion", "reduccion_consumo_hab", "bonus_ataque_global", "bonus_defensa_global"}:
                    v_fmt = valor * 100
                else:
                    v_fmt = valor
                texto = "  ▸  " + _NOMBRES_EFECTO.get(clave, "{v}").format(v=v_fmt)
                pantalla.blit(self.f_popup.render(texto, True, (100, 230, 255)), (px + 14, y))
                y += 18
        else:
            pantalla.blit(self.f_popup.render("  —", True, (100, 110, 130)), (px + 14, y))
            y += 18

        y += 4
        pygame.draw.line(pantalla, (35, 45, 90), (px + 14, y), (px + pw - 14, y), 1)
        y += 10

        # ── COSTE ─────────────────────────────────────────────────────────────
        if not es_max:
            pantalla.blit(self.f_popup_sec.render("COSTE", True, (215, 175, 50)), (px + 14, y))
            col_c = ORO if ok_subir else (120, 110, 60)
            txt_c = self.f_popup_b.render(f"${coste:,}", True, col_c)
            pantalla.blit(txt_c, (px + pw - txt_c.get_width() - 14, y))
            y += 26
            if not ok_subir and motivo_no:
                warn = self.f_popup.render(f"⚠  {motivo_no}", True, (240, 100, 80))
                pantalla.blit(warn, (px + pw // 2 - warn.get_width() // 2, y))
        else:
            lbl = self.f_popup_b.render("✓  NIVEL MÁXIMO ALCANZADO", True, (80, 220, 80))
            pantalla.blit(lbl, (px + pw // 2 - lbl.get_width() // 2, y))

        # ── Botones estilo tienda ─────────────────────────────────────────────
        bw, bh = 160, 42
        y_btn  = py + ph - bh - 14

        self._rect_popup_cancelar = pygame.Rect(px + pw - bw - 14, y_btn, bw, bh)
        col_no = (200, 45, 45) if self._rect_popup_cancelar.collidepoint(mouse_pos) \
                               else (140, 28, 28)
        pygame.draw.rect(pantalla, col_no, self._rect_popup_cancelar, border_radius=10)
        pygame.draw.rect(pantalla, ORO,    self._rect_popup_cancelar, 2, border_radius=10)
        lbl_no = self.f_popup_b.render("CANCELAR", True, (255, 255, 255))
        pantalla.blit(lbl_no, (self._rect_popup_cancelar.centerx - lbl_no.get_width() // 2,
                                self._rect_popup_cancelar.centery - lbl_no.get_height() // 2))

        if ok_subir and not es_max:
            self._rect_popup_subir = pygame.Rect(px + 14, y_btn, bw, bh)
            col_ok = (55, 200, 55) if self._rect_popup_subir.collidepoint(mouse_pos) \
                                   else (34, 139, 34)
            pygame.draw.rect(pantalla, col_ok, self._rect_popup_subir, border_radius=10)
            pygame.draw.rect(pantalla, ORO,    self._rect_popup_subir, 2, border_radius=10)
            lbl_ok = self.f_popup_b.render("MEJORAR", True, (255, 255, 255))
            pantalla.blit(lbl_ok, (self._rect_popup_subir.centerx - lbl_ok.get_width() // 2,
                                    self._rect_popup_subir.centery - lbl_ok.get_height() // 2))
        else:
            self._rect_popup_subir = None

    @staticmethod
    def _efecto_str_legacy(efecto: dict) -> str:
        """Kept for compatibility with other categories using old schema."""
        partes = []
        nombres = {
            "bonus_ingreso_pct":       "+{v:.0f}% ingresos",
            "descuento_mantenimiento": "-{v:.0f}% mant.",
            "descuento_edificios":     "-{v:.0f}% edificios",
        }
        for clave, valor in efecto.items():
            fmt = nombres.get(clave, "+{v}")
            partes.append(fmt.format(v=valor * 100))
        return "  ".join(partes) if partes else "—"

    # ── Manejo de eventos ─────────────────────────────────────────────────────
    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.popup_nodo:
                    self.popup_nodo = None
                else:
                    return 'INVESTIGACION'

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.rect_cerrar and self.rect_cerrar.collidepoint(pos):
                return 'INVESTIGACION'

            if self.popup_nodo:
                if self._rect_popup_subir and self._rect_popup_subir.collidepoint(pos):
                    # Iniciar subida (paga coste, arranca timer)
                    nid_comprar = self.popup_nodo
                    ok, msg = self.gestor.iniciar_subida(
                        self.categoria, nid_comprar, self.logica)
                    if ok:
                        self._timer_nid    = nid_comprar
                        self._timer_frames = self._TIMER_TOTAL
                        self.popup_msg        = "¡Mejora en progreso..."
                        self.popup_msg_frames = 80
                    else:
                        self.popup_msg        = msg
                        self.popup_msg_frames = 120
                    self.popup_nodo = None
                elif self._rect_popup_cancelar and \
                        self._rect_popup_cancelar.collidepoint(pos):
                    self.popup_nodo = None
                return None

            # Clic en nodo: abrir popup siempre (aunque esté bloqueado)
            for nid, rect in self._rects_nodos.items():
                if rect.collidepoint(pos):
                    if nid != self._timer_nid:   # no abrir popup del que está en progreso
                        self.popup_nodo = nid
                    break

        return None
