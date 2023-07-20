//**********************************************************
//* Customer Display Management
//**********************************************************
function DisplayObject(eposdev, properties){

	//**********************************************************
	//* Constants
	//**********************************************************
	this.STR_DEPOSIT	= "Cash",
	this.STR_CHANGE		= "Change";
	this.STR_SUBTOTAL	= "Subtotal";
	this.STR_INITMES	= "Welcome to Epson sample shop";
	//**********************************************************
	//* Variables
	//**********************************************************
	this.deviceObj = null;
	this.eposdev = eposdev;
	this.prop = properties;
	this.retry = 0;
	this.SPLITED = false;
	this.status = "";

	var self = this;
	function cbCreateDevice(deviceObj, code){
		self.status = code;
		self.retry++;
		if ( code == "OK" ){
			self.deviceObj = deviceObj;
			self.DisplayMarquee();
			self.retry = 0;
		} else if ( code == "DEVICE_IN_USE" ){
			if (self.retry < 5) {
				setTimeout(function () {
					self.eposdev.createDevice(self.prop.deviceId, self.eposdev.DEVICE_TYPE_DISPLAY,
						{crypto : self.prop.crypto, buffer : self.prop.buffer},
						cbCreateDevice);
				}, 3000);
				self.status = "RETRY";
			}
		}
		uiDeviceStateArea.ShowDeviceStatus("display", self.status);
	}
	eposdev.createDevice(this.prop.deviceId, this.eposdev.DEVICE_TYPE_DISPLAY,
						{crypto : this.prop.crypto, buffer : this.prop.buffer},
						cbCreateDevice);
}

DisplayObject.prototype = {

	/**
	 * Display Marquee String
	*/
	DisplayMarquee : function(){
		if ( this.status != "OK" )	return;
		this.deviceObj.reset();
		this.deviceObj.setCursorType("none");
		this.deviceObj.addMarquee(this.STR_INITMES, this.deviceObj.MARQUEE_WALK, 550, 1000, 0);
		this.deviceObj.send();
		this.SPLITED = false;
	},

	/**
	* Display String at register item
	*
	* @param	itemName	string		 Character string to express a product name
	* @param	itemPrice		int		 Unit price of a product
	* @param	subtotal		int		 Subtotal
	*
	* @return				void
	*/
	DisplayPrice : function(itemName, itemPrice, subTotal){
		if ( this.status != "OK" )	return;
		if ( this.SPLITED == false ) this.SplitWindow();

		this.deviceObj.setCurrentWindow(1);
		this.deviceObj.clearWindow();
		if ( itemName != "" ){
			this.deviceObj.addText(itemName);
		}

		this.deviceObj.setCurrentWindow(2);
		this.deviceObj.clearWindow();
		this.deviceObj.moveCursorPosition(this.deviceObj.MOVE_BOTTOM_RIGHT);
		if (itemPrice != "") {
			this.deviceObj.addText(formatter.formatAmount(itemPrice));
		}

		this.deviceObj.setCurrentWindow(3);
		this.deviceObj.clearWindow();
		this.deviceObj.addText(this.STR_SUBTOTAL);

		this.deviceObj.setCurrentWindow(4);
		this.deviceObj.clearWindow();
		this.deviceObj.moveCursorPosition(this.deviceObj.MOVE_BOTTOM_RIGHT);
		this.deviceObj.addText(formatter.formatAmount(subTotal));
		this.deviceObj.send();
	},

	/**
	* Display caption, value, and subtotal.
	* @param	caption		Display string 1
	* @param	value		Display string 2
	* @param	subtotal	Subtotal
	*/
	DisplayDescription : function(caption, value, subtotal){
		if ( this.status != "OK" )	return;
		if ( this.SPLITED == false ) this.SplitWindow();

		this.deviceObj.setCurrentWindow(1);
		this.deviceObj.addText(caption);

		this.deviceObj.setCurrentWindow(2);
		this.deviceObj.clearWindow();
		this.deviceObj.moveCursorPosition(this.deviceObj.MOVE_BOTTOM_RIGHT);
		this.deviceObj.addText(value);

		this.deviceObj.setCurrentWindow(3);
		this.deviceObj.clearWindow();
		this.deviceObj.addText(this.STR_SUBTOTAL);

		this.deviceObj.setCurrentWindow(4);
		this.deviceObj.clearWindow();
		this.deviceObj.moveCursorPosition(this.deviceObj.MOVE_BOTTOM_RIGHT);
		this.deviceObj.addText(formatter.formatAmount(subTotal));
		this.deviceObj.send();
	},

	/**
	* Display String at Payment
	*
	* @param	deposit	int
	* @param	change	int
	*
	* @return			void
	*/
	DisplayTotal : function (deposit, change) {
		if ( this.status != "OK" )	return;
		if ( this.SPLITED == false ) this.SplitWindow();

		this.deviceObj.setCurrentWindow(1);
		this.deviceObj.clearWindow();
		this.deviceObj.addText(this.STR_DEPOSIT);
		this.deviceObj.setCurrentWindow(2);
		this.deviceObj.clearWindow();
		this.deviceObj.moveCursorPosition(this.deviceObj.MOVE_BOTTOM_RIGHT);
		this.deviceObj.addText(formatter.formatAmount(deposit));
		this.deviceObj.setCurrentWindow(3);
		this.deviceObj.clearWindow();
		this.deviceObj.addText(this.STR_CHANGE);
		this.deviceObj.setCurrentWindow(4);
		this.deviceObj.clearWindow();
		this.deviceObj.moveCursorPosition(this.deviceObj.MOVE_BOTTOM_RIGHT);
		this.deviceObj.addText(formatter.formatAmount(change));
		this.deviceObj.send();
	},

	/**
	* Split Custumor Display into four Windows
	*/
	SplitWindow : function () {
		this.deviceObj.reset();
		this.deviceObj.setCursorType(this.deviceObj.CURSOR_NONE);
		this.deviceObj.createWindow(1, 1, 1, 12, 1, this.deviceObj.SCROLL_OVERWRITE);
		this.deviceObj.createWindow(2, 13, 1, 8, 1, this.deviceObj.SCROLL_HORIZONTAL);
		this.deviceObj.createWindow(3, 1, 2, 12, 1, this.deviceObj.SCROLL_OVERWRITE);
		this.deviceObj.createWindow(4, 13, 2, 8, 1, this.deviceObj.SCROLL_HORIZONTAL);
		this.SPLITED = true;
	}
};
