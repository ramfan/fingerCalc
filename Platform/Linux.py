from subprocess import Popen, PIPE

from Platform.AbstractPlatform import AbstractPlatform


class Linux(AbstractPlatform):
    def __init__(self):
        self.__controller = Popen(["xte"], stdin=PIPE)
        print("Linux")

    def __key_press(self, key):
        self.__controller.communicate(input=key)
        self.set_sleep()

    def press_space(self):
        space = '''keydown space keyup space'''
        self.__key_press(space)

    def arrow_down(self):
        arrow_down = '''keydown Down keyup Down'''
        self.__key_press(arrow_down)

    def arrow_left(self):
        arrow_left = '''keydown Left keyup Left'''
        self.__key_press(arrow_left)

    def arrow_right(self):
        arrow_right = '''keydown Right keyup Right'''
        self.__key_press(arrow_right)

    def arrow_up(self):
        arrow_up = '''keydown Up keyup Up'''
        self.__key_press(arrow_up)
