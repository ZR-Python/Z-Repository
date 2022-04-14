import pygame
import random

pygame.init()

BLACK = (0,0,0)
RED = (255, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
BORDER = (77, 77, 77)
BUTTON_GREY = (96, 96, 96)
BUTTON_GREEN = (0, 153, 0)
TEXT_BOX = (255,165,53)
TEXT_COLOR = (135,18,130)
game_over = False
title_screen = True
zombie_speed = 500

wave_two_started = False
wave_three_started = False
wave_three_rotating_sides = 0

screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Zombie Typing")
FPS = 60
number_of_zombies = 20

level_wave = 1

clock = pygame.time.Clock()
run = True
font = pygame.font.Font("freesansbold.ttf", 24)
button_font = pygame.font.SysFont("comicsans", 30)
gunshot_words = ""
backspace_delay = 4
gunshot_word_display = font.render(gunshot_words, True, RED)
zombie_words = []
with open("zombie_normal.txt", "r") as f:
    zombie_words = f.readlines()
zombie_words = [line.strip() for line in zombie_words]
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
		display_text = button_font.render(self.text, True, TEXT_COLOR)
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
		self.rect = self.image.get_rect()
		self.health = 100
		self.health_bar_name = "HEALTH: "
		self.kill_count = 0
		self.moving = 25
		self.bang_timer = 0
		self.move_to_new_spot = 0
	def display_health(self):
		health_bar_display = font.render("HEALTH: ", True, RED)
		screen.blit(health_bar_display, (670, 725))
		pygame.draw.rect(screen, GREEN, pygame.Rect(800, 725, self.health * 3, 25))
		kill_count_display = font.render("KILL COUNT: " + str(self.kill_count), True, RED)
		screen.blit(kill_count_display, (670, 775))
	def damage(self, damage):
		self.health -= damage
	def get_health(self):
		return self.health
	def new_wave(self):
		if (self.move_to_new_spot > 0):
			self.move_to_new_spot -= 1
			self.rect.center = (self.rect.center[0] + 10, self.rect.center[1])
			if self.move_to_new_spot == 0:
				self.image = pygame.transform.flip(self.image, True, False)
				self.original_image = pygame.transform.flip(self.original_image, True, False)
				self.bang = pygame.transform.flip(self.bang, True, False)


Phoebe = Player("Phoebe_Right.png")
#Phoebe.image = pygame.transform.flip(Phoebe.image, True, False)

class Zombie(pygame.sprite.Sprite):
	def __init__(self, image, phrase):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
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
	def display_text_bubble(self):
		zombie_word_display = font.render(self.phrase, True, TEXT_COLOR)
		pygame.draw.rect(screen, TEXT_BOX, pygame.Rect(self.rect.x-5, self.rect.y-75, self.phrase_length * 20, 60))
		pygame.draw.rect(screen, BORDER, (self.rect.x-5, self.rect.y-75, self.phrase_length*20, 60), 4, border_radius=1)
		screen.blit(zombie_word_display, (self.rect.x, self.rect.y - 45))
	def move_forward(self, Enemies):
		global game_over
		global run
		dx, dy = (self.rect.x - Phoebe.rect.x, self.rect.y - Phoebe.rect.y)
		if (dx > 30 and level_wave == 1):
			stepx, stepy = (-dx / self.run_speed, -dy /self.run_speed)
			self.rect.center = (self.rect.center[0] + stepx, self.rect.center[1] + stepy)
		elif (dx < 30 and level_wave == 2):
			stepx, stepy = (-dx / self.run_speed, -dy /self.run_speed)
			self.rect.center = (self.rect.center[0] + stepx, self.rect.center[1] + stepy)
		elif ((dx < 30 and level_wave == 3 and self.rect.center[0] < Phoebe.rect.center[0]) or (dx > 30 and level_wave == 3 and self.rect.center[0] > Phoebe.rect.center[0])):
			stepx, stepy = (-dx / self.run_speed, -dy /self.run_speed)
			self.rect.center = (self.rect.center[0] + stepx, self.rect.center[1] + stepy)
		else:
			if self.eating == False:
				self.eating = True
			if self.eat_timer == 100:
				Phoebe.damage(10)
				if (Phoebe.get_health() == 0):
					run = False
					game_over = True
				self.eat_timer = 0
			else:
				self.eat_timer += 1
			#EAT




Bridge_Level = Background("Bridge_Background.png")
Game_Title = Background("Game_Title.png")
Game_Title.rect.center = (600, 200)
Play_Button = Button("START GAME")
Play_Button.rect.center = (600, 400)
Title_Sprites = pygame.sprite.Group()
Title_Sprites.add(Game_Title)
Title_Buttons = [Play_Button]
Few_Zombies = Button("Few")
Some_Zombies = Button("Some")
Some_Zombies.active = True
Some_Zombies.color = BLUE
Many_Zombies = Button("Many")
Number_of_Zombies_Buttons = [Few_Zombies, Some_Zombies, Many_Zombies]
Slow_Speed = Button("Slow")
Medium_Speed = Button("Medium")
Medium_Speed.active = True
Medium_Speed.color = BLUE
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
Few_Zombies.spawn_number = 2 
Some_Zombies.spawn_number = 20
Many_Zombies.spawn_number = 30
Slow_Speed.zombie_speed = 900
Medium_Speed.zombie_speed = 550
Intense_Speed.zombie_speed = 330
Backgrounds = pygame.sprite.Group()
Backgrounds.add(Bridge_Level)
Enemy_List = []
Characters = pygame.sprite.Group()
Enemies = pygame.sprite.Group()
Characters.add(Phoebe)
Enemies.add()
Phoebe.rect.center = (300, 400)

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
					button.color = BLUE
					for other_button in Number_of_Zombies_Buttons:
						if button != other_button:
							other_button.active = False
							other_button.color = BUTTON_GREY
			for button in Zombie_Speed_Buttons:
				if (button.rect.collidepoint(pygame.mouse.get_pos())):
					button.active = True
					button.color = BLUE
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
	number_of_zombies_option = button_font.render("Amount of Zombies: ", True, RED)
	screen.blit(number_of_zombies_option, (450, 450))
	zombie_speed_option = button_font.render("Zombie Speed: ", True, RED)
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
				if event.unicode.islower() or event.unicode.isupper() or event.unicode.isdigit() or event.unicode == ',' or event.unicode == "?" or event.unicode == " ":
					gunshot_words += event.unicode
					for zombie in Enemies:
						if gunshot_words == zombie.phrase:
							Phoebe.bang_timer = 30
							Phoebe.image = Phoebe.bang
							Enemies.remove(zombie)
							zombie.alive = False
							Phoebe.kill_count += 1
							gunshot_words = ""
				gunshot_word_display = font.render(gunshot_words, True, RED)
	pressed = pygame.key.get_pressed()
	if pressed[pygame.K_BACKSPACE]:
		if backspace_delay == 0:
			gunshot_words = gunshot_words[:-1]
			gunshot_word_display = font.render(gunshot_words, True, RED)
			backspace_delay = 4
		else:
			backspace_delay -= 1
	screen.fill(BLACK)
	Backgrounds.update()
	Backgrounds.draw(screen)
	pygame.draw.rect(screen, BLACK, pygame.Rect(0, 685, 1200, 115))
	
	screen.blit(gunshot_word_display, (50, 720))
	zombie_stack = -1
	stacked_zombies = []
	level_spawn_timer -= 1
	if Phoebe.bang_timer > 0:
		Phoebe.bang_timer -= 1
		if (Phoebe.bang_timer == 0):
			Phoebe.image = Phoebe.original_image
	if (level_spawn_timer % 60 == 0 and level_spawn_timer > -1):
		New_Zombie = Zombie("Zombie 1.png", zombie_words[(random.randint(0, len(zombie_words)-1))])
		New_Zombie.run_speed = zombie_speed
		Enemy_List.insert(0, New_Zombie)
		Enemies.add(New_Zombie)
		if level_wave == 1:
			New_Zombie.rect.center = (1060, 400)
		elif level_wave == 2:
			New_Zombie.rect.center = (160, 400)
			New_Zombie.image = pygame.transform.flip(New_Zombie.image, True, False)
		elif level_wave == 3:
			if wave_three_rotating_sides %2 == 0:
				New_Zombie.rect.center = (1060, 400)
				wave_three_rotatin_sides += 1
			else:
				New_Zombie.rect.center = (160, 400)
				New_Zombie.image = pygame.transform.flip(New_Zombie.image, True, False)
				wave_three_rotatin_sides += 1
	for zombie in Enemy_List:
		if zombie.alive == True:
			zombie.move_forward(Enemies)
			zombie.display_text_bubble()
	if (Phoebe.kill_count == number_of_zombies * level_wave and wave_two_started == False):
		wave_two_started = True
		Phoebe.move_to_new_spot = 70
		level_wave += 1
		level_spawn_timer = number_of_zombies * 60 # Desired Zombies * Spawn Rate * Level Wave??
	if (Phoebe.kill_count == number_of_zombies * level_wave and wave_three_started == False):
		wave_three_started = True
		Phoebe.move_to_new_spot = -35
		level_wave += 1
		level_spawn_timer = number_of_zombies * 60 # Desired Zombies * Spawn Rate * Level Wave??
	Enemies.update()
	Enemies.draw(screen)
	#Characters.OrderedUpdates()
	Characters.update()
	Characters.draw(screen)
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


