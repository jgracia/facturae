//**********************************************************
//* Receipt printing management
//**********************************************************
function PrinterObject(eposdev, properties) {
	//**********************************************************
	//* Constants
	//**********************************************************
	this.TOTAL = "TOTAL";
	this.TOTALNET = "NET";
	this.TAX = "TAX";
	this.DEPOSIT = "CASH";
	this.CHANGE = "CHANGE";

	this.YEAR = "/";
	this.MONTH = "/";
	this.DAY = "";
	this.HOUR = ":";
	this.MINUTE = "";

	this.SHOPID = "SEIKO EPSON SHOP";
	this.ADDRESS = "Japan";
	this.TEL = "03-5530-XXXX";

	//**********************************************************
	//* Variables
	//**********************************************************
	this.deviceObj = null;
	this.eposdev = eposdev;
	this.prop = properties;
	this.retry = 0;
	this.status = "";
	// Slip number
	this.SeqNO = 1;
	this.Success = false;

	this.finish = false;

	var self = this;
	function cbCreateDevice(deviceObj, code){
		self.status = code;
		self.retry++;
		if ( code == "OK" ){
			self.deviceObj = deviceObj;
			self.deviceObj.onreceive = self.onreceive.bind(self);
			self.retry = 0;
		} else if ( code == "DEVICE_IN_USE" ){
			if ( self.retry < 5 ) {
				setTimeout(function () {
					self.eposdev.createDevice(self.prop.deviceId,
											self.eposdev.DEVICE_TYPE_PRINTER,
											{crypto : self.prop.crypto, buffer : self.prop.buffer},
											cbCreateDevice);
				}, 3000);
				self.status = "RETRY";
			}
		}
		uiDeviceStateArea.ShowDeviceStatus("printer", self.status);
	}
	eposdev.createDevice(this.prop.deviceId,
						this.eposdev.DEVICE_TYPE_PRINTER,
						{crypto : this.prop.crypto, buffer : this.prop.buffer},
						cbCreateDevice);
}

PrinterObject.prototype = {

	onreceive : function(res){
		// Obtain the print result and error code
		var msg = ' Print ' + (res.success ? ' Success ' : ' Failure ') + '\n Code:' + res.code + '\n Status:\n';

		// Obtain the printer status
		var asb = res.status;
		if (asb & this.deviceObj.ASB_NO_RESPONSE)		{	msg += ' No printer response\n';	}
		if (asb & this.deviceObj.ASB_PRINT_SUCCESS)		{	msg += ' Print complete\n';	}
		if (asb & this.deviceObj.ASB_DRAWER_KICK)		{	msg += ' Status of the drawer kick number 3 connector pin = "H"\n';	}
		if (asb & this.deviceObj.ASB_OFF_LINE)			{	msg += ' Offline status\n';	}
		if (asb & this.deviceObj.ASB_COVER_OPEN)		{	msg += ' Cover is open\n';	}
		if (asb & this.deviceObj.ASB_PAPER_FEED)		{	msg += ' Paper feed switch is feeding paper\n';	}
		if (asb & this.deviceObj.ASB_WAIT_ON_LINE)		{	msg += '  Waiting for online recovery\n';	}
		if (asb & this.deviceObj.ASB_PANEL_SWITCH)		{	msg += ' Panel switch is ON\n';	}
		if (asb & this.deviceObj.ASB_MECHANICAL_ERR)	{	msg += ' Mechanical error generated\n';	}
		if (asb & this.deviceObj.ASB_AUTOCUTTER_ERR)	{	msg += ' Auto cutter error generated\n';	}
		if (asb & this.deviceObj.ASB_UNRECOVER_ERR)		{	msg += ' Unrecoverable error generated\n';	}
		if (asb & this.deviceObj.ASB_AUTORECOVER_ERR)	{	msg += ' Auto recovery error generated\n';	}
		if (asb & this.deviceObj.ASB_RECEIPT_NEAR_END)	{	msg += ' No paper in the roll paper near end detector\n';	}
		if (asb & this.deviceObj.ASB_RECEIPT_END)		{	msg += ' No paper in the roll paper end detector\n';	}
		if (asb & this.deviceObj.ASB_SPOOLER_IS_STOPPED){	msg += ' Stop the spooler\n';	}
		// Display in the dialog box
		if ( res.success == false ){
			alert(msg);
		}
		this.Success = res.success;
		this.finish = true;
	},

	/**
	* Print reciept when payment
	*
	* @retrun			void
	*/
	PrintReciept : function (paperWidth, purchases) {

		//Open drawer
		this.deviceObj.addPulse(this.deviceObj.DRAWER_1, this.deviceObj.PULSE_100);

		//Header
		this.deviceObj.addTextAlign(this.deviceObj.ALIGN_CENTER);
		this.deviceObj.addImage(logocontext, 0, 0, 256, 60);
		this.deviceObj.addText('\n');
		this.deviceObj.addText(this.SHOPID);
		this.deviceObj.addText('\n');
		this.deviceObj.addText(this.ADDRESS);
		this.deviceObj.addText('\n');
		this.deviceObj.addText(this.TEL);
		this.deviceObj.addText('\n\n');
		this.deviceObj.addText('Thank you for shopping');
		this.deviceObj.addText('\n');

		switch(paperWidth) {
 			case PAPER_WIDTH.PAPER_WIDTH_58MM:
				 this.deviceObj.addText('Please visit us\n again soon');
				break;
			case PAPER_WIDTH.PAPER_WIDTH_80MM:
				this.deviceObj.addText('Please visit us again soon');
				break;
			default:
				break;
		}

		this.deviceObj.addText('\n\n');
		this.deviceObj.addText(this.getTimestamp());
		this.deviceObj.addText('\n');

		// Set the individual information of the product of the order list
		for(var i=0; ; i++){
			var purchase = purchases.GetByIndex(i)
			if ( purchase == null ){
				break;
			}
			var strPhonetic = "";
			var strPrice = "";
			var strQuantity = "";
			var strSubtotal = "";

			switch (paperWidth) {
				case PAPER_WIDTH.PAPER_WIDTH_58MM:
					// Product name
					var strName = this.to2ByteChar(purchase["name"]);
					strName = (strName + "            ").slice(0, 12);

					// Quantity
					strQuantity = '   ' + purchase["quantity"];;
					strQuantity = strQuantity.slice(strQuantity.length - 3, strQuantity.length);

					// Subtotal
					strSubtotal = '        ' + formatter.formatAmount(purchase["quantity"] * purchase["unitPrice"]);
					strSubtotal = strSubtotal.slice(strSubtotal.length - 8, strSubtotal.length);
					break;

				case PAPER_WIDTH.PAPER_WIDTH_80MM:
					// Product name
					var strName = this.to2ByteChar(purchase["name"]);
					strName = (strName + "                    ").slice(0, 20);

					// Quantity
					strQuantity = '   ' + purchase["quantity"];;
					strQuantity = strQuantity.slice(strQuantity.length - 3, strQuantity.length);

					// Subtotal
					strSubtotal = '             ' + formatter.formatAmount(purchase["quantity"] * purchase["unitPrice"]);
					strSubtotal = strSubtotal.slice(strSubtotal.length - 13, strSubtotal.length);
					break;

				default:
					break;
			}

			this.deviceObj.addText('\n');
			this.deviceObj.addText(strName);
			this.deviceObj.addText(strQuantity);
			this.deviceObj.addText(' ');
			this.deviceObj.addText(strSubtotal);
		}

		this.deviceObj.addText('\n\n');

		// Set total, net and tax for reciept printing
		var strTotal = formatter.formatAmount(purchases.GetTotalAmount());
		var strTotalNet = formatter.formatAmount(purchases.GetTotalNet());
		var strTax = formatter.formatAmount(purchases.GetTax());
		var strDeposit = formatter.formatAmount(uiAmountArea.GetDeposit());
		var strChange = formatter.formatAmount(uiAmountArea.GetDeposit() - purchases.GetTotalAmount());

		switch( paperWidth ){
			case PAPER_WIDTH.PAPER_WIDTH_58MM:
				// Total
				strTotal = '            ' + strTotal;
				strTotal = strTotal.slice(strTotal.length - 10, strTotal.length);

				// Net
				strTotalNet = '                            ' + strTotalNet;
				strTotalNet = strTotalNet.slice(strTotalNet.length - 24, strTotalNet.length);

				// Tax
				strTax = '                            ' + strTax;
				strTax = strTax.slice(strTax.length - 24, strTax.length);

				// Deposit
				strDeposit = '                             ' + strDeposit;
				strDeposit = strDeposit.slice(strDeposit.length - 25, strDeposit.length);

				// Change
				strChange = '           ' + strChange;
				strChange = strChange.slice(strChange.length - 9, strChange.length);
				break;

			case PAPER_WIDTH.PAPER_WIDTH_80MM:
				// Total
				strTotal = '                 ' + strTotal;
				strTotal = strTotal.slice(strTotal.length - 15, strTotal.length);

				// Net
				strTotalNet = '                                      ' + strTotalNet;
				strTotalNet = strTotalNet.slice(strTotalNet.length - 34, strTotalNet.length);

				// Tax
				strTax = '                                      ' + strTax;
				strTax = strTax.slice(strTax.length - 34, strTax.length);

				// Deposit
				strDeposit = '                                       ' + strDeposit;
				strDeposit = strDeposit.slice(strDeposit.length - 35, strDeposit.length);

				// Change
				strChange = '                ' + strChange;
				strChange = strChange.slice(strChange.length - 14, strChange.length);
				break;
			default:
				break;
		}

		// Net
		this.deviceObj.addTextDouble(true);
		this.deviceObj.addText(this.TOTALNET);
		this.deviceObj.addTextDouble(false);
		this.deviceObj.addText(strTotalNet);
		this.deviceObj.addText('\n');

		// Tax
		this.deviceObj.addTextDouble(true);
		this.deviceObj.addText(this.TAX);
		this.deviceObj.addTextDouble(false);
		this.deviceObj.addText(strTax);
		this.deviceObj.addText('\n');

		// Total
		this.deviceObj.addTextDouble(true);
		this.deviceObj.addText(this.TOTAL);
		this.deviceObj.addText(strTotal);
		this.deviceObj.addTextDouble(false);
		this.deviceObj.addText('\n\n');

		// Deposit
		this.deviceObj.addText(this.DEPOSIT);
		this.deviceObj.addText(strDeposit);
		this.deviceObj.addText('\n');

		// Change
		this.deviceObj.addTextDouble(true);
		this.deviceObj.addText(this.CHANGE);
		this.deviceObj.addText(strChange);
		this.deviceObj.addTextDouble(false);
		this.deviceObj.addText('\n\n');

		// Footer
		this.deviceObj.addTextAlign(this.deviceObj.ALIGN_CENTER);
		this.deviceObj.addText(purchases.Count() + ' lines');

		var strSeqNo = '0000' + this.SeqNO;
		strSeqNo = strSeqNo.slice(strSeqNo.length - 4, strSeqNo.length);
		this.deviceObj.addText(strSeqNo);
		this.deviceObj.addFeedLine(3);
		this.deviceObj.addCut(this.deviceObj.CUT_FEED);
		this.deviceObj.send();

		this.finish = false;

		// Increment slip number
		this.SeqNO += 1;
		// If Slip number is greater than 9999
		if (this.SeqNO > 9999) {
			// Initialize slip number
			this.SeqNO = 0;
		}
	},

	/**
	 * Generate String of current time
	 *
	 * @return			string	String of current time
	 */
	getTimestamp : function() {
		var now = new Date();

		// Year
		var year = now.getYear();
		if (year < 2000) {
			year += 1900;
		}
		year = year + this.YEAR;

		// Month
		var month = now.getMonth() + 1;
		if (month < 10) {
			month = "0" + month;
		}
		month = month + this.MONTH;

		// Date
		var date = now.getDate();
		if (date < 10) {
			date = "0" + date;
		}
		date = date + this.DAY;

		// Hour
		var hour = now.getHours();
		if (hour < 10) {
			hour = "0" + hour;
		}
		hour = hour + this.HOUR;

		// Minute
		var minute = now.getMinutes();
		if (minute < 10) {
			minute = "0" + minute;
		}
		minute = minute + this.MINUTE;

		// ex) 2012/02/20 13:25
		return year + month + date + " " + hour + minute;
	},

	to2ByteChar : function(str) {
		return str;
/*		return str.replace(/[A-Za-z0-9]/g, function(s) {
		    return String.fromCharCode(s.charCodeAt(0) + 0xFEE0);
		});
*/
	}

};
