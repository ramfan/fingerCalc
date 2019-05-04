import warnings

try:
    import win32com.client
    from pyautogui import hotkey, keyDown, keyUp, press
    from Platform.AbstractPlatform import AbstractPlatform


    class Win32(AbstractPlatform):
        def __init__(self):
            print("win32")

        def __shell_dispatcher_actions(self, key):
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys(key)
            self.set_sleep()

        def press_space(self):
            self.__shell_dispatcher_actions(" ")

        def arrow_down(self):
            self.__shell_dispatcher_actions("{DOWN}")

        def arrow_left(self):
            self.__shell_dispatcher_actions("{LEFT}")

        def arrow_right(self):
            self.__shell_dispatcher_actions("{RIGHT}")

        def arrow_up(self):
            self.__shell_dispatcher_actions("{UP}")

        def win_arrow_right(self):
            hotkey('ctrl', 'win', 'right')
except ImportError:
    class Win32:
        def __init__(self):
            warnings.warn('win32com failed to import', ImportWarning)
