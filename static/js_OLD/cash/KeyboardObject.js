//**********************************************************
//* Keyboard object
//**********************************************************
function KeyboardObject(eposdev, properties) {
	this.eposdev = eposdev;
	this.prop = properties;
	this.retry = 0;
	this.status = "";

	var self = this;
	function cbCreateDevice(deviceObj, code){
		self.status = code;
		self.retry++;
		if (code == "OK") {
			deviceObj.setPrefix([deviceObj.VK_F2, deviceObj.VK_F12]);
			deviceObj.onkeypress = self.onkeypress;
			deviceObj.onstring = self.onstring;
			self.retry = 0;
		} else if (code == "DEVICE_IN_USE") {
			if (self.retry < 5) {
				setTimeout(function () {
					self.eposdev.createDevice(self.prop.deviceId,
											self.eposdev.DEVICE_TYPE_KEYBOARD,
											{crypto : self.prop.crypto, buffer : self.prop.buffer},
											cbCreateDevice);
				}, 3000);
				self.status = "RETRY";
			}
		}
		uiDeviceStateArea.ShowDeviceStatus("keyboard", self.status);
	}
	eposdev.createDevice(this.prop.deviceId, this.eposdev.DEVICE_TYPE_KEYBOARD,
						{crypto : this.prop.crypto, buffer : this.prop.buffer},
						cbCreateDevice);
}

KeyboardObject.prototype = {
	onkeypress : function (data) {
		var reg = /[0-9]/;
		if ( reg.test(data.ascii) ){
			cashRegister.onNumber(data.ascii);
		}

		switch( data.keycode ) {
			case 117:	cashRegister.onDoubleZero();	break;	//"00"(F6)
			case 118:	cashRegister.onTenThousand();	break;	//"10000"(F7)
			case 114:	cashRegister.onClear();			break;	//"c"(F3)
			case 115:	cashRegister.onQuantity();		break;	//"Qty"(F4)
			case 116:	cashRegister.onSubtotal();		break;	//"Subtotal"(F5)
			case 13:	cashRegister.onCash();			break;	//"Ent"(Enter)
			default:	break;
		}
	},

	onstring : function (data){
		switch (data.prefix) {
			case 113:
				cashRegister.onItemCodeData(data.input);
				break;

			case 123:
				switch( data.input.charAt(0) ) {
					case "o":	cashRegister.onKeyLock(true);	break;
					case "r":	cashRegister.onKeyLock(false);	break;
					default:	break;
				}
				break;

			default:
				break;
		}
	},
};
