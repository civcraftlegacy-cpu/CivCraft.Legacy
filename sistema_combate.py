# -*- coding: utf-8 -*-

import json
import math
import os
import random
from dataclasses import dataclass

import pygame
from arbol_tecnologico import CATEGORIAS


BASE_DIR = os.path.dirname(__file__)
PROGRESO_PATH = os.path.join(BASE_DIR, "progreso.json")

EVENTO_UNIDAD_MUERTA = pygame.USEREVENT + 41
EVENTO_VICTORIA_BATALLA = pygame.USEREVENT + 42
EVENTO_DERROTA_BATALLA = pygame.USEREVENT + 43

ESTADO_JUGADOR = "ESTADO_JUGADOR"
ESTADO_ENEMIGO = "ESTADO_ENEMIGO"
ESTADO_ANIMACION = "ESTADO_ANIMACION"

COLOR_PANEL = (10, 14, 34)
COLOR_BORDE = (70, 110, 190)
COLOR_CAMPO = (26, 30, 46)
COLOR_LINEA = (60, 72, 115)
COLOR_TEXTO = (235, 240, 255)
COLOR_DORADO = (255, 215, 0)

LANES_Y = [100, 235, 370]


def clamp(valor, minimo, maximo):
	return max(minimo, min(maximo, valor))


def lerp(a, b, t):
	return a + (b - a) * t


@dataclass
class CardDefinition:
	unit_id: str
	nombre: str
	coste: float
	cooldown: float
	color: tuple


@dataclass
class LevelData:
	nivel: int
	recompensa_oro: int
	recompensa_recursos: dict
	base_enemiga_hp: int
	base_jugador_hp: int
	escala: float
	es_boss: bool
	spawns: list


CARD_DEFS = [
	CardDefinition("lancero", "Lancero", 3.0, 2.6, (120, 210, 255)),
	CardDefinition("berserker", "Berserker", 4.0, 4.2, (255, 120, 90)),
	CardDefinition("arquero_hielo", "Arquero Hielo", 4.0, 4.8, (120, 220, 255)),
	CardDefinition("campeon", "Campeon", 6.0, 9.5, (255, 220, 120)),
]


UNIT_DEFS = {
	"lancero": {
		"nombre": "Lancero",
		"max_hp": 120,
		"attack": 24,
		"defense": 10,
		"range": 34,
		"move_speed": 98,
		"attack_interval": 0.92,
		"damage_type": "perforacion",
		"armor_type": "ligero",
		"shape": "diamond",
		"threat": 2.0,
		"powerful": False,
		"size": 22,
	},
	"berserker": {
		"nombre": "Berserker",
		"max_hp": 160,
		"attack": 34,
		"defense": 8,
		"range": 28,
		"move_speed": 106,
		"attack_interval": 1.10,
		"damage_type": "corte",
		"armor_type": "ligero",
		"shape": "hex",
		"threat": 2.3,
		"powerful": True,
		"size": 24,
	},
	"arquero_hielo": {
		"nombre": "Arquero de Hielo",
		"max_hp": 105,
		"attack": 22,
		"defense": 6,
		"range": 190,
		"move_speed": 82,
		"attack_interval": 1.25,
		"damage_type": "hielo",
		"armor_type": "ligero",
		"shape": "triangle",
		"threat": 2.7,
		"powerful": False,
		"size": 21,
		"projectile_speed": 320,
		"slow_pct": 0.32,
		"slow_time": 1.8,
	},
	"campeon": {
		"nombre": "Campeon",
		"max_hp": 300,
		"attack": 42,
		"defense": 18,
		"range": 42,
		"move_speed": 88,
		"attack_interval": 1.18,
		"damage_type": "corte",
		"armor_type": "tanque",
		"shape": "champion",
		"threat": 4.2,
		"powerful": True,
		"size": 28,
		"ability_cd": 8.0,
		"heal_amount": 28,
		"heal_radius": 110,
	},
	"raider": {
		"nombre": "Asaltante",
		"max_hp": 110,
		"attack": 18,
		"defense": 8,
		"range": 28,
		"move_speed": 92,
		"attack_interval": 1.05,
		"damage_type": "corte",
		"armor_type": "ligero",
		"shape": "diamond",
		"threat": 1.8,
		"powerful": False,
		"size": 21,
	},
	"bruto": {
		"nombre": "Bruto",
		"max_hp": 260,
		"attack": 26,
		"defense": 22,
		"range": 28,
		"move_speed": 72,
		"attack_interval": 1.32,
		"damage_type": "impacto",
		"armor_type": "tanque",
		"shape": "square",
		"threat": 3.4,
		"powerful": True,
		"size": 27,
	},
	"ballestero": {
		"nombre": "Ballestero",
		"max_hp": 98,
		"attack": 18,
		"defense": 7,
		"range": 175,
		"move_speed": 76,
		"attack_interval": 1.15,
		"damage_type": "flecha",
		"armor_type": "ligero",
		"shape": "triangle",
		"threat": 2.8,
		"powerful": False,
		"size": 20,
		"projectile_speed": 350,
	},
	"perforador": {
		"nombre": "Perforador",
		"max_hp": 150,
		"attack": 30,
		"defense": 12,
		"range": 36,
		"move_speed": 88,
		"attack_interval": 1.05,
		"damage_type": "perforacion",
		"armor_type": "ligero",
		"shape": "hex",
		"threat": 2.6,
		"powerful": False,
		"size": 23,
	},
	"boss_coloso": {
		"nombre": "Coloso",
		"max_hp": 1650,
		"attack": 72,
		"defense": 34,
		"range": 44,
		"move_speed": 50,
		"attack_interval": 1.65,
		"damage_type": "impacto",
		"armor_type": "boss",
		"shape": "boss",
		"threat": 8.0,
		"powerful": True,
		"size": 42,
		"ability_cd": 4.5,
		"boss": True,
	},
}


DAMAGE_MATRIX = {
	("flecha", "tanque"): 0.60,
	("flecha", "boss"): 0.55,
	("perforacion", "tanque"): 1.45,
	("perforacion", "boss"): 1.20,
	("hielo", "tanque"): 0.85,
	("impacto", "ligero"): 1.12,
}


class ProgressManager:
	def __init__(self, ruta=PROGRESO_PATH):
		self.ruta = ruta
		self.data = self._cargar()

	def _cargar(self):
		if os.path.exists(self.ruta):
			try:
				with open(self.ruta, "r", encoding="utf-8") as fh:
					data = json.load(fh)
					return {
						"max_unlocked": int(data.get("max_unlocked", 1)),
						"last_selected": int(data.get("last_selected", 1)),
						"victorias": [int(v) for v in data.get("victorias", [])],
					}
			except Exception:
				pass
		return {"max_unlocked": 1, "last_selected": 1, "victorias": []}

	def guardar(self):
		with open(self.ruta, "w", encoding="utf-8") as fh:
			json.dump(self.data, fh, ensure_ascii=False, indent=2)

	def nivel_desbloqueado(self, nivel):
		return nivel <= self.data.get("max_unlocked", 1)

	def marcar_victoria(self, nivel):
		victorias = set(self.data.get("victorias", []))
		victorias.add(int(nivel))
		self.data["victorias"] = sorted(victorias)
		self.data["max_unlocked"] = max(self.data.get("max_unlocked", 1), min(50, nivel + 1))
		self.data["last_selected"] = min(50, self.data["max_unlocked"])
		self.guardar()

	def seleccionar(self, nivel):
		self.data["last_selected"] = int(clamp(nivel, 1, 50))
		self.guardar()


class LevelManager:
	ENEMIGOS_ROTACION = ["raider", "ballestero", "perforador", "bruto"]

	@staticmethod
	def escala(nivel):
		return 1.0 * (1.115 ** (nivel - 1))

	@classmethod
	def crear_nivel(cls, nivel):
		nivel = int(clamp(nivel, 1, 50))
		escala = cls.escala(nivel)
		rng = random.Random(7000 + nivel)
		es_boss = (nivel % 10 == 0)
		recompensa_oro = int(2800 * (1.18 ** (nivel - 1)))
		recompensa_recursos = {
			"comida": int(220 * escala),
			"agua": int(200 * escala),
			"electricidad": int(180 * escala),
		}

		spawns = []
		tiempo = 2.5
		bloques = 6 + (nivel // 2)
		for idx in range(bloques):
			lane = rng.choice(LANES_Y)
			unit_id = cls.ENEMIGOS_ROTACION[(nivel + idx) % len(cls.ENEMIGOS_ROTACION)]
			cantidad = 1 + (1 if nivel > 8 and idx % 3 == 0 else 0)
			for n in range(cantidad):
				spawns.append({"time": tiempo + n * 0.35, "unit_id": unit_id, "lane": lane})
			if idx % 2 == 1:
				apoyo = "ballestero" if idx % 4 else "perforador"
				spawns.append({"time": tiempo + 0.75, "unit_id": apoyo, "lane": rng.choice(LANES_Y)})
			tiempo += max(0.95, 2.6 - min(1.4, nivel * 0.03))

		if es_boss:
			spawns.append({"time": tiempo + 2.0, "unit_id": "boss_coloso", "lane": LANES_Y[1]})

		return LevelData(
			nivel=nivel,
			recompensa_oro=recompensa_oro,
			recompensa_recursos=recompensa_recursos,
			base_enemiga_hp=int(1400 * escala + (400 if es_boss else 0)),
			base_jugador_hp=int(1200 * max(1.0, escala * 0.92)),
			escala=escala,
			es_boss=es_boss,
			spawns=spawns,
		)


class ScreenShake:
	def __init__(self):
		self.intensity = 0.0
		self.time_left = 0.0

	def add(self, intensity, duration=0.18):
		self.intensity = max(self.intensity, intensity)
		self.time_left = max(self.time_left, duration)

	def update(self, dt):
		if self.time_left > 0:
			self.time_left = max(0.0, self.time_left - dt)
			self.intensity = max(0.0, self.intensity * 0.88)

	def offset(self):
		if self.time_left <= 0:
			return (0, 0)
		return (
			random.randint(-int(self.intensity), int(self.intensity)),
			random.randint(-int(self.intensity), int(self.intensity)),
		)


class Particle(pygame.sprite.Sprite):
	def __init__(self, x, y, color, velocity, life, radius=3, gravity=0.0, fade=True):
		super().__init__()
		self.pos = pygame.Vector2(x, y)
		self.vel = pygame.Vector2(velocity)
		self.life = life
		self.max_life = life
		self.radius = radius
		self.gravity = gravity
		self.fade = fade
		self.color = color
		self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=(int(x), int(y)))

	def update(self, dt):
		self.life -= dt
		if self.life <= 0:
			self.kill()
			return
		self.vel.y += self.gravity * dt
		self.pos += self.vel * dt
		self.rect.center = (int(self.pos.x), int(self.pos.y))

	def render(self, surface, offset):
		alpha = 255 if not self.fade else int(255 * (self.life / max(0.01, self.max_life)))
		color = (*self.color[:3], alpha)
		x = int(self.pos.x + offset[0])
		y = int(self.pos.y + offset[1])
		pygame.draw.circle(surface, (0, 0, 0, max(0, alpha // 3)), (x + 2, y + 2), max(1, self.radius))
		pygame.draw.circle(surface, color, (x, y), max(1, self.radius))


class FloatingText(pygame.sprite.Sprite):
	def __init__(self, x, y, texto, color):
		super().__init__()
		self.pos = pygame.Vector2(x, y)
		self.texto = texto
		self.color = color
		self.life = 0.7
		self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=(int(x), int(y)))

	def update(self, dt):
		self.life -= dt
		if self.life <= 0:
			self.kill()
			return
		self.pos.y -= 26 * dt
		self.rect.center = (int(self.pos.x), int(self.pos.y))

	def render(self, surface, offset, fuente):
		alpha = int(255 * (self.life / 0.7))
		txt = fuente.render(self.texto, True, self.color)
		txt.set_alpha(alpha)
		x = int(self.pos.x + offset[0] - txt.get_width() // 2)
		y = int(self.pos.y + offset[1] - txt.get_height() // 2)
		shadow = fuente.render(self.texto, True, (0, 0, 0))
		shadow.set_alpha(alpha // 2)
		surface.blit(shadow, (x + 2, y + 2))
		surface.blit(txt, (x, y))


class BaseCore(pygame.sprite.Sprite):
	def __init__(self, team, x, y, hp):
		super().__init__()
		self.team = team
		self.max_hp = hp
		self.hp = float(hp)
		self.attack = 0.0
		self.defense = 12.0
		self.threat = 1.2
		self.armor_type = "estructura"
		self.damage_type = "impacto"
		self.range = 0
		self.pos = pygame.Vector2(x, y)
		self.image = pygame.Surface((90, 130), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=(int(x), int(y)))

	def update(self, dt):
		self.rect.center = (int(self.pos.x), int(self.pos.y))

	def render(self, surface, offset):
		x = self.rect.x + offset[0]
		y = self.rect.y + offset[1]
		sombra = pygame.Rect(x + 8, y + 10, self.rect.width, self.rect.height)
		pygame.draw.rect(surface, (0, 0, 0), sombra, border_radius=16)
		cuerpo = pygame.Rect(x, y, self.rect.width, self.rect.height)
		col = (60, 160, 250) if self.team == "ally" else (220, 80, 80)
		pygame.draw.rect(surface, (22, 28, 48), cuerpo, border_radius=16)
		pygame.draw.rect(surface, col, cuerpo, 3, border_radius=16)
		pygame.draw.rect(surface, col, (x + 18, y + 18, self.rect.width - 36, self.rect.height - 42), border_radius=12)
		self._draw_hp(surface, x, y - 14)

	def _draw_hp(self, surface, x, y):
		ratio = clamp(self.hp / max(1, self.max_hp), 0.0, 1.0)
		w = self.rect.width
		pygame.draw.rect(surface, (18, 18, 22), (x, y, w, 8), border_radius=4)
		color = (int(lerp(220, 80, ratio)), int(lerp(40, 220, ratio)), 60)
		pygame.draw.rect(surface, color, (x, y, int(w * ratio), 8), border_radius=4)
		pygame.draw.rect(surface, (230, 230, 240), (x, y, w, 8), 1, border_radius=4)


class CombatUnit(pygame.sprite.Sprite):
	def __init__(self, scene, team, unit_id, x, y, escala=1.0):
		super().__init__()
		self.scene = scene
		self.team = team
		self.unit_id = unit_id
		base = dict(UNIT_DEFS[unit_id])
		self.nombre = base["nombre"]
		self.max_hp = base["max_hp"] * (escala if team == "enemy" else 1.0)
		self.hp = float(self.max_hp)
		self.attack = base["attack"] * (escala if team == "enemy" else 1.0)
		self.defense = base["defense"] * (escala if team == "enemy" else 1.0)
		self.range = base["range"]
		self.move_speed = base["move_speed"]
		self.base_attack_interval = base["attack_interval"]
		self.damage_type = base["damage_type"]
		self.armor_type = base["armor_type"]
		self.shape = base["shape"]
		self.threat = base["threat"]
		self.powerful = base.get("powerful", False)
		self.size = base["size"]
		self.projectile_speed = base.get("projectile_speed", 0)
		self.slow_pct = base.get("slow_pct", 0.0)
		self.slow_time = base.get("slow_time", 0.0)
		self.ability_cd = base.get("ability_cd", 0.0)
		self.heal_amount = base.get("heal_amount", 0)
		self.heal_radius = base.get("heal_radius", 0)
		self.boss = base.get("boss", False)
		self.pos = pygame.Vector2(x, y)
		self.vel = pygame.Vector2(0, 0)
		self.target = None
		self.attack_timer = random.uniform(0.05, 0.35)
		self.slow_timer = 0.0
		self.slow_factor = 1.0
		self.special_timer = self.ability_cd
		self.attack_flash = 0.0
		self.dead = False
		self.image = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=(int(x), int(y)))

	def is_ranged(self):
		return self.range >= 120

	def current_attack_interval(self):
		if self.unit_id == "berserker":
			missing = 1.0 - (self.hp / max(1.0, self.max_hp))
			return self.base_attack_interval * max(0.42, 1.0 - missing * 0.55)
		return self.base_attack_interval

	def update(self, dt, manager):
		if self.dead:
			return
		self.attack_flash = max(0.0, self.attack_flash - dt * 4.0)
		self.attack_timer = max(0.0, self.attack_timer - dt)
		self.slow_timer = max(0.0, self.slow_timer - dt)
		self.slow_factor = (1.0 - self.slow_pct) if self.slow_timer > 0 else 1.0
		if self.ability_cd > 0:
			self.special_timer = max(0.0, self.special_timer - dt)

		if self.unit_id == "campeon" and self.special_timer <= 0:
			self._usar_grito(manager)
		elif self.boss and self.special_timer <= 0:
			self._usar_golpe_jefe(manager)

		if self.target is None or not manager.is_valid_target(self, self.target):
			self.target = manager.find_best_target(self)

		if self.target and manager.distance_to_target(self, self.target) <= self.range:
			self.vel.xy = (0, 0)
			if self.attack_timer <= 0:
				self._atacar(manager)
		else:
			self._mover(manager)

		self.pos += self.vel * dt
		self.pos.x = clamp(self.pos.x, manager.field_rect.left + 45, manager.field_rect.right - 45)
		self.pos.y = clamp(self.pos.y, manager.field_rect.top + 35, manager.field_rect.bottom - 35)
		self.rect.center = (int(self.pos.x), int(self.pos.y))

	def _mover(self, manager):
		direction = 1 if self.team == "ally" else -1
		desired = pygame.Vector2(direction, 0)
		if self.target and hasattr(self.target, "pos"):
			vec = pygame.Vector2(self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y)
			if vec.length_squared() > 0:
				desired = vec.normalize()

		separation = pygame.Vector2(0, 0)
		for ally in manager.units:
			if ally is self or ally.team != self.team or ally.dead:
				continue
			delta = self.pos - ally.pos
			dist = delta.length()
			if 0 < dist < (self.size + ally.size + 8):
				separation += delta.normalize() * ((self.size + ally.size + 8 - dist) / 18.0)

		self.vel = desired * self.move_speed * self.slow_factor + separation * 70

	def _atacar(self, manager):
		self.attack_timer = self.current_attack_interval()
		self.attack_flash = 1.0
		if self.powerful or self.boss:
			self.scene.shake.add(5 if not self.boss else 8)
		target = self.target
		if target is None:
			return

		if self.is_ranged():
			proj = Projectile(self.scene, self, target)
			manager.projectiles.add(proj)
			manager.all_sprites.add(proj)
		else:
			manager.apply_damage(target, self, self.attack, self.damage_type)
			if hasattr(target, "pos"):
				manager.spawn_sparks(target.pos.x, target.pos.y, (255, 220, 120), 8)

	def _usar_grito(self, manager):
		self.special_timer = self.ability_cd
		curados = 0
		for ally in manager.units:
			if ally.team != self.team or ally.dead:
				continue
			if ally.pos.distance_to(self.pos) <= self.heal_radius and ally.hp < ally.max_hp:
				ally.hp = min(ally.max_hp, ally.hp + self.heal_amount)
				manager.floating_texts.add(FloatingText(ally.pos.x, ally.pos.y - 28, f"+{self.heal_amount}", (120, 255, 140)))
				curados += 1
		if curados:
			manager.spawn_ring(self.pos.x, self.pos.y, (120, 255, 180), 18)
			self.scene.shake.add(3)

	def _usar_golpe_jefe(self, manager):
		self.special_timer = self.ability_cd
		manager.spawn_ring(self.pos.x, self.pos.y, (255, 120, 90), 24)
		self.scene.shake.add(9, 0.28)
		for target in list(manager.units):
			if target.team == self.team or target.dead:
				continue
			if target.pos.distance_to(self.pos) <= 100:
				manager.apply_damage(target, self, self.attack * 0.8, "impacto")

	def render(self, surface, offset):
		x = int(self.pos.x + offset[0])
		y = int(self.pos.y + offset[1])
		self._draw_shadow(surface, x, y)
		self._draw_body(surface, x, y)
		self._draw_health(surface, x, y)

	def _main_color(self):
		if self.team == "ally":
			return (110, 190, 255)
		return (240, 100, 100) if not self.boss else (255, 140, 70)

	def _draw_shadow(self, surface, x, y):
		shadow = pygame.Rect(x - self.size // 2, y + self.size // 2, self.size, self.size // 2)
		pygame.draw.ellipse(surface, (0, 0, 0), shadow)

	def _draw_body(self, surface, x, y):
		col = self._main_color()
		if self.attack_flash > 0:
			col = tuple(min(255, c + 50) for c in col)
		outline = (240, 240, 250)
		if self.shape == "square":
			rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
			pygame.draw.rect(surface, (14, 18, 28), rect.move(3, 4), border_radius=7)
			pygame.draw.rect(surface, col, rect, border_radius=7)
			pygame.draw.rect(surface, outline, rect, 2, border_radius=7)
		elif self.shape == "triangle":
			pts = [(x, y - self.size // 2), (x - self.size // 2, y + self.size // 2), (x + self.size // 2, y + self.size // 2)]
			pygame.draw.polygon(surface, (14, 18, 28), [(px + 3, py + 4) for px, py in pts])
			pygame.draw.polygon(surface, col, pts)
			pygame.draw.polygon(surface, outline, pts, 2)
		elif self.shape == "hex":
			pts = [(x - self.size // 2, y), (x - self.size // 4, y - self.size // 2), (x + self.size // 4, y - self.size // 2), (x + self.size // 2, y), (x + self.size // 4, y + self.size // 2), (x - self.size // 4, y + self.size // 2)]
			pygame.draw.polygon(surface, (14, 18, 28), [(px + 3, py + 4) for px, py in pts])
			pygame.draw.polygon(surface, col, pts)
			pygame.draw.polygon(surface, outline, pts, 2)
		elif self.shape == "champion":
			rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
			pygame.draw.rect(surface, (14, 18, 28), rect.move(3, 4), border_radius=10)
			pygame.draw.rect(surface, col, rect, border_radius=10)
			pygame.draw.rect(surface, COLOR_DORADO, rect, 3, border_radius=10)
		elif self.shape == "boss":
			rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
			pygame.draw.rect(surface, (14, 18, 28), rect.move(4, 5), border_radius=14)
			pygame.draw.rect(surface, col, rect, border_radius=14)
			pygame.draw.rect(surface, COLOR_DORADO, rect, 4, border_radius=14)
		else:
			pts = [(x, y - self.size // 2), (x - self.size // 2, y), (x, y + self.size // 2), (x + self.size // 2, y)]
			pygame.draw.polygon(surface, (14, 18, 28), [(px + 3, py + 4) for px, py in pts])
			pygame.draw.polygon(surface, col, pts)
			pygame.draw.polygon(surface, outline, pts, 2)

	def _draw_health(self, surface, x, y):
		ratio = clamp(self.hp / max(1.0, self.max_hp), 0.0, 1.0)
		bar_w = max(24, self.size + 12)
		left = x - bar_w // 2
		top = y - self.size // 2 - 12
		pygame.draw.rect(surface, (12, 12, 16), (left, top, bar_w, 7), border_radius=4)
		color = (int(lerp(230, 80, ratio)), int(lerp(40, 220, ratio)), 65)
		pygame.draw.rect(surface, color, (left, top, int(bar_w * ratio), 7), border_radius=4)
		pygame.draw.rect(surface, (230, 230, 240), (left, top, bar_w, 7), 1, border_radius=4)


class Projectile(pygame.sprite.Sprite):
	def __init__(self, scene, source, target):
		super().__init__()
		self.scene = scene
		self.source = source
		self.target = target
		self.pos = pygame.Vector2(source.pos)
		self.speed = source.projectile_speed or 320
		self.damage = source.attack
		self.damage_type = source.damage_type
		self.team = source.team
		self.color = (150, 230, 255) if source.unit_id == "arquero_hielo" else (245, 220, 150)
		self.radius = 4 if source.unit_id == "arquero_hielo" else 3
		self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
		self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
		self.trail_cd = 0.0

	def update(self, dt, manager):
		if self.target is None or not manager.is_valid_target(self.source, self.target):
			self.kill()
			return
		direction = pygame.Vector2(self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y)
		dist = direction.length()
		if dist < max(10, self.speed * dt):
			manager.apply_damage(self.target, self.source, self.damage, self.damage_type)
			if self.source.unit_id == "arquero_hielo" and hasattr(self.target, "slow_timer"):
				self.target.slow_timer = max(self.target.slow_timer, self.source.slow_time)
				self.target.slow_pct = max(self.target.slow_pct, self.source.slow_pct)
			manager.spawn_sparks(self.pos.x, self.pos.y, self.color, 10)
			self.kill()
			return
		if dist > 0:
			self.pos += direction.normalize() * self.speed * dt
		self.rect.center = (int(self.pos.x), int(self.pos.y))
		self.trail_cd -= dt
		if self.trail_cd <= 0:
			self.trail_cd = 0.03
			manager.particles.add(Particle(self.pos.x, self.pos.y, self.color, (0, 0), 0.24, radius=2))

	def render(self, surface, offset):
		x = int(self.pos.x + offset[0])
		y = int(self.pos.y + offset[1])
		pygame.draw.circle(surface, (0, 0, 0), (x + 2, y + 2), self.radius)
		pygame.draw.circle(surface, self.color, (x, y), self.radius)


class EntityManager:
	def __init__(self, scene, field_rect):
		self.scene = scene
		self.field_rect = field_rect
		self.all_sprites = pygame.sprite.Group()
		self.units = pygame.sprite.Group()
		self.projectiles = pygame.sprite.Group()
		self.particles = pygame.sprite.Group()
		self.floating_texts = pygame.sprite.Group()
		self.structures = pygame.sprite.Group()

	def add_structure(self, structure):
		self.structures.add(structure)
		self.all_sprites.add(structure)

	def spawn_unit(self, team, unit_id, x, y, escala=1.0):
		unit = CombatUnit(self.scene, team, unit_id, x, y, escala)
		self.units.add(unit)
		self.all_sprites.add(unit)
		return unit

	def is_valid_target(self, source, target):
		if target is None:
			return False
		if hasattr(target, "dead") and target.dead:
			return False
		if hasattr(target, "hp") and target.hp <= 0:
			return False
		return getattr(target, "team", None) != getattr(source, "team", None)

	def distance_to_target(self, source, target):
		if not hasattr(target, "pos"):
			return 99999
		return source.pos.distance_to(target.pos)

	def find_best_target(self, unit):
		candidatos = []
		for target in self.units:
			if not self.is_valid_target(unit, target):
				continue
			dist = unit.pos.distance_to(target.pos)
			score = target.threat * 180 - dist
			if hasattr(target, "is_ranged") and target.is_ranged():
				score += 35
			candidatos.append((score, target))

		objetivo_base = self.scene.base_enemiga if unit.team == "ally" else self.scene.base_jugador
		if objetivo_base and objetivo_base.hp > 0:
			dist = unit.pos.distance_to(objetivo_base.pos)
			score = objetivo_base.threat * 160 - dist * 0.8
			candidatos.append((score, objetivo_base))

		if not candidatos:
			return None
		candidatos.sort(key=lambda item: item[0], reverse=True)
		return candidatos[0][1]

	def apply_damage(self, target, source, damage, damage_type):
		if not self.is_valid_target(source, target):
			return
		mult = DAMAGE_MATRIX.get((damage_type, getattr(target, "armor_type", "ligero")), 1.0)
		final = max(1.0, damage * mult - getattr(target, "defense", 0) * 0.28)
		target.hp = max(0.0, target.hp - final)
		if isinstance(target, BaseCore) and getattr(target, "team", None) == "ally":
			self.scene.disparar_flash_torre(min(1.0, final / 50.0))
		self.floating_texts.add(FloatingText(target.pos.x, target.pos.y - 30, str(int(final)), (255, 235, 150)))
		if target.hp <= 0:
			if hasattr(target, "dead"):
				target.dead = True
			self.spawn_explosion(target.pos.x, target.pos.y, target.team)
			if getattr(target, "powerful", False) or getattr(target, "boss", False):
				self.scene.shake.add(7 if not getattr(target, "boss", False) else 12, 0.24)
			pygame.event.post(pygame.event.Event(EVENTO_UNIDAD_MUERTA, {
				"unit_id": getattr(target, "unit_id", "base"),
				"team": getattr(target, "team", "neutral"),
				"is_structure": isinstance(target, BaseCore),
			}))
			target.kill()

	def spawn_sparks(self, x, y, color, amount):
		for _ in range(amount):
			ang = random.uniform(0, math.tau)
			speed = random.uniform(35, 140)
			vel = pygame.Vector2(math.cos(ang) * speed, math.sin(ang) * speed)
			self.particles.add(Particle(x, y, color, vel, random.uniform(0.15, 0.35), radius=random.randint(2, 3)))

	def spawn_explosion(self, x, y, team):
		base_color = (255, 110, 90) if team == "enemy" else (120, 200, 255)
		for _ in range(16):
			ang = random.uniform(0, math.tau)
			speed = random.uniform(45, 180)
			vel = pygame.Vector2(math.cos(ang) * speed, math.sin(ang) * speed)
			self.particles.add(Particle(x, y, base_color, vel, random.uniform(0.3, 0.7), radius=random.randint(2, 4), gravity=55))

	def spawn_ring(self, x, y, color, amount):
		for idx in range(amount):
			ang = (math.tau / amount) * idx
			vel = pygame.Vector2(math.cos(ang) * 95, math.sin(ang) * 95)
			self.particles.add(Particle(x, y, color, vel, 0.5, radius=3))

	def update(self, dt):
		for structure in list(self.structures):
			structure.update(dt)
		for unit in list(self.units):
			unit.update(dt, self)
		for proj in list(self.projectiles):
			proj.update(dt, self)
		self.particles.update(dt)
		self.floating_texts.update(dt)

	def draw(self, surface, offset, fuente_small):
		for structure in self.structures:
			structure.render(surface, offset)
		for particle in self.particles:
			particle.render(surface, offset)
		for unit in sorted(self.units, key=lambda spr: spr.pos.y):
			unit.render(surface, offset)
		for proj in self.projectiles:
			proj.render(surface, offset)
		for txt in self.floating_texts:
			txt.render(surface, offset, fuente_small)


class CombatManager:
	UNIT_RESEARCH_MAP = {
		"lancero": "guardia",
		"berserker": "milicia",
		"arquero_hielo": "soldado",
		"campeon": "elite",
	}

	def __init__(self, scene):
		self.scene = scene
		self.estado = ESTADO_JUGADOR
		self.ronda = 1
		self.energia_max = 10
		self.energia = self.energia_max
		self.selected_card = None
		self.card_rects = {}
		self.btn_finalizar = pygame.Rect(scene.panel.right - 260, scene.panel.bottom - 92, 220, 44)
		self.flash_cards = 0.0
		self.anim_timer = 0.0
		self.unidades_investigadas = self._resolver_unidades_investigadas()
		self.cards_disponibles = [c for c in CARD_DEFS if self._card_desbloqueada(c.unit_id)]
		self.enemy_rounds = self._preparar_oleadas_enemigas()

	def _resolver_unidades_investigadas(self):
		unlocked = set()
		niveles_arbol = getattr(self.scene.logica, "niveles_arbol", {})
		niveles_tropas = niveles_arbol.get("TROPAS", {}) if isinstance(niveles_arbol, dict) else {}
		arbol_tropas = CATEGORIAS.get("TROPAS", {}).get("arbol", {})

		for nid, nivel in niveles_tropas.items():
			datos = arbol_tropas.get(nid, {})
			nivel = int(nivel)
			if nivel <= 0:
				continue
			if "efectos_por_nivel" in datos:
				for idx in range(min(nivel, len(datos["efectos_por_nivel"]))):
					ef = datos["efectos_por_nivel"][idx]
					unidad = ef.get("desbloquea_unidad") if isinstance(ef, dict) else None
					if unidad:
						unlocked.add(unidad)
			else:
				ef = datos.get("efecto", {})
				unidad = ef.get("desbloquea_unidad") if isinstance(ef, dict) else None
				if unidad:
					unlocked.add(unidad)

		gestor = getattr(self.scene.logica, "gestor_arboles", None)
		if gestor is not None and hasattr(gestor, "unidades_desbloqueadas"):
			unlocked.update(getattr(gestor, "unidades_desbloqueadas", set()))
		return unlocked

	def _card_desbloqueada(self, unit_id):
		req = self.UNIT_RESEARCH_MAP.get(unit_id)
		return req is None or req in self.unidades_investigadas

	def _preparar_oleadas_enemigas(self):
		rondas = {}
		for spawn in self.scene.level_data.spawns:
			ronda = max(1, int(spawn.get("time", 0) // 2.0) + 1)
			rondas.setdefault(ronda, []).append(spawn)
		return rondas

	def update(self, dt):
		self.flash_cards = max(0.0, self.flash_cards - dt * 2.8)
		if self.estado == ESTADO_ANIMACION:
			self.anim_timer = max(0.0, self.anim_timer - dt)
			if self.anim_timer <= 0:
				self._iniciar_ronda_jugador()
		self.scene.entities.particles.update(dt)
		self.scene.entities.floating_texts.update(dt)

	def click(self, pos):
		if self.scene.battle_over or self.estado != ESTADO_JUGADOR:
			return False

		if self.btn_finalizar.collidepoint(pos):
			self._ejecutar_ronda_enemiga()
			return True

		for card in self.cards_disponibles:
			rect = self.card_rects.get(card.unit_id)
			if rect and rect.collidepoint(pos):
				self.selected_card = card.unit_id if self.selected_card != card.unit_id else None
				return True

		if self.selected_card and self.scene.deploy_rect.collidepoint(pos):
			card = next((cd for cd in self.cards_disponibles if cd.unit_id == self.selected_card), None)
			if card is None:
				self.selected_card = None
				return False
			coste = int(math.ceil(card.coste))
			if self.energia < coste:
				self.flash_cards = 1.0
				return False
			lane_abs = min(self.scene.lanes_abs, key=lambda ly: abs(ly - pos[1]))
			x = clamp(pos[0], self.scene.deploy_rect.left + 22, self.scene.deploy_rect.right - 22)
			self.scene.entities.spawn_unit("ally", card.unit_id, x, lane_abs, 1.0)
			self.energia -= coste
			self.selected_card = None
			if self.energia <= 0:
				self.flash_cards = 1.0
			return True
		return False

	def _ejecutar_ronda_enemiga(self):
		self.estado = ESTADO_ENEMIGO
		self._spawn_enemigos_ronda()
		self._acciones_unidades("enemy")
		self._acciones_unidades("ally")
		self._ataques_torres_fin_ronda()
		self.estado = ESTADO_ANIMACION
		self.anim_timer = 0.42
		self.ronda += 1

	def _spawn_enemigos_ronda(self):
		for spawn in self.enemy_rounds.get(self.ronda, []):
			y = self.scene.field_rect.y + spawn["lane"]
			self.scene.entities.spawn_unit("enemy", spawn["unit_id"], self.scene.enemy_spawn_x, y, self.scene.level_data.escala)

	def _acciones_unidades(self, team):
		unidades = [u for u in self.scene.entities.units if not u.dead and u.team == team]
		for unit in unidades:
			target = self._seleccionar_objetivo(unit)
			if target is None:
				continue
			dist = unit.pos.distance_to(target.pos)
			if dist <= unit.range + 6:
				self.scene.entities.apply_damage(target, unit, unit.attack, unit.damage_type)
				if hasattr(target, "pos"):
					self.scene.entities.spawn_sparks(target.pos.x, target.pos.y, (255, 220, 120), 6)
			else:
				self._avanzar_tactico(unit, target)

	def _seleccionar_objetivo(self, unit):
		enemigos = [u for u in self.scene.entities.units if not u.dead and u.team != unit.team]
		if enemigos:
			enemigos.sort(key=lambda e: (e.hp, unit.pos.distance_to(e.pos)))
			if unit.team == "enemy" and self._camino_despejado_hacia_torre(unit):
				return self.scene.base_jugador
			return enemigos[0]
		return self.scene.base_enemiga if unit.team == "ally" else self.scene.base_jugador

	def _camino_despejado_hacia_torre(self, unit):
		for ally in self.scene.entities.units:
			if ally.dead or ally.team != "ally":
				continue
			misma_calle = abs(ally.pos.y - unit.pos.y) <= 38
			if misma_calle and ally.pos.x < unit.pos.x and (unit.pos.x - ally.pos.x) < 260:
				return False
		return True

	def _avanzar_tactico(self, unit, target):
		vec = pygame.Vector2(target.pos.x - unit.pos.x, target.pos.y - unit.pos.y)
		if vec.length_squared() <= 0:
			return
		step = min(unit.move_speed * 0.52, max(24.0, vec.length() - unit.range + 6))
		dir_vec = vec.normalize()
		unit.pos += dir_vec * step
		unit.pos.x = clamp(unit.pos.x, self.scene.field_rect.left + 45, self.scene.field_rect.right - 45)
		unit.pos.y = clamp(unit.pos.y, self.scene.field_rect.top + 35, self.scene.field_rect.bottom - 35)
		unit.rect.center = (int(unit.pos.x), int(unit.pos.y))

	def _ataques_torres_fin_ronda(self):
		self._ataque_torre(self.scene.base_jugador, "enemy")
		self._ataque_torre(self.scene.base_enemiga, "ally")

	def _ataque_torre(self, torre, target_team):
		if torre.hp <= 0:
			return
		area = 185
		targets = [u for u in self.scene.entities.units if not u.dead and u.team == target_team and u.pos.distance_to(torre.pos) <= area]
		if not targets:
			return
		targets.sort(key=lambda u: (u.hp, u.pos.distance_to(torre.pos)))
		objetivo = targets[0]
		self.scene.entities.apply_damage(objetivo, torre, max(18, torre.attack), "impacto")
		self.scene.entities.spawn_ring(objetivo.pos.x, objetivo.pos.y, (255, 120, 90), 10)

	def _iniciar_ronda_jugador(self):
		self.estado = ESTADO_JUGADOR
		self.energia = self.energia_max

	def draw(self, surface):
		self._draw_top(surface)
		self._draw_energy(surface)
		self._draw_cards(surface)
		self._draw_turn_button(surface)
		if self.scene.banner_text:
			self._draw_banner(surface)

	def _draw_top(self, surface):
		f = self.scene.font_small
		lvl = self.scene.level_data.nivel
		txt = self.scene.font_bold.render(f"Nivel {lvl}{'  BOSS' if self.scene.level_data.es_boss else ''}  |  Ronda {self.ronda}", True, COLOR_DORADO)
		surface.blit(txt, (self.scene.panel.x + 20, self.scene.panel.y + 14))

		txt_pb = f.render(f"Torre aliada: {int(self.scene.base_jugador.hp)}/{int(self.scene.base_jugador.max_hp)}", True, (140, 220, 255))
		txt_eb = f.render(f"Torre enemiga: {int(self.scene.base_enemiga.hp)}/{int(self.scene.base_enemiga.max_hp)}", True, (255, 140, 140))
		surface.blit(txt_pb, (self.scene.panel.x + 20, self.scene.panel.y + 42))
		surface.blit(txt_eb, (self.scene.panel.right - txt_eb.get_width() - 20, self.scene.panel.y + 42))

		estado_legible = {
			ESTADO_JUGADOR: "Turno Jugador",
			ESTADO_ENEMIGO: "Turno Enemigo",
			ESTADO_ANIMACION: "Resolviendo...",
		}.get(self.estado, "-")
		txt_turno = self.scene.font_small.render(estado_legible, True, (180, 195, 240))
		surface.blit(txt_turno, (self.scene.panel.centerx - txt_turno.get_width() // 2, self.scene.panel.y + 42))

	def _draw_energy(self, surface):
		x = self.scene.panel.x + 22
		y = self.scene.panel.bottom - 90
		w = 280
		h = 22
		pygame.draw.rect(surface, (20, 22, 36), (x, y, w, h), border_radius=11)
		ratio = clamp(self.energia / max(1, self.energia_max), 0.0, 1.0)
		fill_w = int(w * ratio)
		pygame.draw.rect(surface, (72, 185, 255), (x, y, fill_w, h), border_radius=11)
		if self.energia <= 0:
			pulse = int(60 + 30 * (math.sin(pygame.time.get_ticks() * 0.012) * 0.5 + 0.5))
			over = pygame.Surface((w, h), pygame.SRCALPHA)
			over.fill((pulse, 20, 20, 90))
			surface.blit(over, (x, y))
		pygame.draw.rect(surface, (220, 220, 240), (x, y, w, h), 2, border_radius=11)
		txt = self.scene.font_bold.render(f"ENERGIA {int(self.energia)}/{self.energia_max}", True, COLOR_TEXTO)
		surface.blit(txt, (x + 10, y - 28))

	def _draw_cards(self, surface):
		start_x = self.scene.panel.centerx - 270
		y = self.scene.panel.bottom - 92
		self.card_rects.clear()
		cards = self.cards_disponibles if self.cards_disponibles else CARD_DEFS
		for idx, card in enumerate(cards):
			rect = pygame.Rect(start_x + idx * 138, y, 120, 74)
			self.card_rects[card.unit_id] = rect
			seleccionado = (self.selected_card == card.unit_id)
			coste = int(math.ceil(card.coste))
			listo = self.estado == ESTADO_JUGADOR and self.energia >= coste and not self.scene.battle_over
			color_fondo = (22, 26, 42) if listo else (16, 18, 30)
			borde = card.color if seleccionado or listo else (90, 95, 118)
			pygame.draw.rect(surface, color_fondo, rect, border_radius=12)
			pygame.draw.rect(surface, borde, rect, 2, border_radius=12)
			pygame.draw.rect(surface, (*card.color[:3], 120), (rect.x + 8, rect.y + 8, 10, rect.height - 16), border_radius=5)

			txt_nombre = self.scene.font_small.render(card.nombre, True, COLOR_TEXTO)
			txt_coste = self.scene.font_bold.render(str(coste), True, COLOR_DORADO)
			surface.blit(txt_nombre, (rect.x + 24, rect.y + 10))
			surface.blit(txt_coste, (rect.right - txt_coste.get_width() - 10, rect.y + 8))

			if not listo:
				overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
				overlay.fill((30, 30, 34, 168))
				surface.blit(overlay, rect.topleft)
				txt_no = self.scene.font_small.render("Sin energia" if self.energia < coste else "Bloqueada", True, (210, 140, 140))
				surface.blit(txt_no, (rect.x + 20, rect.bottom - 24))
			else:
				txt_hint = self.scene.font_small.render("Click y despliega", True, (150, 170, 220))
				surface.blit(txt_hint, (rect.x + 24, rect.bottom - 24))

		if not self.cards_disponibles:
			msg = self.scene.font_small.render("No hay tropas investigadas en TROPAS", True, (255, 155, 125))
			surface.blit(msg, (self.scene.panel.centerx - msg.get_width() // 2, y - 26))

		if self.energia <= 0:
			gray = pygame.Surface((self.scene.panel.width - 60, 82), pygame.SRCALPHA)
			gray.fill((80, 80, 86, 80))
			surface.blit(gray, (self.scene.panel.x + 30, y - 4))

	def _draw_turn_button(self, surface):
		activo = self.estado == ESTADO_JUGADOR and not self.scene.battle_over
		col = (35, 136, 74) if activo else (70, 70, 84)
		pygame.draw.rect(surface, col, self.btn_finalizar, border_radius=12)
		pygame.draw.rect(surface, COLOR_DORADO, self.btn_finalizar, 2, border_radius=12)
		txt = self.scene.font_bold.render("FINALIZAR TURNO", True, (255, 255, 255))
		surface.blit(txt, (self.btn_finalizar.centerx - txt.get_width() // 2, self.btn_finalizar.centery - txt.get_height() // 2))

	def _draw_banner(self, surface):
		ov = pygame.Surface((self.scene.panel.width, 90), pygame.SRCALPHA)
		ov.fill((0, 0, 0, 150))
		surface.blit(ov, (self.scene.panel.x, self.scene.panel.centery - 45))
		txt = self.scene.font_title.render(self.scene.banner_text, True, self.scene.banner_color)
		surface.blit(txt, (self.scene.panel.centerx - txt.get_width() // 2, self.scene.panel.centery - txt.get_height() // 2))


class BattleScene:
	def __init__(self, logica, level_data, progress):
		self.logica = logica
		self.level_data = level_data
		self.progress = progress
		self.panel = pygame.Rect(60, 60, 1080, 650)
		self.field_rect = pygame.Rect(self.panel.x + 20, self.panel.y + 80, self.panel.width - 40, 470)
		self.deploy_rect = pygame.Rect(self.field_rect.x + 10, self.field_rect.y, int(self.field_rect.width * 0.35), self.field_rect.height)
		self.enemy_spawn_x = self.field_rect.right - 70
		self.lanes_abs = [self.field_rect.y + lane for lane in LANES_Y]
		self.font_title = pygame.font.SysFont("Arial", 34, bold=True)
		self.font_bold = pygame.font.SysFont("Arial", 20, bold=True)
		self.font_small = pygame.font.SysFont("Arial", 16)
		self.font_tiny = pygame.font.SysFont("Arial", 13)
		self.shake = ScreenShake()
		self.entities = EntityManager(self, self.field_rect)
		self.base_jugador = BaseCore("ally", self.field_rect.left + 70, self.field_rect.centery, self.level_data.base_jugador_hp)
		self.base_enemiga = BaseCore("enemy", self.field_rect.right - 70, self.field_rect.centery, self.level_data.base_enemiga_hp)
		self.base_jugador.attack = 46
		self.base_jugador.range = 185
		self.base_enemiga.attack = 42
		self.base_enemiga.range = 185
		self.entities.add_structure(self.base_jugador)
		self.entities.add_structure(self.base_enemiga)
		self.combat = CombatManager(self)
		self.last_ticks = None
		self.battle_over = False
		self.banner_text = ""
		self.banner_color = COLOR_TEXTO
		self.rect_cerrar = None
		self.victoria_aplicada = False
		self.flash_torre_timer = 0.0

	def disparar_flash_torre(self, intensidad=1.0):
		self.flash_torre_timer = max(self.flash_torre_timer, clamp(0.12 + intensidad * 0.20, 0.1, 0.45))
		self.shake.add(4 + int(intensidad * 4), 0.18)

	def manejar_eventos(self, evento):
		if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
			return "MAPA"
		if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
			if self.rect_cerrar and self.rect_cerrar.collidepoint(evento.pos):
				return "MAPA"
			if self.combat.click(evento.pos):
				return None
		if evento.type == EVENTO_UNIDAD_MUERTA:
			if evento.dict.get("is_structure"):
				if evento.dict.get("team") == "enemy":
					pygame.event.post(pygame.event.Event(EVENTO_VICTORIA_BATALLA))
				elif evento.dict.get("team") == "ally":
					pygame.event.post(pygame.event.Event(EVENTO_DERROTA_BATALLA))
		if evento.type == EVENTO_VICTORIA_BATALLA and not self.battle_over:
			self._cerrar_batalla(True)
		if evento.type == EVENTO_DERROTA_BATALLA and not self.battle_over:
			self._cerrar_batalla(False)
		return None

	def dibujar(self, pantalla):
		ahora = pygame.time.get_ticks() / 1000.0
		if self.last_ticks is None:
			dt = 1 / 60
		else:
			dt = clamp(ahora - self.last_ticks, 0.0, 0.05)
		self.last_ticks = ahora
		self._update(dt)

		ov = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
		ov.fill((0, 0, 0, 170))
		pantalla.blit(ov, (0, 0))

		offset = self.shake.offset()
		panel = self.panel.move(offset)
		field = self.field_rect.move(offset)
		deploy = self.deploy_rect.move(offset)

		pygame.draw.rect(pantalla, COLOR_PANEL, panel, border_radius=18)
		pygame.draw.rect(pantalla, COLOR_BORDE, panel, 3, border_radius=18)
		barra = pygame.Rect(panel.x + 3, panel.y + 3, panel.width - 6, 60)
		pygame.draw.rect(pantalla, (15, 18, 42), barra, border_radius=15)
		titulo = self.font_title.render("CONQUISTA", True, COLOR_DORADO)
		pantalla.blit(titulo, (panel.centerx - titulo.get_width() // 2, panel.y + 12))

		self.rect_cerrar = pygame.Rect(panel.right - 44, panel.y + 10, 34, 34)
		pygame.draw.rect(pantalla, (170, 40, 40), self.rect_cerrar, border_radius=7)
		txt_x = self.font_bold.render("X", True, (255, 255, 255))
		pantalla.blit(txt_x, (self.rect_cerrar.centerx - txt_x.get_width() // 2, self.rect_cerrar.centery - txt_x.get_height() // 2))

		pygame.draw.rect(pantalla, COLOR_CAMPO, field, border_radius=14)
		pygame.draw.rect(pantalla, (60, 75, 120), field, 2, border_radius=14)
		pygame.draw.rect(pantalla, (22, 55, 90), deploy, 2, border_radius=12)
		deploy_txt = self.font_tiny.render("Zona de despliegue", True, (120, 210, 255))
		pantalla.blit(deploy_txt, (deploy.x + 8, deploy.y + 8))

		radio_torre = 185
		for base, col in ((self.base_jugador, (80, 170, 240)), (self.base_enemiga, (240, 120, 120))):
			ov = pygame.Surface((radio_torre * 2 + 8, radio_torre * 2 + 8), pygame.SRCALPHA)
			pygame.draw.circle(ov, (*col, 30), (radio_torre + 4, radio_torre + 4), radio_torre)
			pantalla.blit(ov, (int(base.pos.x - radio_torre + offset[0] - 4), int(base.pos.y - radio_torre + offset[1] - 4)))
			pygame.draw.circle(pantalla, (*col, 120), (int(base.pos.x + offset[0]), int(base.pos.y + offset[1])), radio_torre, 1)

		for lane_y in self.lanes_abs:
			py = lane_y + offset[1]
			pygame.draw.line(pantalla, COLOR_LINEA, (field.x + 12, py), (field.right - 12, py), 1)
		pygame.draw.line(pantalla, (80, 120, 190), (field.centerx, field.y + 10), (field.centerx, field.bottom - 10), 1)

		self.entities.draw(pantalla, offset, self.font_small)
		self.combat.draw(pantalla)

		if self.flash_torre_timer > 0:
			alpha = int(115 * clamp(self.flash_torre_timer / 0.35, 0.0, 1.0))
			flash = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
			flash.fill((255, 35, 35, alpha))
			pantalla.blit(flash, (0, 0))

	def _update(self, dt):
		self.shake.update(dt)
		self.flash_torre_timer = max(0.0, self.flash_torre_timer - dt)
		self.combat.update(dt)
		if self.battle_over:
			return

		if self.combat.ronda > max(self.combat.enemy_rounds.keys(), default=0) and not any(u.team == "enemy" and not u.dead for u in self.entities.units) and self.base_enemiga.hp > 0:
			pygame.event.post(pygame.event.Event(EVENTO_VICTORIA_BATALLA))

	def _cerrar_batalla(self, victoria):
		self.battle_over = True
		if victoria and not self.victoria_aplicada:
			self.victoria_aplicada = True
			self.banner_text = "VICTORIA"
			self.banner_color = (120, 255, 140)
			self.progress.marcar_victoria(self.level_data.nivel)
			self.logica.dinero += self.level_data.recompensa_oro
			for recurso, cantidad in self.level_data.recompensa_recursos.items():
				if recurso in self.logica.recursos:
					limite = {
						"comida": getattr(self.logica, "max_comida", self.logica.recursos[recurso] + cantidad),
						"agua": getattr(self.logica, "max_agua", self.logica.recursos[recurso] + cantidad),
						"electricidad": getattr(self.logica, "max_energia", self.logica.recursos[recurso] + cantidad),
					}.get(recurso, self.logica.recursos[recurso] + cantidad)
					self.logica.recursos[recurso] = min(limite, self.logica.recursos[recurso] + cantidad)
			self.logica.noticias.append({"txt": f"Conquista superada: Nivel {self.level_data.nivel}", "tipo": "LOGRO"})
			if hasattr(self.logica, "guardar_partida"):
				self.logica.guardar_partida()
		elif not victoria:
			self.banner_text = "DERROTA"
			self.banner_color = (255, 120, 120)
			self.logica.noticias.append({"txt": f"Has caido en el nivel {self.level_data.nivel}", "tipo": "CRITICO"})


class EscenaCombate:
	def __init__(self, logica):
		self.logica = logica
		self.progress = ProgressManager()
		self.active_battle = None
		self.selected_level = self.progress.data.get("last_selected", 1)
		self.font_title = pygame.font.SysFont("Arial", 30, bold=True)
		self.font_bold = pygame.font.SysFont("Arial", 18, bold=True)
		self.font_small = pygame.font.SysFont("Arial", 15)
		self.font_tiny = pygame.font.SysFont("Arial", 13)
		self.rect_cerrar = None
		self.rect_iniciar = None
		self.level_rects = {}

	def dibujar(self, pantalla):
		if self.active_battle:
			self.active_battle.dibujar(pantalla)
			return

		ancho, alto = pantalla.get_size()
		panel = pygame.Rect(ancho // 2 - 520, alto // 2 - 330, 1040, 660)
		ov = pygame.Surface((ancho, alto), pygame.SRCALPHA)
		ov.fill((0, 0, 0, 185))
		pantalla.blit(ov, (0, 0))

		pygame.draw.rect(pantalla, COLOR_PANEL, panel, border_radius=18)
		pygame.draw.rect(pantalla, COLOR_BORDE, panel, 3, border_radius=18)
		titulo = self.font_title.render("CAMPANA DE CONQUISTA", True, COLOR_DORADO)
		pantalla.blit(titulo, (panel.centerx - titulo.get_width() // 2, panel.y + 14))

		self.rect_cerrar = pygame.Rect(panel.right - 44, panel.y + 10, 34, 34)
		pygame.draw.rect(pantalla, (170, 40, 40), self.rect_cerrar, border_radius=7)
		txt_x = self.font_bold.render("X", True, (255, 255, 255))
		pantalla.blit(txt_x, (self.rect_cerrar.centerx - txt_x.get_width() // 2, self.rect_cerrar.centery - txt_x.get_height() // 2))

		info = self.font_small.render("50 niveles | Boss cada 10 | progreso automatico", True, (180, 195, 240))
		pantalla.blit(info, (panel.centerx - info.get_width() // 2, panel.y + 54))

		grid = pygame.Rect(panel.x + 30, panel.y + 100, 660, 520)
		sidebar = pygame.Rect(panel.x + 720, panel.y + 100, 290, 520)
		pygame.draw.rect(pantalla, (16, 22, 40), grid, border_radius=14)
		pygame.draw.rect(pantalla, (16, 22, 40), sidebar, border_radius=14)
		pygame.draw.rect(pantalla, COLOR_BORDE, grid, 1, border_radius=14)
		pygame.draw.rect(pantalla, COLOR_BORDE, sidebar, 1, border_radius=14)

		self.level_rects.clear()
		cols = 10
		step_x = grid.width // cols
		step_y = grid.height // 5
		for nivel in range(1, 51):
			c = (nivel - 1) % cols
			r = (nivel - 1) // cols
			cx = grid.x + c * step_x + step_x // 2
			cy = grid.y + r * step_y + step_y // 2
			rect = pygame.Rect(cx - 22, cy - 22, 44, 44)
			self.level_rects[nivel] = rect
			desbloq = self.progress.nivel_desbloqueado(nivel)
			ganado = nivel in self.progress.data.get("victorias", [])
			boss = (nivel % 10 == 0)
			color = (90, 90, 110)
			borde = (120, 120, 140)
			if desbloq:
				color = (70, 95, 140)
				borde = COLOR_DORADO if boss else (130, 210, 255)
			if ganado:
				color = (70, 135, 90)
				borde = (120, 255, 160)
			if nivel == self.selected_level:
				borde = (255, 255, 255)
			pygame.draw.circle(pantalla, (0, 0, 0), (cx + 3, cy + 4), 22)
			pygame.draw.circle(pantalla, color, (cx, cy), 22)
			pygame.draw.circle(pantalla, borde, (cx, cy), 22, 2)
			txt = self.font_tiny.render(str(nivel), True, COLOR_TEXTO if desbloq else (160, 160, 170))
			pantalla.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
			if boss:
				pygame.draw.circle(pantalla, (255, 120, 90), (cx + 14, cy - 14), 6)

		datos = LevelManager.crear_nivel(self.selected_level)
		lbl = self.font_bold.render(f"Nivel {self.selected_level}", True, COLOR_DORADO)
		pantalla.blit(lbl, (sidebar.x + 18, sidebar.y + 16))
		if datos.es_boss:
			boss_lbl = self.font_small.render("Batalla contra BOSS", True, (255, 120, 90))
			pantalla.blit(boss_lbl, (sidebar.x + 18, sidebar.y + 42))

		lineas = [
			f"Recompensa: ${datos.recompensa_oro:,}",
			f"Comida +{datos.recompensa_recursos['comida']}",
			f"Agua +{datos.recompensa_recursos['agua']}",
			f"Energia +{datos.recompensa_recursos['electricidad']}",
			f"Base enemiga: {datos.base_enemiga_hp}",
			f"Oleadas: {len(datos.spawns)} spawns",
		]
		yy = sidebar.y + 86
		for linea in lineas:
			txt = self.font_small.render(linea, True, COLOR_TEXTO)
			pantalla.blit(txt, (sidebar.x + 18, yy))
			yy += 28

		hint1 = self.font_small.render("Cartas disponibles", True, (180, 195, 240))
		pantalla.blit(hint1, (sidebar.x + 18, yy + 10))
		yy += 42
		for card in CARD_DEFS:
			txt = self.font_small.render(f"- {card.nombre} | coste {int(card.coste)}", True, card.color)
			pantalla.blit(txt, (sidebar.x + 18, yy))
			yy += 24

		self.rect_iniciar = pygame.Rect(sidebar.x + 18, sidebar.bottom - 64, sidebar.width - 36, 42)
		desbloq = self.progress.nivel_desbloqueado(self.selected_level)
		col = (30, 120, 60) if desbloq else (70, 70, 70)
		pygame.draw.rect(pantalla, col, self.rect_iniciar, border_radius=10)
		pygame.draw.rect(pantalla, COLOR_DORADO, self.rect_iniciar, 2, border_radius=10)
		txt_btn = self.font_bold.render("INICIAR BATALLA" if desbloq else "NIVEL BLOQUEADO", True, (255, 255, 255))
		pantalla.blit(txt_btn, (self.rect_iniciar.centerx - txt_btn.get_width() // 2, self.rect_iniciar.centery - txt_btn.get_height() // 2))

	def manejar_eventos(self, evento):
		if self.active_battle:
			resultado = self.active_battle.manejar_eventos(evento)
			if resultado == "MAPA":
				self.active_battle = None
				return None
			return resultado

		if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
			return "CIUDAD"

		if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
			pos = evento.pos
			if self.rect_cerrar and self.rect_cerrar.collidepoint(pos):
				return "CIUDAD"
			for nivel, rect in self.level_rects.items():
				if rect.collidepoint(pos):
					self.selected_level = nivel
					self.progress.seleccionar(nivel)
					return None
			if self.rect_iniciar and self.rect_iniciar.collidepoint(pos) and self.progress.nivel_desbloqueado(self.selected_level):
				self.active_battle = BattleScene(self.logica, LevelManager.crear_nivel(self.selected_level), self.progress)
		return None
