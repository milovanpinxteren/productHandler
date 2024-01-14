import keyboard

from barcode.user_interface.user_interface import UserInterface


class BarcodeScanner:
    def __init__(self):
        # Initialization code for BarcodeScanner
        pass

    def scan(self):
        barcode = ""
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "enter":
                    print(f"Scanned Barcode: {barcode}")
                    #TODO: send to Untappd (get info)8720615262519

                    #TODO: create interface and start webcam

                    barcode = ""
                else:
                    barcode += event.name