import glob

for file in glob.glob("rpg/**/*.py", recursive=True):
    with open(file, "r") as f:
        a = f.read()
    
    lines = a.rstrip().splitlines()
    for line in lines:
        if line.startswith("import "):
            module = line[7:]
            if module + "." not in a:
                print(file, module)