# -*- coding: utf-8 -*-
# Copyright (c) 2026 [Cayetano Tielas Fernandez]. Todos los derechos reservados.
# Módulo: Estado de Juego — Laboratorio de Investigación

import pygame
import os

BASE_DIR = os.path.dirname(__file__)

# Datos de las 4 tarjetas
TARJETAS_INFO = [
    {"nombre": "RECURSOS",  "archivo": "targeta_recursos.png"},
    {"nombre": "ECONOMÍA",  "archivo": "targeta_economia.png"},
    {"nombre": "TROPAS",    "archivo": "targeta_tropas.png"},
    {"nombre": "AVANCES",   "archivo": "targeta_avances.png"},
]

# Dimensiones del panel central (popup grande)
PANEL_ANCHO = 900
PANEL_ALTO  = 580

# Tamaño fijo cuadrado de cada tarjeta
TAR_SIZE = 180

# Frames que dura el mensaje de sub-menú (~3 s a 60 FPS)
MSG_DURACION = 180


class EscenaInvestigacion:
    """Estado de juego: menú de laboratorio como panel central sobre la ciudad."""

    # ------------------------------------------------------------------
    def __init__(self):
        self.fuente_titulo  = pygame.font.SysFont("Arial", 42, bold=True)
        self.fuente_nivel   = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_tarjeta = pygame.font.SysFont("Arial", 15, bold=True)
        self.fuente_msg     = pygame.font.SysFont("Arial", 19, bold=True)
        self.fuente_cerrar  = pygame.font.SysFont("Arial", 18, bold=True)
        self.fuente_hint    = pygame.font.SysFont("Arial", 13)

        # Fondo del laboratorio escalado al tamaño exacto del panel
        ruta_fondo = os.path.join(BASE_DIR, "assets", "imagenes", "fondo_lab.jpg")
        img_fondo = pygame.image.load(ruta_fondo).convert()
        self.fondo_panel = pygame.transform.scale(img_fondo, (PANEL_ANCHO, PANEL_ALTO))

        # Cargar tarjetas: eliminar fondo blanco, escalar a cuadrado uniforme
        self.tarjetas = []
        for info in TARJETAS_INFO:
            ruta = os.path.join(BASE_DIR, "assets", "imagenes", info["archivo"])
            img  = pygame.image.load(ruta).convert()
            img.set_colorkey((255, 255, 255))          # elimina fondo blanco
            img  = pygame.transform.smoothscale(img, (TAR_SIZE, TAR_SIZE))
            self.tarjetas.append({
                "img":    img,
                "nombre": info["nombre"],
                "rect":   None,   # se asigna en dibujar()
            })

        # Rect del botón cerrar (se actualiza en dibujar)
        self.rect_cerrar = None

        # Mensaje temporal al hacer clic en una tarjeta
        self.mensaje_texto  = ""
        self.mensaje_frames = 0

    # ------------------------------------------------------------------
    def _panel_rect(self, ancho, alto):
        """Rect del panel central."""
        px = ancho // 2 - PANEL_ANCHO // 2
        py = alto  // 2 - PANEL_ALTO  // 2
        return pygame.Rect(px, py, PANEL_ANCHO, PANEL_ALTO)

    def _posiciones_tarjetas(self, panel):
        """Posiciones (x, y) de las 4 tarjetas en cuadrícula 2×2 dentro del panel."""
        # Zona vertical disponible (deja espacio al título arriba y al nivel abajo)
        y_inicio = panel.y + 86
        y_fin    = panel.y + PANEL_ALTO - 60

        espacio_v = y_fin - y_inicio
        gap_v     = (espacio_v - 2 * TAR_SIZE) // 3
        fila1_y   = y_inicio + gap_v
        fila2_y   = fila1_y + TAR_SIZE + gap_v

        # Zona horizontal: centrar 2 columnas dentro del panel
        gap_h = (PANEL_ANCHO - 2 * TAR_SIZE) // 3
        col1_x = panel.x + gap_h
        col2_x = col1_x + TAR_SIZE + gap_h

        return [
            (col1_x, fila1_y),
            (col2_x, fila1_y),
            (col1_x, fila2_y),
            (col2_x, fila2_y),
        ]

    # ------------------------------------------------------------------
    def dibujar(self, pantalla, nivel_ciudad=1):
        """
        Dibuja el panel de investigación encima de lo que ya hay en pantalla.
        Recibe 'nivel_ciudad' directamente desde main.py (ej: self.logica.capitulo_actual).
        """
        ancho, alto = pantalla.get_size()
        panel = self._panel_rect(ancho, alto)

        # 1 — Overlay oscuro sobre toda la pantalla (ciudad visible pero apagada)
        overlay_fondo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        overlay_fondo.fill((0, 0, 0, 175))
        pantalla.blit(overlay_fondo, (0, 0))

        # 2 — Fondo del laboratorio recortado al panel
        pantalla.blit(self.fondo_panel, (panel.x, panel.y))

        # 3 — Capa oscurecedora sobre el fondo del panel (mejora legibilidad)
        panel_overlay = pygame.Surface((PANEL_ANCHO, PANEL_ALTO), pygame.SRCALPHA)
        panel_overlay.fill((5, 5, 20, 155))
        pantalla.blit(panel_overlay, (panel.x, panel.y))

        # 4 — Borde del panel
        pygame.draw.rect(pantalla, (90, 110, 200), panel, 3, border_radius=12)

        # 5 — Botón cerrar (X) esquina superior derecha del panel
        btn_cerrar = pygame.Rect(panel.right - 42, panel.y + 9, 33, 33)
        self.rect_cerrar = btn_cerrar
        mouse_pos = pygame.mouse.get_pos()
        color_x = (210, 40, 40) if btn_cerrar.collidepoint(mouse_pos) else (150, 30, 30)
        pygame.draw.rect(pantalla, color_x, btn_cerrar, border_radius=6)
        txt_x = self.fuente_cerrar.render("X", True, (255, 255, 255))
        pantalla.blit(txt_x, (
            btn_cerrar.x + btn_cerrar.width  // 2 - txt_x.get_width()  // 2,
            btn_cerrar.y + btn_cerrar.height // 2 - txt_x.get_height() // 2,
        ))

        # 6 — Título "LABORATORIO" centrado en la cabecera del panel
        txt_titulo = self.fuente_titulo.render("LABORATORIO", True, (255, 255, 255))
        pantalla.blit(txt_titulo, (
            panel.x + PANEL_ANCHO // 2 - txt_titulo.get_width() // 2,
            panel.y + 16,
        ))

        # 7 — Separador bajo el título
        pygame.draw.line(
            pantalla, (90, 110, 200),
            (panel.x + 20,     panel.y + 68),
            (panel.right - 20, panel.y + 68), 2,
        )

        # 8 — Tarjetas en cuadrícula 2×2
        posiciones = self._posiciones_tarjetas(panel)
        for i, tarjeta in enumerate(self.tarjetas):
            x, y = posiciones[i]
            rect = pygame.Rect(x, y, TAR_SIZE, TAR_SIZE)
            tarjeta["rect"] = rect

            # Fondo semitransparente detrás de cada tarjeta
            fondo_t = pygame.Surface((TAR_SIZE, TAR_SIZE), pygame.SRCALPHA)
            fondo_t.fill((10, 10, 30, 200))
            pantalla.blit(fondo_t, (x, y))

            # Imagen (con colorkey ya aplicado)
            pantalla.blit(tarjeta["img"], (x, y))

            # Borde: dorado en hover, azul en reposo
            hover       = rect.collidepoint(mouse_pos)
            color_borde = (255, 215, 0) if hover else (70, 95, 175)
            pygame.draw.rect(pantalla, color_borde, rect, 3, border_radius=8)

            # Etiqueta del nombre centrada debajo de la tarjeta
            txt_lb = self.fuente_tarjeta.render(tarjeta["nombre"], True, (210, 210, 255))
            pantalla.blit(txt_lb, (
                x + TAR_SIZE // 2 - txt_lb.get_width() // 2,
                y + TAR_SIZE + 5,
            ))

        # 9 — Mensaje temporal de sub-menú (fade-out)
        if self.mensaje_frames > 0:
            alpha = min(255, self.mensaje_frames * 3)
            msg_surf = self.fuente_msg.render(self.mensaje_texto, True, (255, 220, 80))
            msg_surf.set_alpha(alpha)
            pantalla.blit(msg_surf, (
                panel.x + PANEL_ANCHO // 2 - msg_surf.get_width()  // 2,
                panel.y + PANEL_ALTO  // 2 - msg_surf.get_height() // 2,
            ))
            self.mensaje_frames -= 1

        # 10 — "Nivel Ciudad: X" centrado en el pie del panel
        txt_nivel = self.fuente_nivel.render(f"Nivel Ciudad: {nivel_ciudad}", True, (175, 205, 255))
        pantalla.blit(txt_nivel, (
            panel.x + PANEL_ANCHO // 2 - txt_nivel.get_width() // 2,
            panel.y + PANEL_ALTO - 44,
        ))

        # 11 — Hint ESC en esquina inferior izquierda del panel
        txt_esc = self.fuente_hint.render("[ ESC ]  Cerrar", True, (100, 100, 130))
        pantalla.blit(txt_esc, (panel.x + 12, panel.y + PANEL_ALTO - 20))

    # ------------------------------------------------------------------
    def manejar_eventos(self, evento):
        """
        Procesa un evento de pygame.
        Devuelve 'CIUDAD' para cerrar el panel; None en cualquier otro caso.
        """
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return 'CIUDAD'

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            # Botón X
            if self.rect_cerrar and self.rect_cerrar.collidepoint(pos):
                return 'CIUDAD'

            # Tarjetas: mostrar mensaje temporal, NO subir nivel
            for tarjeta in self.tarjetas:
                if tarjeta["rect"] and tarjeta["rect"].collidepoint(pos):
                    nombre = tarjeta["nombre"].capitalize()
                    self.mensaje_texto  = f"Abriendo sub-menú de {nombre}..."
                    self.mensaje_frames = MSG_DURACION
                    print(f"Abriendo sub-menú de {nombre}...")
                    return None

        return None
