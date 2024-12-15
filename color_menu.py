import pygame
import pygame_menu
from random import randrange

# Initialize Pygame
pygame.init()

# Set up the display
surface = pygame.display.set_mode((600, 400))
pygame.display.set_caption('Pygame Menu Text Color Change Example')

# Create a function to change the menu background color
def change_color():
    random_color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
    menu.get_scrollarea().update_area_color(random_color)

# Create a function to change the text color of the menu buttons
def change_text_color():
    random_text_color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
    # Change button text colors
    for widget in menu.get_widgets():
        if isinstance(widget, pygame_menu.widgets.Button):
            widget.set_font('Arial', 30, random_text_color, random_text_color, random_text_color, (0, 0, 0), (0, 0, 0))  # Set font name, size, normal color, selected color, readonly color, background color

# Create the menu with initial settings
menu = pygame_menu.Menu('My Menu', 600, 400, theme=pygame_menu.themes.THEME_DARK)
menu.add.button('Change Color', change_color)
menu.add.button('Change Text Color', change_text_color)
menu.add.button('Quit', pygame_menu.events.EXIT)

# Main loop
running = True
while running:
    surface.fill((0, 0, 0))  # Clear screen with black color

    # Run the menu on the surface
    menu.mainloop(surface)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygame
pygame.quit()
