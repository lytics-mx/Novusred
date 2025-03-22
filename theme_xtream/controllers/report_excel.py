import base64
import io
import xlsxwriter
from PIL import Image
from odoo.http import Controller, request, route

class ReportExcelController(Controller):

    @route('/export/excel', type='http', auth='user')
    def export_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Reporte")

        row = 0
        col = 0

        products = request.env['product.product'].search([])

        for product in products:
            sheet.write(row, col, product.name)

            if product.image_1920:
                image_data = base64.b64decode(product.image_1920)
                image = Image.open(io.BytesIO(image_data))

                image_path = "/tmp/temp_image.png"
                image.save(image_path, "PNG")

                # Insertar imagen
                sheet.insert_image(row, col + 1, image_path, {'x_scale': 0.2, 'y_scale': 0.2})

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