if __name__ == "__main__":
    from sys import argv
    from importlib import import_module
    import os

    print("\nServices:")
    services = [
        file[:-3]
        for file
        in os.listdir("./services")
        if file[-3:] == ".py"
    ]
    print("\n".join(services))
    print("")
    
    service = ""
    if len(argv) > 1: service = argv[1]
    
    while True:
        if service in services:
            print("-- -- -- -- -- -- -- -- -- -- --")
            print(f"Running {service}")
            print("-- -- -- -- -- -- -- -- -- -- --\n")
            module = import_module(f"services.{service}")
            module.main() # type: ignore
            exit()
        else:
            service = input("Service? ")