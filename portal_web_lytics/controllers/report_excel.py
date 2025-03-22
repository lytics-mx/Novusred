import base64
import io
import xlsxwriter
from PIL import Image
from odoo.http import Controller, request, route
import tempfile
import os

class ReportExcelController(Controller):

    @route('/export/excel', type='http', auth='user')
    def export_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Reporte")

        row = 0
        col = 0

        # Cambiar a product.template
        products = request.env['product.template'].search([])

        for product in products:
            sheet.write(row, col, product.name)

            if product.image_1920:
                image_data = base64.b64decode(product.image_1920)
                image = Image.open(io.BytesIO(image_data))

                # Guardar la imagen en un archivo temporal
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image_file:
                    image.save(temp_image_file.name, "PNG")
                    temp_image_path = temp_image_file.name

                # Insertar la imagen en el Excel
                sheet.insert_image(row, col + 1, temp_image_path, {'x_scale': 0.2, 'y_scale': 0.2})

                # Eliminar el archivo temporal
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)

            row += 1

        workbook.close()
        output.seek(0)

        # Descargar archivo Excel
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename="Reporte.xlsx"')
            ]
        )