# ===== Importing Required Modules ==========================================
from pynput.keyboard import Controller as kc
from pynput.keyboard import Key
from pynput.mouse import Controller as mc, Controller
from pynput.mouse import Button
import cv2  # конкретное названия

from win32com.client import Dispatch
from win32api import GetSystemMetrics
# import ctypes

import pygetwindow as gw

import pygetwindow as gw
# import time

from numpy import interp
from time import sleep, time

# from Handcontroller import Hand_Controller

keyboard = kc()
mouse = mc()
# ================================================================================
# =============== Machine Voice ==================================================
voice_engine = Dispatch('SAPI.Spvoice')

from math import hypot
from mediapipe import solutions
from cv2 import line, circle, cvtColor, flip, FILLED, COLOR_BGR2RGB
import numpy as np


class Hand_Controller:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_confidence=0.5):
        """
        Args:
            max_hands (int):        Defaults to 1.
                Represents the maximum no. of handes to detect in a frame at a time.
            detection_con (float):  Defaults to 0.7.
                Confidence in the detection of hande with-in the frame
            track_confidence (float):Defaults to 0.6.
                Confidence of detecting the hand-movement between frame, i.e. Confidence to detecrmined the track change of hand.
        Custom-Class made to get the Hand-gesture , position, and state of each finger
        """
        self.mpHands = solutions.hands
        self.max_hand = max_hands
        self.hands = self.mpHands.Hands(mode, max_hands, 1, detection_con, track_confidence)
        self.mpdraw = solutions.drawing_utils

        self.fingerup_list = np.array([])
        self.lm_list = []
        self.base_id = [1, 5, 9, 13, 17]
        self.tip_id = [4, 8, 12, 16, 20]
        self.close_tip_id = [5, 6, 10, 14, 18]
        self.hand_side = None

    def findhand(self, img, draw=False, fliped_img=True):
        """Method used to find hands with in the given frame/image

        Args:
            img     : Image onto which hands are needed to be find
            draw (bool): Need to draw hand landmarks. Defaults to False.
            fliped_img (bool): Image passed as agrgument is Flipped or not. Defaults to True.

        Returns:
            cv2-image: image onto which landmarks ar drawn
        """
        # === Getting the image in BGR format ====================================
        # === Then flipping the image for better understanding ===================
        self.fliped_img = fliped_img
        RGBimg = cvtColor(img, COLOR_BGR2RGB)
        if self.fliped_img:
            self.img = img
        else:
            self.img = flip(img, 1)
            RGBimg = flip(RGBimg, 1)
        # === Processing the Hand position and ===================================
        self.result = self.hands.process(RGBimg)
        # === Drawing the Landmarks of the Hand, if given draw ===================
        lm_list = []
        if self.result.multi_hand_landmarks:
            for handlms in self.result.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(img, handlms, self.mpHands.HAND_CONNECTIONS)
                if self.max_hand == 1:
                    given_hand = self.result.multi_hand_landmarks[0]
                    for id, lm in enumerate(given_hand.landmark):
                        h, w, _ = self.img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lm_list.append([id, cx, cy])
        self.lm_list = lm_list
        return img

    def findPosition(self, handno=0):
        """
        Method used to find the postion of hand lanmarks in the image

        Args:
            handno (int) : If here are multi hands, select a specific hand to find it's landmark position. Defaults to 0.

        Returns:
            lm_list : list of coordinates of each handlandmarks in the image along with there landmark id.
        """
        if handno == 0:
            return self.lm_list

        lm_list = []
        if self.result.multi_hand_landmarks:
            given_hand = self.result.multi_hand_landmarks[handno]
            for id, lm in enumerate(given_hand.landmark):
                h, w, _ = self.img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
        self.lm_list = lm_list
        return self.lm_list

    def fingersUp(self):
        """
        Method used to find whether the fingers and thumb are open or closed

        Returns:
            fingerup_list : list of states of each finger in the hand
        """
        self.fingerup_list = np.array([])
        if self.lm_list:
            # ==== Checking whether left hand or right hand =======================
            # ==== And then determining the Thumb state:- Open or Close ==========
            if self.lm_list[0][1] > self.lm_list[1][1]:
                self.hand_side = 'right'
                if self.lm_list[self.tip_id[0]][1] < self.lm_list[self.close_tip_id[0]][1]:
                    self.fingerup_list = np.append(self.fingerup_list, [1])
                else:
                    # self.fingerup_list.append(0)
                    self.fingerup_list = np.append(self.fingerup_list, [0])
            else:
                self.hand_side = 'left'
                if self.lm_list[self.tip_id[0]][1] > self.lm_list[self.close_tip_id[0]][1]:
                    self.fingerup_list = np.append(self.fingerup_list, [1])
                else:
                    self.fingerup_list = np.append(self.fingerup_list, [0])
            # ==== Checking the state of the Fingers:- Open or Close =============
            for id in range(1, 5):
                if self.lm_list[self.tip_id[id]][2] < self.lm_list[self.close_tip_id[id]][2]:
                    self.fingerup_list = np.append(self.fingerup_list, [1])
                else:
                    self.fingerup_list = np.append(self.fingerup_list, [0])
                # ====================================================================
        return self.fingerup_list

    def getBaseSize(self, img, F1, F2, draw_f=True, draw_line=True, draw_cntr=False, finger_up=False):
        """
        Args:
            img : image onto which landmarks are to be drawn
            F1  : Finger 1 id no.
            F2  : Finger 2 id no.
            draw_f (bool)   : Do fingers are needed to be highlighted or not. Defaults to True.
            draw_line (bool): Is there any need of line conecting fingers to be highlighted or not. Defaults to True.
            draw_cntr (bool): Do centre point is needed to be highlighted or not. Defaults to False.
            finger_up (bool): Finger state. Defaults to True.

        Returns:
            distance        : distance btw the two fingers
            tuple (cx, cy)  : center point btw the fingers
        """
        f1 = self.base_id[F1]
        f2 = self.base_id[F2]
        distance = 0
        cx, cy = 0, 0

        def find():
            """Used to find the distance btw the two fingers and draw the connecting lines btw the finger

            Returns:
                dis             : distance btw the fingers
                tuple (cx, cy)  : center point btw the fingers
            """
            f1_x, f1_y = self.lm_list[f1][1:]
            f2_x, f2_y = self.lm_list[f2][1:]
            cx, cy = (f1_x + f2_x) // 2, (f1_y + f2_y) // 2
            if draw_line:
                line(img, (f1_x, f1_y), (f2_x, f2_y), (61, 90, 128), 4)
            if draw_f:
                circle(img, (f1_x, f1_y), 10, (0, 29, 62), FILLED)
                circle(img, (f1_x, f1_y), 7, (0, 53, 102), FILLED)
                circle(img, (f2_x, f2_y), 10, (0, 29, 62), FILLED)
                circle(img, (f2_x, f2_y), 7, (0, 53, 102), FILLED)
            if draw_cntr:
                circle(img, (cx, cy), 8, (224, 251, 252), FILLED)
            dis = hypot(f2_x - f1_x, f2_y - f1_y)
            return dis, (cx, cy)

        if (self.lm_list != []) and (self.fingerup_list.size != 0):
            if finger_up:
                if (self.fingerup_list[F1] == self.fingerup_list[F2] == 1):
                    distance, (cx, cy) = find()
                else:
                    pass
            else:
                distance, (cx, cy) = find()
            return [distance, (cx, cy)]

    def findDistance(self, img, F1, F2, draw_f=True, draw_line=True, draw_cntr=False, finger_up=True):
        """
        Args:
            img : image onto which landmarks are to be drawn
            F1  : Finger 1 id no.
            F2  : Finger 2 id no.
            draw_f (bool)   : Do fingers are needed to be highlighted or not. Defaults to True.
            draw_line (bool): Is there any need of line conecting fingers to be highlighted or not. Defaults to True.
            draw_cntr (bool): Do centre point is needed to be highlighted or not. Defaults to False.
            finger_up (bool): Finger state. Defaults to True.

        Returns:
            distance        : distance btw the two fingers
            tuple (cx, cy)  : center point btw the fingers
        """
        f1 = self.tip_id[F1]
        f2 = self.tip_id[F2]
        distance = 0
        cx, cy = 0, 0

        def find():
            """Used to find the distance btw the two fingers and draw the connecting lines btw the finger

            Returns:
                dis             : distance btw the fingers
                tuple (cx, cy)  : center point btw the fingers
            """
            f1_x, f1_y = self.lm_list[f1][1:]
            f2_x, f2_y = self.lm_list[f2][1:]
            cx, cy = (f1_x + f2_x) // 2, (f1_y + f2_y) // 2
            if draw_line:
                line(img, (f1_x, f1_y), (f2_x, f2_y), (61, 90, 128), 4)
            if draw_f:
                circle(img, (f1_x, f1_y), 10, (0, 29, 62), FILLED)
                circle(img, (f1_x, f1_y), 7, (0, 53, 102), FILLED)
                circle(img, (f2_x, f2_y), 10, (0, 29, 62), FILLED)
                circle(img, (f2_x, f2_y), 7, (0, 53, 102), FILLED)
            if draw_cntr:
                circle(img, (cx, cy), 8, (224, 251, 252), FILLED)
            dis = hypot(f2_x - f1_x, f2_y - f1_y)
            return dis, (cx, cy)

        if (self.lm_list != []) and (self.fingerup_list.size != 0):
            if finger_up:
                if (self.fingerup_list[F1] == self.fingerup_list[F2] == 1):
                    distance, (cx, cy) = find()
                else:
                    pass
            else:
                distance = find()
            return [distance, (cx, cy)]


# def move_window(window_name, x, y):
#     user32 = ctypes.windll.user32
#     hwnd = user32.FindWindowW(None, window_name)
#     user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001 | 0x0002)


def say(audio):
    """Used to Speak the text, given audio parameter"""
    # voice_engine.Speak(audio)
    print(f'Audio: {audio}')


say('Включен режим озвучки')

def get_current_pygame_window():
    menu_open = False
    racer_open = False
    space_defender_open = False
    space_defender_play_open = False

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
            current_pygame_window = gw.getWindowsWithTitle('Космический защитник - Меню')[0]
            space_defender_open = True
        except:
            space_defender_open = False

    if not (menu_open or racer_open or space_defender_open):
        try:
            current_pygame_window = gw.getWindowsWithTitle('Космический защитник - Игра')[0]
            space_defender_play_open = True
            space_defender_open = False
        except:
            space_defender_play_open = False

    if not (menu_open or racer_open or space_defender_open or space_defender_play_open):
        print('Ошибка! Не найдены открытые окна!')
        return False

    return menu_open, racer_open, space_defender_open, space_defender_play_open


# =============== Main Program ===================================================
def gesture_control():
    """
    Main function to run the program
    """

    def check_in_fing(point_list=[0, 0], box=0):
        """
        Проверка положения пальца в интерфейсе окна Computer Vision
        Args:
            point_list (list, optional): finger position on the image. (Defaults to [0,0])
            box (int, optional): It describes which box value has to be returned (Defaults to 0.)

        box = 0: Returns, is finger in the detection box. \n
        box = 1: Returns, is finger only in the gesture box. \n
        box = 2: Returns, on which state box finger is in. \n
        box = 3: Returns, is finger on the qutting button box.
        """
        if box == 0:
            if start_x < point_list[0] < end_x and start_y < point_list[1] < hand_start_y:
                return True
            return False

        if box == 1:
            if hand_start_x < point_list[0] < hand_end_x and hand_start_y < point_list[1] < hand_end_y:
                return True
            return False

        elif box == 2:
            if start_x < point_list[0] < mid_x and start_y < point_list[1] < hand_start_y:
                return 1
            elif mid_x < point_list[0] < end_x and start_y < point_list[1] < hand_start_y:
                return 2

        elif box == 3:
            if (start_x - 100) < point_list[0] < start_x and start_y < point_list[1] < hand_start_y:
                return True
            return False
        return 0

    # ===========================================================================
    def mouse_pointer_click(centre, dis, click, click_counter, thr = 150):
        """
        Определяет, делать ли клик на основании растояния между пальцами

        Args:
            centre  : Middle Coordinates btw the two fingers
            dis     : Distance btw the two fingers
            click : bool можно ли кликать сейчас
        Returns click state.
        """

        try:
            cx, cy = centre

            # Рисует серый круг по центру между пальцами
            cv2.circle(Main_img, (cx, cy), 15, (181, 181, 181), cv2.FILLED)

            max_count = 7

            # Если до этого уже был клик, то обнулить клики?
            if click_counter == 0:
                click = True
            elif click_counter < max_count:
                click = False
            else:
                click_counter = 0
                click = True

            # Если расстояние меньше thr между пальцами
            if dis < thr:
                # Если до этого клика не было, то сделать клик
                # print(f'click_counter: {click_counter}')
                # print(f'click: {click}')

                if click:
                    # Сделать круг желтым
                    cv2.circle(Main_img, (cx, cy), 15, (0, 252, 51), cv2.FILLED)
                    click_counter += 1

                else:
                    # Клик был зарегистрирован, но сам клик не произошел
                    click_counter += 1

            return click, click_counter
        except Exception as e:
            print(e)

            return





    # ===========================================================================
    say('Getting Hand dectector')
    Hand_detector = Hand_Controller()  # Creating hand-Detector
    # ===========================================================================
    V_dir, H_dir, Jump = 0, 0, 0
    Controller_Mode = 0
    # ===========================================================================
    # Setting up the fingers relted variable
    Thumb = Index_Finger = Middle_Finger = Ring_Finger = Pinky_Finger = 1
    sum_of_finger_state = 0
    finger_up_state = []
    # ===========================================================================
    prev_time, cur_time = 0, 0  # Creating time counter to get the fps
    Quit_confirm = False  # Variable that used to stop the program
    # ===========================================================================
    # Font Type used in the text, that to be displayed in the image-frame
    Font_type = cv2.FONT_HERSHEY_PLAIN
    Font_size = 1
    Font_color = (215, 255, 214)
    Font_thickness = 2
    # ===========================================================================
    # Mouse pointer cordinate variable
    pointer_x, pointer_y = 0, 0
    click = False
    click_counter = 0
    clk = 0
    # ===========================================================================
    # Setting up the dimension & co-ordinate for the image-frame to recoginize the gesture
    start_x, start_y, end_x, end_y = 225, 50, 575, 400
    hand_start_x, hand_start_y, hand_end_x, hand_end_y = 225, 100, 575, 400
    mid_x = (start_x + end_x) // 2
    scrn_width, scrn_height = GetSystemMetrics(0), GetSystemMetrics(1)
    # ===========================================================================
    say('Getting Camera')
    cap = cv2.VideoCapture(0)  # Initialising Camera object
    cam_width, cam_height = 960, 720  # And setiing up its
    cap.set(3, cam_width)  # Width and Height
    cap.set(4, cam_height)  # According to ourself
    say('Camera connected')
    # ==========================================================================
    while True:
        _, cap_img = cap.read()  # reading the image from the camera
        cur_time = time()  # storing the current time, [used to calculate FPS]
        Main_img = cv2.flip(cap_img, 1)  # Flipping the image; This image will be used for further processing
        # ======================================================================
        state = ''  # Setting up the state variable
        Hand_Detection_check = False  # Variable to check detection of hand
        # Finding hand in 'Main_img' frame using custom class
        Main_img = Hand_detector.findhand(Main_img, True)
        # Finding up the position of each landmarks in the image
        lm_list = Hand_detector.findPosition()
        # ======================================================================
        # Setted Each Direction value -> 0
        V_dir, H_dir, Jump = 0, 0, 0
        # ======================================================================
        # If hand is detected then do some works; else pass
        if lm_list:
            Hand_Detection_check = True  # Set detection->true for further refernce
            # Get the state of each finger; whether they are open or closed
            finger_up_state = Hand_detector.fingersUp() # массив из 5 цифр 0 или 1

            # print('before', finger_up_state)

            index_base_px, index_base_py = lm_list[5][1:]
            pinky_base_px, pinky_base_px = lm_list[17][1:]

            [dis_base, centre_base] = Hand_detector.getBaseSize(Main_img, 1, 4)

            # print(f'Base: {dis_base}')

            coefficient = 1.8
            dynamic_thr = dis_base * coefficient

            # print(f'Thr: {dynamic_thr}')

            # getting each fingers coordinate list; such that they don't need to be fetched multiple times
            Index_pos = lm_list[8][1:]
            Middle_pos = lm_list[12][1:]
            # Ring_pos = lm_list[16][1:]
            Pinky_pos = lm_list[20][1:]
            Thumb_pos = lm_list[4][1:]

            menu_open, racer_open, space_defender_open, space_defender_play_open = get_current_pygame_window()
            print(get_current_pygame_window())
            if menu_open or racer_open or space_defender_open:
                Controller_Mode = 0
            elif space_defender_play_open:
                Controller_Mode = 1
            else:
                Controller_Mode = 0
                print('Ошибка определения текущего экрана игры!')

            # print(f'Control: {Controller_Mode}')

            # =============== Checking & Changing finger's State ===============
            """
            if any fingers is open,then check for gesture
            else pass
            """
            # Если есть поднятые пальцы?
            if finger_up_state.size != 0:

                # print('finger_up_state.size != 0')

                # Сохранить состояние поднятости каждого пальца отдельно
                [Thumb, Index_Finger, Middle_Finger, Ring_Finger, Pinky_Finger] = finger_up_state

                # Проверка, находится ли указательный и средний палец внутри красной рамки обнаружения жеста
                Index_finger_inn = check_in_fing(Index_pos)  # Checking whether Index & Middle finger
                Middle_finger_inn = check_in_fing(Middle_pos)  # are in the detection box
                Pinky_finger_inn = check_in_fing(Pinky_pos)
                # ==============================================================
                # Если указательный или средний палец внутри рамки
                if Index_finger_inn: # or Middle_finger_inn:
                    """If Index & Middle finger are in the detection box check whether they are in the State-Change Button box"""
                    # Проверяет, находятся ли пальцы в мини-окошке изменения состояния (mouse-arrow?)
                    Index_finger_button_in = check_in_fing(Index_pos, 2)
                    # Middle_finger_button_in = check_in_fing(Middle_pos, 2)

                    # Если оба пальца находятся в одном мини-окошке
                    if Index_finger_button_in and Pinky_Finger: # == Middle_finger_button_in:
                        """
                        if index & middle finger are state-change button box, 
                        find whether they are clicking or not
                        also check in which box they are clicking-in;
                        then change the Controller_mode according to the box
                        """
                        z = 0
                        # Вернуть расстояние между указ и сред пальцем и координату центра между пальцами
                        [dis, centre] = Hand_detector.findDistance(Main_img, 1, 4)

                        # Если заполнено расстояние и центр, то
                        if centre and dis:
                            click, click_counter = mouse_pointer_click(centre, dis, click, click_counter,
                                                                       thr=dynamic_thr)
                            # print(f'Index in control box, and pinky up, click: {click}')
                            # Если был клик, то сделать флаг z = 1, т.е. нужно поменять состояние
                            if click: z = 1
                        if Index_finger_button_in == 1 and z == 1:
                            """if fingers are in box 1 set controller_mode to 0 i.e. Arrow Controls"""
                            # Если в мини-окне "мыши", то поменять на мышь
                            state += " mouse"
                            Controller_Mode = 0
                        elif Index_finger_button_in == 2 and z == 1:
                            # Если в мини-окне "стрелки", то поменять на стрелку
                            """if fingers are in box 2 set controller_mode to 1 i.e. Mouse Controls"""
                            state += " arrow"
                            Controller_Mode = 1
                else:
                    # Если указательного и среднего пальца нет внутри рамки обнаружения жестов



                    # Просуммировать 1 и 0 в состояниях пальцев
                    sum_of_finger_state = sum(finger_up_state)
                    # ==========================================================
                    """ Check for each finger & thumb, whether they are in the detection & gesture box """

                    # Проверить каждый палец, находится ли он именно в окне обнаружения жестов, а не окне изменения состояния
                    Thumb_in = check_in_fing(Thumb_pos, 1)
                    Index_finger_in = check_in_fing(Index_pos, 1)
                    Middle_finger_in = check_in_fing(Middle_pos, 1)
                    # Ring_Finger_in = check_in_fing(Ring_pos,1)
                    Pinky_Finger_in = check_in_fing(Pinky_pos, 1)

                    """ Checking for Index & Middle finger whether they are in Qutting button section """

                    # Проверить не находятся ли одновременно указательный и средний в мини-окошке выхода из программы
                    Index_fing_qt = check_in_fing(Index_pos, 3)
                    # Middle_fing_qt = check_in_fing(Middle_pos, 3)

                    # Если все пальцы выдвинуты
                    if sum_of_finger_state == 5:
                        if Thumb_in:  # И большой палец тоже в окне захвата жестов
                            # Зарегистрировать "прыжок"
                            state = state + "Jump "  # set Jump state to high
                            Jump = 1

                    # Если не все пальцы выдвинуты
                    else:

                        # print(finger_up_state)
                        """if any of the finger is open, check for other controls"""
                        # Create Direction Controls
                        # Vertical Direction

                        # Если выдвинут указательный палец и он в окне захвата жестов
                        if Index_Finger and Index_finger_in:
                            # А средний палец убран
                            if (not Middle_Finger):
                                # То зарегистрировать направление вверх
                                state = state + "Up "
                                V_dir = 1

                            # Если указательный и средний (без безымянного) выдвинуты и в окне захвата
                            elif Middle_finger_in and Middle_Finger and not (
                            Ring_Finger):
                                # То зарегистрировать направление вниз
                                state = state + "Down "
                                V_dir = -1


                        # Horizontal Direction

                        # Если большой палец выдвинут и в окне захвата, а мизинец и средний палец не выдвинуты
                        if (Thumb and Thumb_in) and not (Pinky_Finger) and not (
                        Middle_Finger):
                            # То зарегистрировать направление влево
                            state = state + "Left "
                            H_dir = -1

                        # Если большой палец закрыт и выдвинут и в окне захвата мизинец
                        elif (Pinky_Finger and Pinky_Finger_in) and not (
                        Thumb):
                            # То зарегистрировать движение вправо
                            state = state + "Right "
                            H_dir = 1

                    # print(state)

                    # ==========================================================

                    # Если выбран режим управления мышью
                    if Controller_Mode == 0:
                        """Controller mode -> 0; is mouse control mode
                        Available mouse controls are Pointer movement & Left-click"""

                        sensitivity_factor = 1  # Decrease for less sensitivity, increase for more sensitivity

                        # Если выбрано направление "вверх", т.е. только указательный палец выдвинут
                        if V_dir == 1:
                            # IF vertical direction is +ve then pointer movement will occur
                            # Перемещение курсора мыши через указ. палец
                            px, py = lm_list[8][1:] # Index finger position
                            pointer_x = int(interp(px, (hand_start_x, end_x), (0, scrn_width)) * sensitivity_factor)
                            pointer_y = int(interp(py, (hand_start_y, end_y), (0, scrn_height)) * sensitivity_factor)
                            # ==== Mouse Pointer Movement ==============================
                            state = "Указатель мыши"
                            cv2.circle(Main_img, (px, py), 5, (200, 200, 200), cv2.FILLED)
                            cv2.circle(Main_img, (px, py), 10, (200, 200, 200), 3)
                            mouse.position = (int(pointer_x), int(pointer_y))

                            # print(Index_finger_in, Pinky_Finger_in)

                            # Если выдвинут указ и мизинец
                            if Index_Finger and Pinky_Finger:
                                # Подсчет расстояния между указ и мизинцем
                                [dis, centre] = Hand_detector.findDistance(Main_img, 1, 4)

                                # print(f'Dis/Base {dis/dis_base}')

                                if centre and dis:

                                    state = f"Click {click}, count: {click_counter}"

                                    # Проверка необходимости клика
                                    click, click_counter = mouse_pointer_click(centre, dis, click, click_counter, thr = dynamic_thr)
                                    # print(f'outer click_counter: {click_counter}')
                                    # print(f'outer click: {click}')
                                    # Если нужно сделать клик
                                    if click:
                                        # Выполнить клик
                                        mouse.position = (int(pointer_x), int(pointer_y))
                                        mouse.click(Button.left)
                                        # print("Normal Click index and pinky up")


                                # Trigger mouse click action
                                # Выполнить клик мышью
                                # mouse.click(Button.left)  # Perform a left-click
                                # print("Test Click index and pinky up")

                        # elif V_dir == 0:
                        #     print('V_dir == 0')
                        #     pass

                        # Если выбрано направление "вниз", т.е. указ и средний выдвинуты
                        # ИЛИ V_dir == 0
                        else:

                            # IF vertical direction is not +ve then left-click or quit-check wil happen

                            # Подсчет расстояния между указ и мизинцем
                            [dis, centre] = Hand_detector.findDistance(Main_img, 1, 4)

                            # Если указ и средний в окне выхода и больше никаких пальцев не выдвинуто
                            if (Index_fing_qt and Pinky_Finger) and sum_of_finger_state <= 3:
                                """If Index in quit button box,then check for click in it."""
                                state = "Quit Check"
                                if centre and dis:
                                    click, click_counter = mouse_pointer_click(centre, dis, click, click_counter,
                                                                               thr=dynamic_thr)
                                    # Если нужно кликнуть, т.е. пальцы близко друг к другу
                                    # То поднять флаг выхода
                                    if click: Quit_confirm = True

                            # Если выбрано направление "вниз", т.е. указ и средний выдвинуты и пройдена проверка на расстояние и центр?
                            if V_dir == -1 and (centre and dis):
                                """If vertial direction is -ve then check for mouse left-click"""
                                state = "Click mouse"

                                # Проверка необходимости клика
                                click = mouse_pointer_click(centre, dis, click)
                                # Если нужно сделать клик
                                if click:
                                    # Если до этого клик не делался
                                    if (clk == 0):
                                        # Выполнить клик
                                        mouse.position = (int(pointer_x), int(pointer_y))
                                        mouse.click(Button.left)
                                        clk += 1
                                        # print("Normal Click index and pinky up")

                                    #Если клик уже делался
                                    else:
                                        # Уменьшить счетчик кликов
                                        clk -= 1
                                    # ==========================================================
                    # Если выбран режим управления стрелкам
                    if Controller_Mode == 1:
                        """Controller mode -> 1; is Keys control mode
                        Available Keys controls are Left, Right, Up, Down & Space bar press"""
                        # Horizontal direction control
                        if H_dir == 1:
                            keyboard.press(Key.right)
                        elif H_dir == -1:
                            keyboard.press(Key.left)
                        else:
                            keyboard.release(Key.right)
                            keyboard.release(Key.left)

                        # Vertical direction control
                        if V_dir == 1:
                            keyboard.press(Key.up)
                        elif V_dir == -1:
                            keyboard.press(Key.down)
                        else:
                            keyboard.release(Key.up)
                            keyboard.release(Key.down)

                        # Space-bar/Jump control
                        if Jump == 1:
                            keyboard.press(Key.space)
                        else:
                            keyboard.release(Key.space)
        # ======================================================================
        # Puttign Text onto the Image for user to get the states & controls & othe r info required
        cv2.putText(Main_img, f'MOUSE', (start_x + 60, start_y + 30), Font_type, Font_size, Font_color, 2)
        cv2.putText(Main_img, f'ARROW', (mid_x + 60, start_y + 30), Font_type, Font_size, Font_color, 2)

        cv2.line(Main_img, (mid_x, start_y), (mid_x, hand_start_y), (10, 10, 250), 2)
        cv2.rectangle(Main_img, (start_x, start_y), (end_x, end_y), (10, 10, 250), 2)
        cv2.rectangle(Main_img, (hand_start_x, hand_start_y), (hand_end_x, hand_end_y), (10, 10, 250), 2)

        cv2.putText(Main_img, f'DETECTION :- {Hand_Detection_check}', (40, 20), Font_type, Font_size, Font_color,
                    Font_thickness)
        cv2.putText(Main_img, f'STATE :-{state}', (250, 20), Font_type, Font_size, Font_color, Font_thickness)

        cv2.putText(Main_img, f'QUIT', (start_x - 65, start_y + 30), Font_type, Font_size, Font_color, 2)
        cv2.rectangle(Main_img, (start_x - 100, start_y), (start_x, hand_start_y), (10, 10, 250), 2)
        # ======================================================================
        if Controller_Mode == 0:
            type_controller = "Mouse"
        elif Controller_Mode == 1:
            type_controller = "Arrow"
        else:
            type_controller = "None"
        cv2.putText(Main_img, f"Control Type:-{type_controller}", (250, 40), Font_type, Font_size, Font_color,
                    Font_thickness)
        # ======= Displaying the FPS of the CV Apk =============================
        fps = 1 / (cur_time - prev_time)
        prev_time = cur_time
        cv2.putText(Main_img, f'FPS:- {int(fps)}', (40, 40), Font_type, Font_size, (90, 140, 185), Font_thickness)
        # ======== Displaying the Main Image ===================================
        title = 'Computer Vision' # .encode('utf-8').decode('windows-1251')
        # print(title)
        cv2.imshow(title, Main_img)

        # sleep(0.1)
        # window = gw.getWindowsWithTitle('Game Controller')[0]  # Get the window by title
        # window.move(window.left + 25, window.top)

        # move_window('Game Controller', 100 + 10, 100)

        if cv2.waitKey(10) == ord("q"): Quit_confirm = True
        # ======= Quiting the apk ==============================================
        if Quit_confirm:
            say('Quitting')
            sleep(1)
            break


# ============================================
def start_gesture_control():
    gesture_control()