import xlwt
import base64
from io import BytesIO
from PIL import Image

def generate_xls_report(self, workbook, data, partners):
    sheet = workbook.add_sheet("Reporte")
    
    row = 0
    for partner in partners:
        # Escribir el nombre
        sheet.write(row, 0, partner.name)
        
        # Obtener la imagen
        if partner.image_1920:
            image_data = base64.b64decode(partner.image_1920)
            image = Image.open(BytesIO(image_data))
            
            # Guardar la imagen en un archivo temporal
            image_path = "/tmp/temp_image.bmp"
            image.save(image_path, "BMP")
            
            # Insertar imagen en Excel
            sheet.insert_bitmap(image_path, row, 1) 
        
        row += 1