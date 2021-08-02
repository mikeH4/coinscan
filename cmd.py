if __name__ == "__main__":
    from sys import argv
    from importlib import import_module

    module = ""
    if len(argv) > 1:
        module = argv[1]
    
    while True:
        try:
            import_module(module)
            exit()
        except ModuleNotFoundError:
            try:
                module = input("Script? ")
            except KeyboardInterrupt: exit()