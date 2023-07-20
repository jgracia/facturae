// Address and Port to connect
var ipAddress = '192.168.192.168';
var port = '8008';

var printerProp = {
	deviceId :	"local_printer",
	deviceUse :	true,
	crypto :	true,
	buffer :	false,
};
var lineDisplayProp = {
	deviceId :	"local_display",
	deviceUse :	true,
	crypto :	true,
	buffer :	false,
};
var scannerProp = {
	deviceId :	"local_scanner",
	deviceUse :	true,
	crypto :	true,
	buffer :	false,
};
var keyboardProp = {
	deviceId :	"local_keyboard",
	deviceUse :	true,
	crypto :	true,
	buffer :	false,
};

var PAPER_WIDTH = {
	PAPER_WIDTH_58MM: 0, 	// 58mm Reciept
	PAPER_WIDTH_80MM: 1		// 80mm Reciept
};
// Define the paper width for receipt
var PRINTER_PAPER_WIDTH = PAPER_WIDTH.PAPER_WIDTH_80MM;
