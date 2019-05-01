from sys import platform

from Platform.Linux import Linux
from Platform.Win32 import Win32


class PlatformFactory:
    def getClassByPlatform(self):
        if platform == "win32":
            return Win32()
        elif platform == "linux" or platform == "linux2":
            return Linux()
        else:
            raise Exception('Unknown platform!')
