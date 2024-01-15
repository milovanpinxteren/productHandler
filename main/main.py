from barcode.barcode_scanner import BarcodeScanner
from barcode.user_interface.user_interface import UserInterface




def main():
    # Create an instance of BarcodeScanner
    # scanner = BarcodeScanner()
    user_inferface = UserInterface()
    user_inferface.run()
    # Start the barcode scanning loop
    # scanner.scan()

if __name__ == '__main__':
    main()