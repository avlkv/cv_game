import pygame
import threading


def run_pygame():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
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
    cap = cv2.VideoCapture(0)  # Open the default camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    pygame_thread = threading.Thread(target=run_pygame)
    opencv_thread = threading.Thread(target=run_opencv)

    pygame_thread.start()
    opencv_thread.start()

    pygame_thread.join()
    opencv_thread.join()