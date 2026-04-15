# -*- coding: utf-8 -*-
# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.
# Módulo: Componentes de Interfaz Reutilizables

"""
Componentes:
  BotonCircular  — botón redondo con animación de pulso al hacer hover
  Slider         — control deslizante para volumen / cualquier float 0‒1
  Tooltip        — etiqueta flotante auto-ocultante
  crear_botones_hud() — genera la barra de 6 botones inferior lista para usar
"""

import pygame
import math
import os

BASE_DIR = os.path.dirname(__file__)


# ══════════════════════════════════════════════════════════════════════════════
# BOTÓN CIRCULAR CON PULSO
# ══════════════════════════════════════════════════════════════════════════════
class BotonCircular:
    """
    Botón redondo con:
      - imagen de icono centrada
      - etiqueta de texto debajo
      - animación de pulso (radio oscila) al hacer hover
      - colores: fondo / borde normal / borde hover
    """

    def __init__(
        self,
        cx: int, cy: int,
        radio: int = 30,
        imagen: pygame.Surface = None,
        etiqueta: str = "",
        color_fondo: tuple = (50, 50, 70),
        color_borde: tuple = (90, 110, 200),
        color_borde_hover: tuple = (255, 215, 0),
        color_etiqueta: tuple = (200, 200, 255),
        tag: str = "",
    ):
        self.cx = cx
        self.cy = cy
        self.radio = radio
        self.imagen = imagen
        self.etiqueta = etiqueta
        self.color_fondo = color_fondo
        self.color_borde = color_borde
        self.color_borde_hover = color_borde_hover
        self.color_etiqueta = color_etiqueta
        self.tag = tag          # identificador lógico ("investigar", "ataque", …)

        self._fuente = pygame.font.SysFont("Arial", 11, bold=True)
        self._tick = 0.0        # para animación de pulso

    @property
    def rect(self) -> pygame.Rect:
        """Rect cuadrado que envuelve el círculo (útil para colisiones)."""
        r = self.radio + 4
        return pygame.Rect(self.cx - r, self.cy - r, r * 2, r * 2)

    def contiene(self, pos: tuple) -> bool:
        dx = pos[0] - self.cx
        dy = pos[1] - self.cy
        return (dx * dx + dy * dy) <= (self.radio + 4) ** 2

    def dibujar(self, pantalla: pygame.Surface, dt: float = 1 / 60):
        """Dibuja el botón. Llama cada frame con dt (segundos por frame)."""
        self._tick += dt * 4.0     # velocidad del pulso
        pos_mouse = pygame.mouse.get_pos()
        hover = self.contiene(pos_mouse)

        # Radio animado
        if hover:
            extra = int(math.sin(self._tick) * 2.5)
            r_draw = self.radio + extra
            color_b = self.color_borde_hover
        else:
            r_draw = self.radio
            color_b = self.color_borde

        # Sombra suave
        sombra = pygame.Surface((r_draw * 2 + 8, r_draw * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(sombra, (0, 0, 0, 80), (r_draw + 4, r_draw + 4), r_draw + 2)
        pantalla.blit(sombra, (self.cx - r_draw - 4, self.cy - r_draw - 4))

        # Fondo
        pygame.draw.circle(pantalla, self.color_fondo, (self.cx, self.cy), r_draw)
        # Borde
        pygame.draw.circle(pantalla, color_b, (self.cx, self.cy), r_draw, 2)

        # Icono centrado
        if self.imagen:
            iw = self.imagen.get_width()
            ih = self.imagen.get_height()
            pantalla.blit(self.imagen, (self.cx - iw // 2, self.cy - ih // 2))

        # Etiqueta debajo
        if self.etiqueta:
            txt = self._fuente.render(self.etiqueta, True, self.color_etiqueta)
            pantalla.blit(txt, (self.cx - txt.get_width() // 2, self.cy + r_draw + 4))


# ══════════════════════════════════════════════════════════════════════════════
# SLIDER INDEPENDIENTE
# ══════════════════════════════════════════════════════════════════════════════
class Slider:
    """
    Control deslizante horizontal.
      valor (float 0‒1) se lee con .valor
      Llama a callback(valor) al cambiar.
    """

    ANCHO_PISTA = 180
    ALTO_PISTA  = 6
    RADIO_PULGAR = 9

    def __init__(
        self,
        x: int, y: int,
        valor_inicial: float = 0.5,
        etiqueta: str = "",
        color_pista: tuple = (80, 80, 100),
        color_relleno: tuple = (90, 110, 200),
        color_pulgar: tuple = (255, 255, 255),
        callback=None,
    ):
        self.x = x
        self.y = y
        self.valor = max(0.0, min(1.0, valor_inicial))
        self.etiqueta = etiqueta
        self.color_pista = color_pista
        self.color_relleno = color_relleno
        self.color_pulgar = color_pulgar
        self.callback = callback
        self._arrastrando = False
        self._fuente = pygame.font.SysFont("Arial", 12)

    @property
    def rect_pista(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y - self.ALTO_PISTA // 2, self.ANCHO_PISTA, self.ALTO_PISTA)

    def _cx_pulgar(self) -> int:
        return self.x + int(self.valor * self.ANCHO_PISTA)

    def manejar_evento(self, evento: pygame.event.Event):
        """Devuelve True si consumió el evento."""
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            px, py = evento.pos
            cx = self._cx_pulgar()
            if abs(px - cx) <= self.RADIO_PULGAR + 4 and abs(py - self.y) <= self.RADIO_PULGAR + 4:
                self._arrastrando = True
                return True
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self._arrastrando:
                self._arrastrando = False
                return True
        elif evento.type == pygame.MOUSEMOTION and self._arrastrando:
            nx = max(self.x, min(self.x + self.ANCHO_PISTA, evento.pos[0]))
            self.valor = (nx - self.x) / self.ANCHO_PISTA
            if self.callback:
                self.callback(self.valor)
            return True
        return False

    def dibujar(self, pantalla: pygame.Surface):
        # Pista completa (fondo)
        pygame.draw.rect(pantalla, self.color_pista, self.rect_pista, border_radius=3)
        # Pista rellena (izquierda del pulgar)
        ancho_relleno = int(self.valor * self.ANCHO_PISTA)
        if ancho_relleno > 0:
            pygame.draw.rect(
                pantalla, self.color_relleno,
                pygame.Rect(self.x, self.y - self.ALTO_PISTA // 2, ancho_relleno, self.ALTO_PISTA),
                border_radius=3,
            )
        # Pulgar
        cx = self._cx_pulgar()
        pygame.draw.circle(pantalla, self.color_pulgar, (cx, self.y), self.RADIO_PULGAR)
        pygame.draw.circle(pantalla, self.color_relleno, (cx, self.y), self.RADIO_PULGAR, 2)
        # Etiqueta y porcentaje
        if self.etiqueta:
            txt = self._fuente.render(f"{self.etiqueta}: {int(self.valor * 100)}%", True, (200, 200, 200))
            pantalla.blit(txt, (self.x, self.y - 20))


# ══════════════════════════════════════════════════════════════════════════════
# TOOLTIP FLOTANTE AUTO-OCULTANTE
# ══════════════════════════════════════════════════════════════════════════════
class Tooltip:
    """
    Muestra un texto flotante cerca del ratón durante 'duracion' frames.
    Uso:
        tooltip = Tooltip()
        tooltip.mostrar("Texto de ayuda", duracion=120)
        # en el game loop:
        tooltip.dibujar(pantalla)
    """

    _PADDING = 8

    def __init__(self):
        self._texto = ""
        self._frames = 0
        self._fuente = pygame.font.SysFont("Arial", 13)

    def mostrar(self, texto: str, duracion: int = 120):
        self._texto = texto
        self._frames = duracion

    def dibujar(self, pantalla: pygame.Surface):
        if self._frames <= 0 or not self._texto:
            return

        alpha = min(255, self._frames * 4)
        pos = pygame.mouse.get_pos()

        surf = self._fuente.render(self._texto, True, (240, 240, 240))
        w = surf.get_width() + self._PADDING * 2
        h = surf.get_height() + self._PADDING * 2

        # Ajustar para que no salga de pantalla
        px = min(pos[0] + 14, pantalla.get_width() - w - 4)
        py = max(4, pos[1] - h - 6)

        fondo = pygame.Surface((w, h), pygame.SRCALPHA)
        fondo.fill((20, 20, 35, 210))
        pygame.draw.rect(fondo, (90, 110, 200, 200), (0, 0, w, h), 1, border_radius=5)
        fondo.set_alpha(alpha)
        pantalla.blit(fondo, (px, py))

        txt_s = self._fuente.render(self._texto, True, (240, 240, 240))
        txt_s.set_alpha(alpha)
        pantalla.blit(txt_s, (px + self._PADDING, py + self._PADDING))

        self._frames -= 1


# ══════════════════════════════════════════════════════════════════════════════
# FÁBRICA DE BOTONES HUD
# ══════════════════════════════════════════════════════════════════════════════
def crear_botones_hud(ancho_pantalla: int, alto_pantalla: int, iconos: dict) -> list:
    """
    Genera la lista de 6 BotonCircular para la barra inferior.
    Se reposiciona automáticamente llamando a esta función cuando cambia la resolución.

    Botones (de derecha a izquierda):
      0 - noticias      (azul)
      1 - inventario    (dorado)
      2 - ajustes       (gris)
      3 - investigacion (cian)
      4 - misiones      (verde)
      5 - ataque        (rojo)   ← NUEVO

    Retorna lista[BotonCircular]. El campo .tag identifica a cada botón.
    """
    cy = alto_pantalla - 50
    separacion = 80
    x_base = ancho_pantalla - 70       # más a la derecha

    configuracion = [
        # (offset_x desde x_base, tag, etiqueta, color_fondo, color_borde, color_hover)
        (0,             "noticias",     "Noticias",  (40, 40, 60), (90, 110, 200), (100, 140, 255)),
        (-separacion,   "inventario",   "Inventario",(40, 40, 60), (200, 170, 30), (255, 215, 0)),
        (-separacion*2, "ajustes",      "Ajustes",   (40, 40, 60), (120, 120, 120),(200, 200, 200)),
        (-separacion*3, "investigar",   "Lab.",      (30, 40, 60), (0,  200, 220), (0,  255, 255)),
        (-separacion*4, "misiones",     "Misiones",  (30, 50, 30), (50, 200, 50),  (100, 255, 100)),
        (-separacion*5, "ataque",       "Ataque",    (60, 20, 20), (200, 50, 50),  (255, 80, 80)),
    ]

    botones = []
    for offset, tag, etiqueta, c_fondo, c_borde, c_hover in configuracion:
        img = iconos.get(tag) if iconos else None
        # intentar cargar icono específico si no está en el dict
        if img is None:
            ruta = os.path.join(BASE_DIR, "assets", "imagenes", f"{tag}.png")
            if os.path.exists(ruta):
                raw = pygame.image.load(ruta).convert_alpha()
                img = pygame.transform.scale(raw, (28, 28))

        btn = BotonCircular(
            cx=x_base + offset,
            cy=cy,
            radio=30,
            imagen=img,
            etiqueta=etiqueta,
            color_fondo=c_fondo,
            color_borde=c_borde,
            color_borde_hover=c_hover,
            tag=tag,
        )
        botones.append(btn)

    return botones
