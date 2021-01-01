import os, shutil

exclude = [
    "asyncio", "concurrent", "ctypes", "disutils", "email", "html", "http", "lib2to3", "logging",
    "multiprocessing", "pydoc_data", "test", "tkinter", "unittest", "urllib", "xml", "xmlrpc"]

if os.path.isdir("dist"):
    shutil.rmtree("dist")
os.system("cxfreeze -c -OO cli.py --target-dir dist --excludes " + ",".join(exclude))

os.chdir("dist/lib")
for file in os.listdir():
    if file not in ["collections", "encodings", "importlib", "rpg", "library.zip"]:
        if os.path.isfile(file):
            os.remove(file)
        else:
            shutil.rmtree(file)