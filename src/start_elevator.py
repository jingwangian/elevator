import configs

from apps.elevator import Elevator


def main():
    elevator = Elevator(current_floor=0)

    elevator.run()

if __name__ == '__main__':
    main()
