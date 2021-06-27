def main():
    from library.Repeater import Repeater

    repeater = Repeater(min=1)
    while repeater.loop():
        print("START")