if __name__ == "__main__":
    from sys import argv
    from os import listdir
    from importlib import import_module

    available = []
    for fn in listdir("commands"):
        if fn[-3:] == ".py" and fn != ".py":
            available.append(fn[:-3])
    if len(available) < 1:
        raise Exception("No Script found!")
    opt = ""
    if len(argv) > 1:
        opt = argv[1]
    while opt not in available:
        opt = input("Script? ")

    module = import_module("commands." + opt)