import pygame
import threading
import os


def run_pygame():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"  # Set initial position
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Pygame Window")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 255))  # Fill screen with blue
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()


import cv2


def run_opencv():
    print('here')
    os.environ['SDL_VIDEO_WINDOW_POS'] = "800,100"  # Set initial position next to Pygame window
    cap = cv2.VideoCapture(0)  # Open the default camera
    print('open')
    while True:
        ret, frame = cap.read()
        if not ret:
            print('broke')
            break

        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()


import pygetwindow as gw
import time


def synchronize_windows():
    while True:
        try:
            # Get the positions of the windows
            pygame_window = gw.getWindowsWithTitle('Pygame Window')[0]
            opencv_window = gw.getWindowsWithTitle('Camera Feed')[0]

            # Calculate new positions for the OpenCV window
            new_x = pygame_window.left + pygame_window.width + 1  # Offset to avoid overlap
            new_y = pygame_window.top

            # Move OpenCV window to new position if it's not already there
            if opencv_window.left != new_x or opencv_window.top != new_y:
                opencv_window.moveTo(new_x, new_y)

        except IndexError:
            # If windows are not found, break the loop
            break

        time.sleep(0.1)  # Sleep briefly to reduce CPU usage


if __name__ == "__main__":
    pygame_thread = threading.Thread(target=run_pygame)
    opencv_thread = threading.Thread(target=run_opencv)
    print('running')

    pygame_thread.start()
    opencv_thread.start()
    print('started')

    time.sleep(3)

    sync_thread = threading.Thread(target=synchronize_windows)
    sync_thread.start()

    pygame_thread.join()
    opencv_thread.join()
    sync_thread.join()