import pyglet.media


class MusicPlayer(pyglet.media.Player):
	def __init__(self):
		super().__init__()

		self.standby = False
		self.next_time = 0
