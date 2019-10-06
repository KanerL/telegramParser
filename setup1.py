import sys
from cx_Freeze import setup, Executable
executables = [
         Executable('main.py'),
         Executable('main_server.py')
     ]
setup(name='tgPars',
           version='version',
           description='desc',
           executables=executables,
        )
