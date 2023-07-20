const escpos = require('escpos');

const device  = new escpos.USB(0x1a86, 0x7584, 0, 0x82, 0x02);
// const device  = new escpos.RawBT();
// const device  = new escpos.Network('localhost');
// const device  = new escpos.Serial('/dev/usb/lp0');
const printer = new escpos.Printer(device);

device.open(function(){
  printer
  .font('a')
  .align('ct')
  .style('bu')
  .size(1, 1)
  .text('INTIC, INC.')
  .text('FACTURA #: 123')
  .text('SR. GRACIA MOREIRA JAVIER ISAIAS')
  .feed()
  .feed()
  .feed()
  .cut()
  .close();
});