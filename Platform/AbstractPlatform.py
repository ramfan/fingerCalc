import time
from abc import ABC, abstractmethod


class AbstractPlatform:

    def set_sleep(self):
        time.sleep(0.2)

    @abstractmethod
    def press_space(self):
        pass

    @abstractmethod
    def arrow_down(self):
        pass

    @abstractmethod
    def arrow_up(self):
        pass

    @abstractmethod
    def arrow_right(self):
        pass

    @abstractmethod
    def arrow_left(self):
        pass
