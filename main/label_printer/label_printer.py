from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
from brother_ql.conversion import convert
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

class LabelPrinter:
    def print_label(self, product_title, product_price, untappd_score):
        label_size = '62x29' #62 BY 29 MM

        qlr = BrotherQLRaster('QL-820NWB')
        qlr.exception_on_warning = True
        # qlr.cut_at_end = False
        printer = 'tcp://169.254.76.236'
        title_font_size = 24
        title_font = ImageFont.truetype("arial.ttf", title_font_size)
        price_font_size = 30
        price_font = ImageFont.truetype("arialbd.ttf", price_font_size)
        untappd_font_size = 30
        untappd_font = ImageFont.truetype("arial.ttf", untappd_font_size)


        img = Image.new("RGB", (500, 100), "white")
        d = ImageDraw.Draw(img)
        wrapped_text = textwrap.fill(product_title, width=40)

        d.text((10, 10), wrapped_text, fill=(0, 0, 0), font=title_font)
        d.text((10, 65), product_price, fill=(0, 0, 0), font=price_font)
        d.text((260, 65), 'Untappd: ' + untappd_score, fill=(0, 0, 0), font=untappd_font)
        img = img.resize((696, 271))

        # Convert image to raster
        qlr = BrotherQLRaster("QL-820NWB")
        qlr.exception_on_warning = True
        converted_data = convert(qlr, [img], label=label_size, threshold=70, dither=True)

        # Save raster data to file
        output_path = Path("../temp.bin")
        with open(output_path, "wb") as f:
            f.write(converted_data)

        # Send data to printer
        # send(output_path.read_bytes(), printer_identifier=printer)
        response = send(output_path.read_bytes(), printer_identifier=printer)['did_print']
        return response





# label_printer = LabelPrinter()