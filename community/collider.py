import math
import glm
from typing import Self

class Collider:
	def __init__(self, pos1: glm.vec3 = glm.vec3(0, 0, 0), pos2: glm.vec3 = glm.vec3(0, 0, 0)):
		# pos1: position of the collider vertex in the -X, -Y, -Z direction
		# pos2: position of the collider vertex in the +X, +Y, +Z direction

		self.x1, self.y1, self.z1 = pos1
		self.x2, self.y2, self.z2 = pos2
	
	def __add__(self, pos: glm.vec3) -> Self:
		x, y, z = pos

		return Collider(
			(self.x1 + x, self.y1 + y, self.z1 + z),
			(self.x2 + x, self.y2 + y, self.z2 + z)
		)
	
	def __and__(self, collider: Self) -> bool:
		x = min(self.x2, collider.x2) - max(self.x1, collider.x1)
		y = min(self.y2, collider.y2) - max(self.y1, collider.y1)
		z = min(self.z2, collider.z2) - max(self.z1, collider.z1)

		return x > 0 and y > 0 and z > 0
	
	def collide(self, collider: Self, velocity: glm.vec3) -> tuple[int, glm.vec3 | None]:
		# self: the dynamic collider, which moves
		# collider: the static collider, which stays put

		no_collision = 1, None

		# find entry & exit times for each axis

		vx, vy, vz = velocity

		time = lambda x, y: x / y if y else (-math.inf if x > 0 else math.inf)

		x_entry = time(collider.x1 - self.x2 if vx > 0 else collider.x2 - self.x1, vx)
		x_exit  = time(collider.x2 - self.x1 if vx > 0 else collider.x1 - self.x2, vx)

		y_entry = time(collider.y1 - self.y2 if vy > 0 else collider.y2 - self.y1, vy)
		y_exit  = time(collider.y2 - self.y1 if vy > 0 else collider.y1 - self.y2, vy)

		z_entry = time(collider.z1 - self.z2 if vz > 0 else collider.z2 - self.z1, vz)
		z_exit  = time(collider.z2 - self.z1 if vz > 0 else collider.z1 - self.z2, vz)

		# make sure we actually got a collision

		if x_entry < 0 and y_entry < 0 and z_entry < 0:
			return no_collision

		if x_entry > 1 or y_entry > 1 or z_entry > 1:
			return no_collision
		
		# on which axis did we collide first?

		entry = max(x_entry, y_entry, z_entry)
		exit_ = min(x_exit,  y_exit,  z_exit )

		if entry > exit_:
			return no_collision
		
		# find normal of surface we collided with

		nx = (0, -1 if vx > 0 else 1)[entry == x_entry]
		ny = (0, -1 if vy > 0 else 1)[entry == y_entry]
		nz = (0, -1 if vz > 0 else 1)[entry == z_entry]

		return entry, glm.vec3(nx, ny, nz)