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
pdf.newMargin();

code='01234567890123456789';
pdf.Code128(10,80,code,82,10);
pdf.set_font('arial', '', 8.5)
pdf.set_xy(119,90);
pdf.write(4,'A set: "'+code+'"')
#pdf.cell(5,'A set: "'+code+'"');

pdf.set_fill_color(255);
pdf.RoundedRect(60, 30, 68, 46, 5, '123', 'DF');

pdf.output('D://firma/factura.pdf', 'F')

os.system("D://firma/factura.pdf")