import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
import logging
from random import randrange
from typing import Tuple, Any, Optional, List
import threading
from racer import start_racer
from space_defender import start_space_defender
from cv_gesture import start_gesture_control
import time
import pygetwindow as gw
from os.path import join

ABOUT = [f'pygame-menu {pygame_menu.__version__}',
         f'Author: {pygame_menu.__author__}',
         f'Email: {pygame_menu.__email__}']
DIFFICULTY = ['EASY']
CB_MODE = False
FPS = 60
WINDOW_SIZE = (640, 480)

clock: Optional['pygame.time.Clock'] = None
main_menu: Optional['pygame_menu.Menu'] = None
about_menu: Optional['pygame_menu.Menu'] = None
play_menu: Optional['pygame_menu.Menu'] = None
surface: Optional['pygame.Surface'] = None

def play_function(difficulty: List, font: 'pygame.font.Font', test: bool = False) -> None:
    """
    Main game function.

    :param difficulty: Difficulty of the game
    :param font: Pygame font
    :param test: Test method, if ``True`` only one loop is allowed
    """
    assert isinstance(difficulty, list)
    difficulty = difficulty[0]
    assert isinstance(difficulty, str)

    # Define globals
    global main_menu
    global play_menu
    global clock
    global CB_MODE

    if difficulty == 'EASY':
        f = font.render('Playing as a baby (easy)', True, (255, 255, 255))
    elif difficulty == 'MEDIUM':
        f = font.render('Playing as a kid (medium)', True, (255, 255, 255))
    elif difficulty == 'HARD':
        f = font.render('Playing as a champion (hard)', True, (255, 255, 255))
    else:
        raise ValueError(f'unknown difficulty {difficulty}')
    f_esc = font.render('Press ESC to open the menu', True, (255, 255, 255))

    # Draw random color and text
    bg_color = (100, 100, 100) # random_color()

    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.full_reset()

    frame = 0

    while True:

        # noinspection PyUnresolvedReferences
        clock.tick(60)
        frame += 1

        # Application events
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()

                    # Quit this function, then skip to loop of main-menu on line 221
                    return

        # Pass events to main_menu
        if main_menu.is_enabled():
            main_menu.update(events)

        # Continue playing
        # surface.fill(bg_color)

        # if CB_MODE:
        #     surface.fill((0, 0, 0))
        # else:
        #     surface.fill((128, 0, 128))

        surface.blit(f, (int((WINDOW_SIZE[0] - f.get_width()) / 2),
                         int(WINDOW_SIZE[1] / 2 - f.get_height())))
        surface.blit(f_esc, (int((WINDOW_SIZE[0] - f_esc.get_width()) / 2),
                             int(WINDOW_SIZE[1] / 2 + f_esc.get_height())))
        pygame.display.flip()

        # If test returns
        if test and frame == 2:
            break


def main_background() -> None:
    """
    Function used by menus, draw on background while menu is active.
    """
    global surface
    # print(CB_MODE)
    if CB_MODE:
        surface.fill((255, 255, 255))
    else:
        surface.fill((101, 0, 0))


def start_pygame(test: bool = False) -> None:
    """
    Main program.

    :param test: Indicate function is being tested
    """

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock, main_menu, about_menu, play_menu, surface, CB_MODE


    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = create_example_window('Example - Game Selector', WINDOW_SIZE)
    clock = pygame.time.Clock()

    # -------------------------------------------------------------------------
    # Create menus: Play Menu
    # -------------------------------------------------------------------------
    my_theme = pygame_menu.themes.Theme(title_background_color=(120, 120, 120),
                                        title_font_shadow=True,
                                        title_font='arialblack')

    play_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.7,
        title='Play Menu',
        theme=my_theme,
        width=WINDOW_SIZE[0] * 0.75
    )

    # submenu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    #
    # submenu_theme.widget_font_size = 15
    # play_submenu = pygame_menu.Menu(
    #     height=WINDOW_SIZE[1] * 0.5,
    #     theme=submenu_theme,
    #     title='Submenu',
    #     width=WINDOW_SIZE[0] * 0.7
    # )
    # for i in range(30):
    #     play_submenu.add.button(f'Back {i}', pygame_menu.events.BACK)
    # play_submenu.add.button('Return to main menu', pygame_menu.events.RESET)

    play_menu.add.button('Гонщик',  # When pressing return -> play(DIFFICULTY[0], font)
                         start_game_with_options,
                         'racer',
                         font_name = 'arialblack')
                         # DIFFICULTY,
                         # pygame.font.Font(pygame_menu.font.FONT_FRANCHISE, 30))
    play_menu.add.button('Космический защитник',  # When pressing return -> play(DIFFICULTY[0], font)
                         start_game_with_options,
                         'space_defender',
                         font_name = 'arialblack')
                         # DIFFICULTY,
                         # pygame.font.Font(pygame_menu.font.FONT_FRANCHISE, 30))
    # play_menu.add.selector('Select difficulty ',
    #                        [('1 - Easy', 'EASY'),
    #                         ('2 - Medium', 'MEDIUM'),
    #                         ('3 - Hard', 'HARD')],
    #                        onchange=change_difficulty,
    #                        selector_id='select_difficulty')
    # play_menu.add.button('Another menu', play_submenu)
    play_menu.add.button('Главное меню', pygame_menu.events.BACK,
                         font_name = 'arialblack')

    # -------------------------------------------------------------------------
    # Create menus:About
    # -------------------------------------------------------------------------
    about_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    about_theme.widget_margin = (0, 0)

    about_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.9,
        theme=my_theme,
        title='Настройки',
        width=WINDOW_SIZE[0] * 0.9
    )

    # for m in ABOUT:
    #     about_menu.add.label(m, align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    about_menu.add.vertical_margin(30)
    about_menu.add.toggle_switch(
        "Режим цветослабости:",
        onchange=_menu_set_cb_mode,
        default=False,
        width=120,
        state_text=('Выкл', 'Вкл'),
        toggleswitch_id="CB_MODE",
        font_name = 'arialblack'
    )
    about_menu.add.button('Главное меню', pygame_menu.events.BACK,
                         font_name = 'arialblack')

    # -------------------------------------------------------------------------
    # Create menus: Main
    # -------------------------------------------------------------------------
    main_theme = pygame_menu.themes.THEME_DEFAULT.copy()



    main_menu = pygame_menu.Menu(
            height=WINDOW_SIZE[1] * 0.7,
            theme=my_theme,
            title='Главное меню',
            width=WINDOW_SIZE[0] * 0.7
        )

    main_menu.add.button('Играть!', play_menu,
                         font_name = 'arialblack')
    main_menu.add.button('Настройки', about_menu,
                         font_name = 'arialblack')

    main_menu.add.button('Выход', pygame_menu.events.EXIT,
                         font_name = 'arialblack')

    change_color(main_menu)
    change_color(about_menu)
    change_color(play_menu)

    # Icon of the Game
    icon = pygame.image.load(join('.\\Assets\\', 'main_menu_icon.png'))

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    while True:

        # Tick
        clock.tick(FPS)

        # Paint background
        main_background()

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Main menu
        if main_menu.is_enabled():
            # Screen_Width, Screen_Height = 600, 700
            # win_size = (Screen_Width, Screen_Height)
            surface = surface = create_example_window('Главное меню', WINDOW_SIZE)
            # pygame.display.set_caption(title)
            # screen = pygame.display.set_mode((Screen_Width, Screen_Height))
            # Set Caption of the Game
            pygame.display.set_caption('Главное меню')
            # Set Icon
            pygame.display.set_icon(icon)
            main_menu.mainloop(surface, main_background, disable_loop=test, fps_limit=FPS)

        # Flip surface
        pygame.display.flip()

        # At first loop returns
        if test:
            break


# def create_menu(theme):
#     menu = pygame_menu.Menu('Welcome', 600, 400, theme=theme)
#     # menu.add.button('Toggle Theme', lambda: toggle_theme(menu))
#     menu.add.button('Quit', pygame_menu.events.EXIT)
#     return menu


# Function to toggle theme
# def toggle_theme(val, current_menu):
#     global current_theme, menu
#     if val:
#         # current_theme = 'dark'
#         menu = create_menu(theme_dark)  # Create new menu with dark theme
#     else:
#         # current_theme = 'default'
#         menu = create_menu(theme_default)  # Create new menu with default theme
def change_color(menu):
    if CB_MODE:
        menu_color = (255, 228, 179)
        text_color = (0, 0, 224)
    else:
        menu_color = (205, 0, 0)
        text_color = (255, 215, 0)
        # menu_color = (220, 220, 220)
        # text_color = (70, 70, 70)
    menu.get_scrollarea().update_area_color(menu_color)
    for widget in menu.get_widgets():
        if isinstance(widget, pygame_menu.widgets.Button) or isinstance(widget, pygame_menu.widgets.ToggleSwitch):
            widget.set_font('arialblack', 30, text_color, text_color, text_color, (0, 0, 0), menu_color)  # Set font name, size, normal color, selected color, readonly color, background color

    # surface.fill((100, 100, 100))

def _menu_set_cb_mode(val: bool) -> None:
    try:
        global CB_MODE
        if val:
            CB_MODE = True
            change_color(main_menu)
            change_color(about_menu)
            change_color(play_menu)
            logging.info('Включен режим цветослабости')
        else:
            CB_MODE = False
            change_color(main_menu)
            change_color(about_menu)
            change_color(play_menu)
            logging.info('Выключен режим цветослабости')
    except Exception:
        logging.exception(f"Ошибка переключения режима цветослабости")

def synchronize_windows():
    while True:
        try:
            # Get the positions of the windows
            menu_open = False
            racer_open = False
            space_shooter_open = False

            # current_pygame_window = gw.getWindowsWithTitle('Главное меню')[0]

            try:
                current_pygame_window = gw.getWindowsWithTitle('Главное меню')[0]
                menu_open = True
            except:
                menu_open = False

            if not menu_open:
                try:
                 current_pygame_window = gw.getWindowsWithTitle('Гонщик')[0]
                 racer_open = True
                except:
                 racer_open = False

            if not (menu_open or racer_open):
                try:
                 current_pygame_window = gw.getWindowsWithTitle('Космический защитник')[0]
                 space_shooter_open = True
                except:
                 space_shooter_open = False

            if not (menu_open or racer_open or space_shooter_open):
                print('no windows')
                break

            opencv_window = gw.getWindowsWithTitle('1')[0]

            # Calculate new positions for the OpenCV window
            new_x = current_pygame_window.left + current_pygame_window.width + 1  # Offset to avoid overlap
            new_y = current_pygame_window.top

            # Move OpenCV window to new position if it's not already there
            if opencv_window.left != new_x or opencv_window.top != new_y:
                opencv_window.moveTo(new_x, new_y)

        except IndexError:
            # If windows are not found, break the loop
            break

        time.sleep(0.1)  # Sleep briefly to reduce CPU usage

def start_game_with_options(game_name):
    global CB_MODE
    if game_name == 'racer':
        start_racer(CB_MODE)
    elif game_name == 'space_defender':
        start_space_defender(CB_MODE)
    else:
        return

if __name__ == "__main__":

    open_cv = False
    if open_cv:
        pygame_thread = threading.Thread(target=start_pygame)
        opencv_thread = threading.Thread(target=start_gesture_control)
        print('running')

        pygame_thread.start()
        opencv_thread.start()
        print('started')

        time.sleep(3) # Ожидание запуска камеры

        sync_thread = threading.Thread(target=synchronize_windows)
        sync_thread.start()

        pygame_thread.join()
        opencv_thread.join()
        sync_thread.join()
    else:
        pygame_thread = threading.Thread(target=start_pygame)
        pygame_thread.start()
        pygame_thread.join()