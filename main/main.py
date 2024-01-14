# This is a sample Python script.
from barcode.barcode_scanner import BarcodeScanner
from barcode.user_interface.user_interface import UserInterface


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    # Create an instance of BarcodeScanner
    scanner = BarcodeScanner()
    user_inferface = UserInterface()
    user_inferface.run()
    # Start the barcode scanning loop
    # scanner.scan()

if __name__ == '__main__':
    main()