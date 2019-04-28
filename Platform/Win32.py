import win32com.client

from Platform.AbstractPlatform import AbstractPlatform


class Win32(AbstractPlatform):
    def __init__(self):
        print("win32")

    def press_space(self):
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys(" ")
        self.set_sleep()

