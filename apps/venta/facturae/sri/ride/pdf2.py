# -*- coding: iso-8859-1 -*-

# @mail ep_niebla@hotmail.com, ep.niebla@gmail.com
# @version 1.0
import os
from barcode import BarCode
'''
import os
from fpdf import FPDF
'''
pdf = BarCode()
pdf.alias_nb_pages()
pdf.add_page()


pdf.set_fill_color(0);

code='12345678901234567890';
pdf.Code128(50,20,code,50,20);
pdf.set_font('arial', '', 13.0)
pdf.set_xy(50,45);
pdf.cell(ln=0, h=22.0, align='C', w=75.0, txt='A set: "'+code+'"', border=0)
#pdf.cell(5,'A set: "'+code+'"');

pdf.set_fill_color(255);
pdf.RoundedRect(60, 30, 68, 46, 5, '13', 'DF');

pdf.set_font('arial', '', 13.0)
pdf.set_xy(105.0, 8.0)
pdf.cell(ln=0, h=22.0, align='C', w=75.0, txt='Comprobante de Ejemplo', border=0)
pdf.set_line_width(0.0)
pdf.rect(15.0, 15.0, 170.0, 245.0)
pdf.set_line_width(0.0)
pdf.rect(95.0, 15.0, 10.0, 10.0)
#pdf.image('Serpiente.png', 20.0, 17.0, link='', type='', w=13.0, h=13.0)
pdf.set_font('arial', 'B', 16.0)
pdf.set_xy(95.0, 18.0)
pdf.cell(ln=0, h=2.0, align='C', w=10.0, txt='X', border=0)
pdf.set_font('arial', '', 8.0)
pdf.set_xy(105.0, 21.0)
pdf.cell(ln=0, h=4.0, align='C', w=75.0, txt='Original', border=0)
pdf.set_font('arial', 'B', 7.0)
pdf.set_xy(95.0, 21.5)
pdf.cell(ln=0, h=4.5, align='C', w=10.0, txt='COD.00', border=0)
pdf.set_line_width(0.0)
pdf.line(100.0, 25.0, 100.0, 57.0)
pdf.set_font('arial', 'B', 14.0)
pdf.set_xy(125.0, 25.5)
pdf.cell(ln=0, h=9.5, align='L', w=60.0, txt='00000001', border=0)
pdf.set_xy(115.0, 27.5)
pdf.cell(ln=0, h=5.5, align='L', w=10.0, txt='N\xba: ', border=0)
pdf.set_font('arial', 'B', 12.0)
pdf.set_xy(17.0, 32.5)
pdf.cell(ln=0, h=5.0, align='L', w=98.0, txt='EMPRESA', border=0)
pdf.set_font('arial', '', 12.0)
pdf.set_xy(115.0, 33.0)
pdf.cell(ln=0, h=7.0, align='L', w=60.0, txt='Fecha:', border=0)
pdf.set_xy(135.0, 33.0)
pdf.cell(ln=0, h=7.0, align='L', w=40.0, txt='19/02/2009', border=0)
pdf.set_line_width(0.0)
pdf.line(15.0, 57.0, 185.0, 57.0)
pdf.set_font('arial', '', 10.0)
pdf.set_xy(17.0, 59.0)
pdf.cell(ln=0, h=6.0, align='L', w=13.0, txt='Sr.(s):', border=0)
pdf.set_xy(35.0, 59.0)
pdf.cell(ln=0, h=6.0, align='L', w=140.0, txt='Mariano Reingart', border=0)
pdf.set_xy(17.0, 64.0)
pdf.cell(ln=0, h=6.0, align='L', w=18.0, txt='Domicilio:', border=0)
pdf.set_xy(35.0, 64.0)
pdf.cell(ln=0, h=6.0, align='L', w=125.0, txt='Siempreviva 12345', border=0)
pdf.set_xy(17.0, 69.0)
pdf.cell(ln=0, h=6.0, align='L', w=18.0, txt='Tel\xe9fono:', border=0)
pdf.set_xy(35.0, 69.0)
pdf.cell(ln=0, h=6.0, align='L', w=80.0, txt='+1-5555-5555', border=0)
pdf.set_xy(115.0, 69.0)
pdf.cell(ln=0, h=6.0, align='L', w=18.0, txt='Localidad:', border=0)
pdf.set_xy(133.0, 69.0)
pdf.cell(ln=0, h=6.0, align='L', w=42.0, txt='Springfield', border=0)
pdf.set_line_width(0.0)
pdf.line(15.0, 77.0, 185.0, 77.0)
pdf.set_xy(17.0, 80.0)
pdf.cell(ln=0, h=5.0, align='L', w=15.0, txt='IVA:', border=0)
pdf.set_xy(35.0, 80.0)
pdf.cell(ln=0, h=5.0, align='L', w=70.0, txt='Responsable', border=0)
pdf.set_xy(115.0, 80.0)
pdf.cell(ln=0, h=5.0, align='L', w=20.0, txt='CUIT:', border=0)
pdf.set_xy(135.0, 80.0)
pdf.cell(ln=0, h=5.0, align='L', w=40.0, txt='10-12345678-9', border=0)
pdf.set_line_width(0.0)
pdf.line(15.0, 88.0, 185.0, 88.0)
pdf.set_xy(17.0, 90.0)
pdf.cell(ln=0, h=5.0, align='L', w=48.0, txt='Fecha de Vencimiento Pago:', border=0)
pdf.set_xy(65.0, 90.0)
pdf.cell(ln=0, h=5.0, align='L', w=20.0, txt='23/07/1978', border=0)
pdf.set_xy(92.0, 90.0)
pdf.cell(ln=0, h=5.0, align='L', w=43.0, txt='Per\xedodo Facturado', border=0)
pdf.set_xy(125.0, 90.0)
pdf.cell(ln=0, h=5.0, align='L', w=20.0, txt='01/01/2009', border=0)
pdf.set_xy(150.0, 90.0)
pdf.cell(ln=0, h=5.0, align='L', w=20.0, txt='31/01/2009', border=0)
pdf.set_line_width(0.0)
pdf.line(15.0, 95.0, 185.0, 95.0)
pdf.set_line_width(0.0)
pdf.line(155.0, 95.0, 155.0, 230.0)
pdf.set_xy(20.0, 97.0)
pdf.cell(ln=0, h=5.0, align='L', w=125.0, txt='Descripci\xf3n', border=0)
pdf.set_xy(160.0, 97.0)
pdf.cell(ln=0, h=5.0, align='R', w=20.0, txt='Importe', border=0)
pdf.set_line_width(0.0)
pdf.line(15.0, 102.0, 185.0, 102.0)
pdf.set_xy(20.0, 103.0)
pdf.cell(ln=0, h=7.0, align='L', w=125.0, txt='Esto es una prueba y no es v\xe1lido como factura', border=0)
pdf.set_xy(160.0, 103.0)
pdf.cell(ln=0, h=7.0, align='R', w=20.0, txt='100,00', border=0)
pdf.set_line_width(0.0)
pdf.line(15.0, 230.0, 185.0, 230.0)
pdf.set_xy(20.0, 233.0)
pdf.cell(ln=0, h=5.0, align='L', w=95.0, txt='CAE N\xba', border=0)
pdf.set_xy(45.0, 233.0)
pdf.cell(ln=0, h=5.0, align='L', w=30.0, txt='01234567890', border=0)
pdf.set_font('arial', '', 12.0)
pdf.set_xy(105.0, 234.0)
pdf.cell(ln=0, h=9.0, align='R', w=45.0, txt='NETO GRAVADO:', border=0)
pdf.set_font('arial', 'B', 12.0)
pdf.set_xy(145.0, 234.0)
pdf.cell(ln=0, h=9.0, align='R', w=33.0, txt='100,00', border=0)
pdf.set_font('arial', '', 10.0)
pdf.set_xy(20.0, 238.0)
pdf.cell(ln=0, h=5.0, align='L', w=95.0, txt='Fecha Vto. CAE:', border=0)
pdf.set_xy(55.0, 238.0)
pdf.cell(ln=0, h=5.0, align='L', w=30.0, txt='19/02/2009', border=0)
pdf.set_font('arial', '', 12.0)
pdf.set_xy(125.0, 241.0)
pdf.cell(ln=0, h=9.0, align='R', w=25.0, txt='IVA 21%:', border=0)
pdf.set_font('arial', 'B', 12.0)
pdf.set_xy(145.0, 241.0)
pdf.cell(ln=0, h=9.0, align='R', w=33.0, txt='21,00', border=0)
pdf.interleaved2of5('0602201806070420611900110010010000000111234567811', 20.0, 243.5, w=0.50)
pdf.set_font('arial', 'B', 12.0)
pdf.set_xy(105.0, 251.0)
pdf.cell(ln=0, h=9.0, align='R', w=73.0, txt='121,00', border=0)
pdf.set_font('arial', '', 12.0)
pdf.set_xy(125.0, 251.0)
pdf.cell(ln=0, h=9.0, align='R', w=25.0, txt='Total:', border=0)
pdf.set_line_width(0.0)
pdf.rect(155.0, 252.0, 25.0, 7.0)
pdf.set_font('arial', '', 10.0)
pdf.set_xy(18.0, 253.0)
pdf.set_font('arial', 'B', 9.0)

pdf.cell(ln=0, h=7.0, align='L', w=120.0, txt='0602201806070420611900110010010000000111234567811', border=0)
pdf.output('D://firma/factura.pdf', 'F')

os.system("D://firma/factura.pdf")