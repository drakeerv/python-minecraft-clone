import math
import collider
import glm

FLYING_ACCEL  = glm.vec3(0, 0, 0)
GRAVITY_ACCEL = glm.vec3(0, -32, 0)

# these values all come (losely) from Minecraft, but are multiplied by 20 (since Minecraft runs at 20 TPS)

FRICTION  = glm.vec3(20, 20, 20)

DRAG_FLY  = glm.vec3(5, 5, 5)
DRAG_JUMP = glm.vec3(1.8, 0, 1.8)
DRAG_FALL = glm.vec3(1.8, 0.4, 1.8)

class Entity:
	def __init__(self, world):
		self.world = world

		# physical variables

		self.jump_height = 1.25
		self.flying = False

		self.position = glm.vec3(0, 80, 0)
		self.rotation = glm.vec2(-math.tau / 4, 0)

		self.old_position = glm.vec3(self.position)
		self.old_rotation = glm.vec2(self.rotation)

		self.step = 1

		self.velocity = glm.vec3(0, 0, 0)
		self.accel = glm.vec3(0, 0, 0)

		# collision variables

		self.width = 0.6
		self.height = 1.8

		self.collider = collider.Collider()
		self.grounded = False

	def update_collider(self):
		x, y, z = self.position

		self.collider.x1 = x - self.width / 2
		self.collider.x2 = x + self.width / 2

		self.collider.y1 = y
		self.collider.y2 = y + self.height

		self.collider.z1 = z - self.width / 2
		self.collider.z2 = z + self.width / 2

	def teleport(self, pos: glm.vec3):
		self.position = pos
		self.velocity *= 0

	def jump(self, height: float | None = None):
		# obviously, we can't initiate a jump while in mid-air

		if not self.grounded:
			return

		if height is None:
			height = self.jump_height

		self.velocity[1] = math.sqrt(2 * height * -GRAVITY_ACCEL[1])

	@property
	def friction(self) -> glm.vec3:
		if self.flying:
			return DRAG_FLY

		elif self.grounded:
			return FRICTION

		elif self.velocity[1] > 0:
			return DRAG_JUMP

		return DRAG_FALL

	def update(self, delta_time: float):
		self.step = 1
		self.old_position = glm.vec3(self.position)
	
		# apply input acceleration, and adjust for friction/drag

		self.velocity = self.velocity + self.accel * self.friction * delta_time
		self.accel = glm.vec3(0, 0, 0)

		# compute collisions

		self.update_collider()
		self.grounded = False

		for _ in range(3):
			adjusted_velocity = self.velocity * delta_time
			vx, vy, vz = adjusted_velocity

			# find all the blocks we could potentially be colliding with
			# this step is known as "broad-phasing"

			step_x = 1 if vx > 0 else -1
			step_y = 1 if vy > 0 else -1
			step_z = 1 if vz > 0 else -1

			steps_xz = int(self.width / 2)
			steps_y  = int(self.height)

			x, y, z = map(int, self.position)
			cx, cy, cz = map(int, self.position + adjusted_velocity)

			potential_collisions = []

			for i in range(x - step_x * (steps_xz + 1), cx + step_x * (steps_xz + 2), step_x):
				for j in range(y - step_y * (steps_y + 2), cy + step_y * (steps_y + 3), step_y):
					for k in range(z - step_z * (steps_xz + 1), cz + step_z * (steps_xz + 2), step_z):
						pos = (i, j, k)
						num = self.world.get_block_number(pos)

						if not num:
							continue

						for _collider in self.world.block_types[num].colliders:
							entry_time, normal = self.collider.collide(_collider + pos, adjusted_velocity)

							if normal is None:
								continue

							potential_collisions.append((entry_time, normal))

			# get first collision

			if not potential_collisions:
				break

			entry_time, normal = min(potential_collisions, key = lambda x: x[0])
			entry_time -= 0.001

			self.velocity -= normal * glm.dot(normal, self.velocity)
			self.position += self.velocity * entry_time * glm.abs(normal)

			if normal[1] == 1:
				self.grounded = True

		self.position += self.velocity * delta_time

		# apply gravity acceleration

		gravity = (GRAVITY_ACCEL, FLYING_ACCEL)[self.flying]
		self.velocity += gravity * delta_time

		# apply friction/drag

		self.velocity -= glm.vec3([min(v * f * delta_time, v, key=abs) for v, f in zip(self.velocity, self.friction)])

		# make sure we can rely on the entity's collider outside of this function

		self.update_collider()