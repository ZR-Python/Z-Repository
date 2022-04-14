import pygame
import random
from playsound import playsound

pygame.init()

BLACK = (0,0,0)
RED = (255, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
BORDER = (77, 77, 77)
BUTTON_GREY = (255, 44, 53)
BUTTON_GREEN = (0, 153, 0)
ACTIVE_GREEN = (0, 53, 0)
TEXT_BOX = (255,165,53)
TEXT_COLOR = (135,18,130)
game_over = False
title_screen = True
victory = False
zombie_speed = 500

wave_two_started = False
wave_three_started = False
wave_three_rotating_sides = 0

screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Zombie Typing")
FPS = 60
number_of_zombies = 20

level_wave = 1
current_stage = 0

clock = pygame.time.Clock()
run = True
font = pygame.font.Font("Zombie.ttf", 36)
button_font = pygame.font.SysFont("comicsans", 30)
gunshot_words = ""
backspace_delay = 4
gunshot_word_display = font.render(gunshot_words, True, RED)
zombie_words = []
zombie_adjectives = []
zombie_nouns = []
with open("zombie_normal.txt", "r") as f:
    zombie_words = f.readlines()
zombie_words = [line.strip() for line in zombie_words]
f.close()

with open("ZombieAdjectives.txt", "r") as f:
    zombie_adjectives = f.readlines()
zombie_adjectives = [line.strip() for line in zombie_adjectives]
f.close()

with open("ZombieNouns.txt", "r") as f:
    zombie_nouns = f.readlines()
zombie_nouns = [line.strip() for line in zombie_nouns]
f.close()

class Background(pygame.sprite.Sprite):
	def __init__(self, image):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.rect = self.image.get_rect()
		self.rect.center = (600, 400)

class Button(pygame.sprite.Sprite):
	def __init__(self, text):
		self.text = text
		self.rect = pygame.Rect(0,0, len(text)*35, 70)
		self.color = BUTTON_GREY
		self.colinked = False
		self.active = False
		self.spawn_number = 0
		self.zombie_speed = 0
	def draw(self):
		pygame.draw.rect(screen, self.color, (self.rect))
		display_text = font.render(self.text, True, TEXT_COLOR)
		screen.blit(display_text, (self.rect.x+ len(self.text)*6, self.rect.y+15))
	def update(self):
		if (self.rect.collidepoint(pygame.mouse.get_pos())):
			if self.active == False:
				self.color = BUTTON_GREEN
		else:
			if self.active == False:
				self.color = BUTTON_GREY


class Player(pygame.sprite.Sprite):
	def __init__(self, image):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.original_image = self.image
		self.bang = pygame.image.load("Phoebe_Bang.png")
		self.walk_a_image = pygame.image.load("Phoebe_Walk_A.png")
		self.walk_b_image = pygame.image.load("Phoebe_Walk_B.png")
		self.new_l_original_image = self.image
		self.new_l_bang = pygame.image.load("Phoebe_Bang.png")
		self.new_l_walk_a_image = pygame.image.load("Phoebe_Walk_A.png")
		self.new_l_walk_b_image = pygame.image.load("Phoebe_Walk_B.png")
		self.rect = self.image.get_rect()
		self.health = 100
		self.health_bar_name = "HEALTH: "
		self.kill_count = 0
		self.moving = 25
		self.bang_timer = 0
		self.move_to_new_spot = 0
		self.facing_right = True
		self.move_timer = 0
		self.hitbox = pygame.Rect(self.rect.center[0], self.rect.center[1], 100, 100)
	def new_level(self):
		self.image = self.new_l_original_image
		self.original_image = self.new_l_original_image
		self.bang = self.new_l_bang
		self.walk_a_image = self.new_l_walk_a_image
		self.walk_b_image = self.new_l_walk_b_image
		self.health = 100
	def display_health(self):
		pygame.draw.rect(screen, RED, pygame.Rect(870, 725, self.health * 3, 25))
		kill_count_display = font.render(str(self.kill_count), True, RED)
		screen.blit(kill_count_display, (900, 760))
	def damage(self, damage):
		self.health -= damage
	def get_health(self):
		return self.health
	def flip_sides(self):
		self.image = pygame.transform.flip(self.image, True, False)
		self.original_image = pygame.transform.flip(self.original_image, True, False)
		self.bang = pygame.transform.flip(self.bang, True, False)
		self.walk_a_image = pygame.transform.flip(self.walk_a_image, True, False)
		self.walk_b_image = pygame.transform.flip(self.walk_a_image, True, False)

	def new_wave(self):
		if (self.move_to_new_spot > 0):
			self.move_to_new_spot -= 1
			self.rect.center = (self.rect.center[0] + 10, self.rect.center[1])
			self.move_timer += 1
			if self.move_to_new_spot == 0:
				self.flip_sides()
				self.facing_right = False
		if (self.move_to_new_spot < 0):
			self.move_to_new_spot += 1
			self.rect.center = (self.rect.center[0] - 10, self.rect.center[1])
			self.move_timer += 1
			if self.move_to_new_spot == 0:
				self.move_timer = 0
				self.image = self.original_image
				self.flip_sides()
				self.facing_right = True


Phoebe = Player("Phoebe_Right.png")
#Phoebe.image = pygame.transform.flip(Phoebe.image, True, False)

class Zombie(pygame.sprite.Sprite):
	def __init__(self, image, phrase):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.original_image = self.image
		self.shot_image = pygame.image.load("Zombie_Shot.png")
		self.feast_image = pygame.image.load("Zombie_Feast.png")
		self.feast_head_back_image = pygame.image.load("Zombie_Feast_Head_Back.png")
		self.walk_a_image = pygame.image.load("Zombie_Walk_A.png")
		self.rect = self.image.get_rect()
		self.alive = True
		self.run_speed = 500
		self.eat_timer = 100
		self.phrase = phrase
		self.phrase_length = len(self.phrase)
		self.eating = False
		self.stacked = False
		self.stack_dy = 0
		self.stacking = 0
		self.spawn_timer = 0
		self.wave_three_status = 0
		self.remain_on_screen = 36
		self.move_timer = 0
	def load_fat(self):
		self.shot_image = pygame.image.load("Fat Zombie Shot.png")
		self.feast_image = pygame.image.load("Fat Zombie Eat_A.png")
		self.feast_head_back_image = pygame.image.load("Fat Zombie Eat_B.png")
		self.walk_a_image = pygame.image.load("Fat Zombie Walk.png")	
	def get_rect(self):
		return self.rect
	def display_text_bubble(self):
		zombie_word_display = font.render(self.phrase, True, TEXT_COLOR)
		pygame.draw.rect(screen, TEXT_BOX, pygame.Rect(self.rect.x-5, self.rect.y-75, self.phrase_length * 20, 60))
		pygame.draw.rect(screen, BORDER, (self.rect.x-5, self.rect.y-75, self.phrase_length*20, 60), 4, border_radius=1)
		screen.blit(zombie_word_display, (self.rect.x, self.rect.y - 65))
	def flip_sides(self):
		self.original_image = pygame.transform.flip(self.original_image, True, False)
		self.walk_a_image = pygame.transform.flip(self.walk_a_image, True, False)
		self.feast_image = pygame.transform.flip(self.feast_image, True, False)
		self.feast_head_back_image = pygame.transform.flip(self.feast_head_back_image, True, False)
		self.image = pygame.transform.flip(self.image, True, False)
	def animation(self):
		if (self.move_timer % 12 == 0):
			temp = self.image
			self.image = self.walk_a_image
			self.walk_a_image = temp
	def eat(self):
		global run
		global game_over
		if self.eating == True:
			if self.eat_timer == 100:
				self.image = self.feast_image
				Phoebe.damage(10)
				if (Phoebe.get_health() == 0):
					run = False
					game_over = True
				self.eat_timer = 0
			else:
				self.eat_timer += 1
				if (self.eat_timer > 35):
					self.image = self.feast_head_back_image
				if (self.eat_timer > 70):
					self.image = self.original_image
				#EAT


	def move_forward(self):
		global game_over
		global run
		global level_wave
		if (abs(Phoebe.rect.center[0] - self.rect.center[0]) > 30):
			if (level_wave == 1):
				self.rect.center = (self.rect.center[0] - (5*self.run_speed), self.rect.center[1])
			if (level_wave == 2):
				self.rect.center = (self.rect.center[0] + (5*self.run_speed), self.rect.center[1])
			if (level_wave == 3):
				if (self.wave_three_status == 1):
					self.rect.center = (self.rect.center[0] - (5*self.run_speed), self.rect.center[1])
				elif (self.wave_three_status == 2):
					self.rect.center = (self.rect.center[0] + (5*self.run_speed), self.rect.center[1])
			self.move_timer += self.run_speed
			self.animation()
		else:
			self.eating = True


Castle_Level = Background("Castle.png")
Bridge_Level = Background("Bridge_Background.png")
Forest_Level = Background("Forest.png")
Game_Levels = [Forest_Level, Bridge_Level, Castle_Level]
Phoebe_Spawns = [(300,480),(300,400),(300,480)]
Zombie_Spawns = [(1060, 480),(1060, 400),(1060, 480)]
Zombie_Left_Spawns = [(200, 480), (200, 400), (200, 480)]
UI = Background("zz.png")
UI.rect.center = (600, 760)
Game_Title = Background("Game_Title.png")
Title_Background = Background("Title Background.png")
Title_Background.rect.center = (600, 400)
Game_Title.rect.center = (600, 200)
Play_Button = Button("START GAME")
Play_Button.rect.center = (600, 400)
Title_Sprites = pygame.sprite.Group()
Title_Sprites.add(Title_Background , Game_Title)
Title_Buttons = [Play_Button]
Few_Zombies = Button("Few")
Some_Zombies = Button("Some")
Some_Zombies.active = True
Some_Zombies.color = ACTIVE_GREEN
Many_Zombies = Button("Many")
Number_of_Zombies_Buttons = [Few_Zombies, Some_Zombies, Many_Zombies]
Slow_Speed = Button("Slow")
Medium_Speed = Button("Medium")
Medium_Speed.active = True
Medium_Speed.color = ACTIVE_GREEN
Intense_Speed = Button("Intense")
Zombie_Speed_Buttons = [Slow_Speed, Medium_Speed, Intense_Speed]
for button in Number_of_Zombies_Buttons:
	button.colinked = True
for button in Zombie_Speed_Buttons:
	button.colinked = True
Few_Zombies.rect.center = (300, 550)
Some_Zombies.rect.center = (600, 550)
Many_Zombies.rect.center = (900, 550)
Slow_Speed.rect.center = (300, 700)
Medium_Speed.rect.center = (600, 700)
Intense_Speed.rect.center = (900, 700)
Few_Zombies.spawn_number = 3
Some_Zombies.spawn_number = 8
Many_Zombies.spawn_number = 13
Slow_Speed.zombie_speed = 0.5
Medium_Speed.zombie_speed = 1
Intense_Speed.zombie_speed = 1.5
Backgrounds = pygame.sprite.Group()
Backgrounds.add(Forest_Level)
Enemy_List = []
Characters = pygame.sprite.Group()
Enemies = pygame.sprite.Group()
Characters.add(Phoebe, UI)
Enemies.add()
Phoebe.rect.center = (300, 480)

while (title_screen):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			title_screen = False
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			if (Play_Button.rect.collidepoint(pygame.mouse.get_pos())):
				title_screen = False
				for button in Number_of_Zombies_Buttons:
					if button.active == True:
						number_of_zombies = button.spawn_number
						level_spawn_timer = number_of_zombies * 60 # Desired Zombies * Spawn Rate * Level Wave??
				for button in Zombie_Speed_Buttons:
					if button.active == True:
						zombie_speed = button.zombie_speed
			for button in Number_of_Zombies_Buttons:
				if (button.rect.collidepoint(pygame.mouse.get_pos())):
					button.active = True
					button.color = ACTIVE_GREEN
					for other_button in Number_of_Zombies_Buttons:
						if button != other_button:
							other_button.active = False
							other_button.color = BUTTON_GREY
			for button in Zombie_Speed_Buttons:
				if (button.rect.collidepoint(pygame.mouse.get_pos())):
					button.active = True
					button.color = ACTIVE_GREEN
					for other_button in Zombie_Speed_Buttons:
						if button != other_button:
							other_button.active = False
							other_button.color = BUTTON_GREY
	screen.fill(BLACK)
	Title_Sprites.update()
	Title_Sprites.draw(screen)
	for button in Title_Buttons:
		button.update()
		button.draw()
	number_of_zombies_option = font.render("Amount of Zombies: ", True, RED)
	screen.blit(number_of_zombies_option, (450, 450))
	zombie_speed_option = font.render("Zombie Speed: ", True, RED)
	screen.blit(zombie_speed_option, (450, 600))
	for button in Number_of_Zombies_Buttons:
		button.update()
		button.draw()
	for button in Zombie_Speed_Buttons:
		button.update()
		button.draw()
	pygame.display.flip()
	clock.tick(FPS)
while (run):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				for zombie in Enemies:
					gunshot_words = ""
					gunshot_word_display = font.render(gunshot_words, True, RED)
			if event.key == pygame.K_BACKSPACE:
				pass
			else:
				if event.unicode.islower() or event.unicode.isupper() or event.unicode.isdigit() or event.unicode == ',' or event.unicode == "?" or event.unicode == " " or event.unicode == "'" or event.unicode == "-":
					gunshot_words += event.unicode
					for zombie in Enemies:
						if gunshot_words == zombie.phrase:
							Phoebe.bang_timer = 30
							Phoebe.image = Phoebe.bang
							zombie.alive = False
							zombie.image = zombie.shot_image
							if (zombie.rect.center[0] < Phoebe.rect.center[0]):
								zombie.flip_sides()
								zombie.remain_on_screen = -36
							zombie.rotation_pivot = zombie.image
							Phoebe.kill_count += 1
							gunshot_words = ""
							if (level_wave == 3 and Phoebe.rect.center[0] < zombie.rect.center[0] and Phoebe.facing_right == False):
								Phoebe.flip_sides()
								Phoebe.facing_right = True
							if (level_wave == 3 and Phoebe.rect.center[0] > zombie.rect.center[0] and Phoebe.facing_right == True):
								Phoebe.flip_sides()
								Phoebe.facing_right = False
								
				gunshot_word_display = font.render(gunshot_words, True, RED)
	pressed = pygame.key.get_pressed()
	if pressed[pygame.K_BACKSPACE]:
		if backspace_delay == 0:
			gunshot_words = gunshot_words[:-1]
			gunshot_word_display = font.render(gunshot_words, True, RED)
			backspace_delay = 2
		else:
			backspace_delay -= 1
	screen.fill(BLACK)
	Backgrounds.update()
	Backgrounds.draw(screen)
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, 685, 1200, 115))
	
	
	zombie_stack = -1
	stacked_zombies = []
	level_spawn_timer -= 1
	if Phoebe.bang_timer > 0:
		Phoebe.bang_timer -= 1
		if (Phoebe.bang_timer == 0):
			Phoebe.image = Phoebe.original_image
	if (level_spawn_timer % 60 == 0 and level_spawn_timer > -1):
		zombie_type = random.randint(0,5)
		if (zombie_type <= 3):
			New_Zombie = Zombie("Zombie 1.png", zombie_words[(random.randint(0, len(zombie_words)-1))])
			New_Zombie.run_speed = zombie_speed
		else:
			New_Zombie = Zombie("Fat Zombie.png", zombie_adjectives[(random.randint(0, len(zombie_adjectives)-1))].capitalize() + " " + zombie_nouns[(random.randint(0, len(zombie_nouns)-1))].capitalize())
			New_Zombie.load_fat()
			New_Zombie.run_speed = zombie_speed*.4
		Enemy_List.insert(0, New_Zombie)
		Enemies.add(New_Zombie)
		if level_wave == 1:
			New_Zombie.rect.center = Zombie_Spawns[current_stage]
		elif level_wave == 2:
			New_Zombie.rect.center = Zombie_Left_Spawns[current_stage]
			New_Zombie.flip_sides()
		elif level_wave == 3:
			if wave_three_rotating_sides %2 == 0:
				New_Zombie.rect.center = Zombie_Spawns[current_stage]
				wave_three_rotating_sides += 1
				New_Zombie.wave_three_status = 1
			elif wave_three_rotating_sides %2 == 1:
				New_Zombie.rect.center = Zombie_Left_Spawns[current_stage]
				New_Zombie.flip_sides()
				wave_three_rotating_sides += 1
				New_Zombie.wave_three_status = 2
	for zombie in Enemy_List:
		if zombie.alive == True:
			zombie.move_forward()
			zombie.display_text_bubble()
			zombie.eat()
		elif zombie.alive == False:
			if zombie.remain_on_screen > 0:
				zombie.remain_on_screen -= 1
				zombie.image = pygame.transform.rotate(zombie.rotation_pivot, 10 * (36-zombie.remain_on_screen))
				zombie.image = pygame.transform.scale(zombie.image, (zombie.remain_on_screen*6, zombie.remain_on_screen*6))
			elif zombie.remain_on_screen < 0:
				zombie.remain_on_screen += 1
				zombie.image = pygame.transform.rotate(zombie.rotation_pivot, - 10 * (36+zombie.remain_on_screen))
				zombie.image = pygame.transform.scale(zombie.image, (-zombie.remain_on_screen*6, -zombie.remain_on_screen*6))

			if zombie.remain_on_screen == 0:
				Enemies.remove(zombie)
	if (Phoebe.kill_count == number_of_zombies * level_wave and wave_two_started == False):
		wave_two_started = True
		Phoebe.move_to_new_spot = 70
		level_wave += 1
		level_spawn_timer = number_of_zombies * 60 # Desired Zombies * Spawn Rate * Level Wave??
	if (Phoebe.kill_count == number_of_zombies * level_wave and wave_three_started == False):
		wave_three_started = True
		Phoebe.move_to_new_spot = -40
		level_wave += 1
		level_spawn_timer = number_of_zombies * 60 * 2# Desired Zombies * Spawn Rate * Level Wave??
	if (Phoebe.kill_count == number_of_zombies * 4):
		wave_two_started = False
		wave_three_started = False
		Phoebe.kill_count = 0
		level_wave = 1
		level_spawn_timer = number_of_zombies * 60
		current_stage += 1
		if (current_stage == 3):
			run = False
			game_over = False
			victory = True
			#WIN SCREEN
		else:
			Backgrounds.empty()
			Backgrounds.add(Game_Levels[current_stage])
			Phoebe.rect.center = (Phoebe_Spawns[current_stage])
			Phoebe.new_level()
	Enemies.update()
	Enemies.draw(screen)
	#Characters.OrderedUpdates()
	Characters.update()
	Characters.draw(screen)
	chunks = gunshot_words.split(' ', 1)
	if len(chunks) >= 1:
		gunshot_word_display = font.render("~ " + chunks[0], True, RED)
		screen.blit(gunshot_word_display, (10, 720))
	if len(chunks) == 2:
		gunshot_word_display_two = font.render("~ " + chunks[1], True, RED)
		screen.blit(gunshot_word_display_two, (10, 760))
	spaces = 0
	for i in range (0, len(gunshot_words)):
		if gunshot_words[i] == ' ':
			spaces += 1
	if spaces >= 2:
		gunshot_words = ""
	Phoebe.new_wave()
	Phoebe.display_health()
	
	#Line for text entry
	pygame.draw.rect(screen, BLUE, pygame.Rect(0, 685, 1200, 30))
	pygame.display.flip()
	clock.tick(FPS)
while (game_over == True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			game_over = False
	screen.fill(BLACK)
	game_over_display = font.render("GAME OVER", True, RED)
	screen.blit(game_over_display, (430, 400))
	kill_count_display = font.render("KILL COUNT: " + str(Phoebe.kill_count), True, RED)
	screen.blit(kill_count_display, (430, 460))
	pygame.display.flip()
	clock.tick(FPS)
while (victory == True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			victory = False
	screen.fill(BLACK)
	game_over_display = font.render("VICTORY!", True, RED)
	screen.blit(game_over_display, (430, 400))
	#kill_count_display = font.render("KILL COUNT: " + str(Phoebe.kill_count), True, RED)
	#screen.blit(kill_count_display, (430, 460))
	pygame.display.flip()
	clock.tick(FPS)


