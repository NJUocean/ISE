import subprocess

subprocess.call("pip3 install clang==6.0", shell = True)
subprocess.call("pip3 install pyinstaller", shell = True)
subprocess.call("pyinstaller -F codesim.py", shell = True)
subprocess.call("sudo cp dist/codesim /usr/local/bin/", shell = True)
print ("Setup done!")
