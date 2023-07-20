//**********************************************************
//* Scanner object
//**********************************************************
function ScannerObject(eposdev, properties) {
	this.eposdev = eposdev;
	this.prop = properties;
	this.retry = 0;
	this.status = "";

	var self = this;
	function cbCreateDevice(deviceObj, code){
		self.status = code;
		self.retry++;
		if ( code == "OK" ){
			deviceObj.ondata = self.ondata;
			self.retry = 0;
		} else if (code == "DEVICE_IN_USE") {
			if ( self.retry < 5 ){
				setTimeout(function () {
					self.eposdev.createDevice(self.prop.deviceId,
											self.eposdev.DEVICE_TYPE_SCANNER,
											{crypto : self.prop.crypto, buffer : self.prop.buffer},
											cbCreateDevice);
				}, 3000);
				self.status = "RETRY";
			}
		}
		uiDeviceStateArea.ShowDeviceStatus("scanner", self.status);
	}
	eposdev.createDevice(this.prop.deviceId,
						this.eposdev.DEVICE_TYPE_SCANNER,
						{crypto : this.prop.crypto, buffer : this.prop.buffer},
						cbCreateDevice);
}

ScannerObject.prototype = {
	ondata : function(data){
		cashRegister.onItemCodeData(data.input);
	},
};
