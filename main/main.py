# from main.user_interface import UserInterface
from user_interface import UserInterface

def main():
    print('Opstarten van de app, even geduld a.u.b.')
    user_inferface = UserInterface()
    print('App opgestart')
    user_inferface.run()

if __name__ == '__main__':
    main()