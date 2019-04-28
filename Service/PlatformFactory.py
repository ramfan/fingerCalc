from sys import platform

from Platform.Win32 import Win32


class PlatformFactory:
    def getClassByPlatform(self):
        if platform == "win32":
            return Win32()
        elif platform == "linux" or platform == "linux2":
            return
        elif platform == "darwin":
            return
        else:
            raise Exception('Unknown platform!')
