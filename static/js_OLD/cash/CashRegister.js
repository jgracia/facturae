//**********************************************************
//* Main control of application
//**********************************************************
function CashRegister(){
	this.STYLE = {
		NORMAL : "ItemRowStyle",
		SELECT : "ItemRowSelectStyle"
	};
	this.UI_ELEMENT_ID = {
		ITEM_QUANTITY:	"Quantity",
		ITEM_SUM:		"Sum"
	};
	this.UI_ELEMENT = {
		ITEM_CODE:		document.getElementById("ItemCode"),
	};
	this.BUTTON = {
		REMOVEITEM:		document.getElementById("RemoveItemButton"),
		REMOVEALLITEMS:	document.getElementById("RemoveAllItemsButton")
	}

	var self = this;
	var ua = navigator.userAgent;
	var eventName = (ua.indexOf('iPhone') > -1 || ua.indexOf('iPad') > -1 || ua.indexOf('iPod') > -1) ? "touchstart" : "mousedown";
	document.getElementById("QuantityButton").addEventListener(		eventName, function(){self.onQuantity(); }, false);
	document.getElementById("ClearButton").addEventListener(		eventName, function(){self.onClear();},	false);
	document.getElementById("OneButton").addEventListener(			eventName, function(){self.onNumber(1);},	false);
	document.getElementById("TwoButton").addEventListener(			eventName, function(){self.onNumber(2);},	false);
	document.getElementById("ThreeButton").addEventListener(		eventName, function(){self.onNumber(3);},	false);
	document.getElementById("FourButton").addEventListener(			eventName, function(){self.onNumber(4);},	false);
	document.getElementById("FiveButton").addEventListener(			eventName, function(){self.onNumber(5);},	false);
	document.getElementById("SixButton").addEventListener(			eventName, function(){self.onNumber(6);},	false);
	document.getElementById("SevenButton").addEventListener(		eventName, function(){self.onNumber(7);},	false);
	document.getElementById("EightButton").addEventListener(		eventName, function(){self.onNumber(8);},	false);
	document.getElementById("NineButton").addEventListener(			eventName, function(){self.onNumber(9);},	false);
	document.getElementById("ZeroButton").addEventListener(			eventName, function(){self.onNumber(0);},	false);
	document.getElementById("DoubleZeroButton").addEventListener(	eventName, function(){self.onDoubleZero();},false);
	document.getElementById("TenThousandButton").addEventListener(	eventName, function(){self.onTenThousand();},false);
	document.getElementById("SubtotalButton").addEventListener(		eventName, function(){self.onSubtotal();}, false);
	document.getElementById("CashButton").addEventListener(			eventName, function(){self.onCash(); }, false);
	document.getElementById("RemoveItemButton").addEventListener(	eventName, function(){self.onRemove(); }, false);
	document.getElementById("RemoveAllItemsButton").addEventListener(eventName,function(){self.onRemoveAll(); }, false);

	this.purchases = new Purchases();
	this.isKeyLock = false;
	this.timerId = null;
	this.InitScreen();
}

CashRegister.prototype = {
	/**
	* Return to the initial state
	*/
	InitScreen : function(){
		this.UI_ELEMENT.ITEM_CODE.innerHTML = "";
		uiAmountArea.InitArea();
		uiItemListArea.InitArea();
		this.ChangeMode(MODE.MODE_REGISTER);
	},

	/**
	* Process when QuantityButton is pushed
	* Switch to Change Quantity Mode
	*/
	onQuantity : function () {
		if ( ModeFlag == MODE.MODE_QUANTITY || ModeFlag == MODE.MODE_PAYMENT ) return;
		if ( !uiItemListArea.IsItemSelect() ) return;

		// Switch to Change Quantity Mode
		this.ChangeMode(MODE.MODE_QUANTITY);
		uiItemListArea.UpdateCurQuantity("");
	},

	/**
	 * Process when ClearButton is pushed
	 * Clear the current input area
	 */
	onClear : function () {
		switch(ModeFlag) {
			case MODE.MODE_REGISTER:
				this.UI_ELEMENT.ITEM_CODE.innerHTML = "";
				break;
			case MODE.MODE_QUANTITY:
				uiItemListArea.UpdateCurQuantity("");
				break;
			case MODE.MODE_PAYMENT:
                uiAmountArea.UpdateDeposit(0);
				break;
			default:
				break;
		}
	},

	/**
	 * Process when NumberButton to 0-9 is pushed
	 * Insert a number into the current input area
	 */
	onNumber : function (num) {
		switch(ModeFlag) {
			case MODE.MODE_REGISTER:
				// Input item code if MODE is Register Item Mode
				var itemCode = this.UI_ELEMENT.ITEM_CODE.innerHTML;
				if(itemCode.length < 13) {
					itemCode += num
					this.UI_ELEMENT.ITEM_CODE.innerHTML = itemCode;
				}
				if ( itemCode.length != 13 ) return;

				// Get item information from item code
				priceLookupper.Lookup(itemCode);
				break;

			case MODE.MODE_QUANTITY:
				// Input Quantity if MODE is Change Quantity Mode
				if ( !uiItemListArea.IsItemSelect() )	return;
				var str = String(uiItemListArea.GetCurQuantity());
				str += num
				uiItemListArea.UpdateCurQuantity(str);
				break;

			case MODE.MODE_PAYMENT:
				// Input deposit value if MODE is Payment Mode
				var strAmount = String(uiAmountArea.GetDeposit());
				strAmount += num
				uiAmountArea.UpdateDeposit(strAmount);
				break;
			default:
				break;
		}
	},

	/**
	 * Process when DoubleZeroButton is pushed
	 * Add "00" to current input value
	 */
	onDoubleZero : function () {
		switch(ModeFlag) {
			case MODE.MODE_REGISTER:
				var itemCode = this.UI_ELEMENT.ITEM_CODE.innerHTML;
				itemCode += "00";
				if(itemCode.length >= 13) {
					itemCode = itemCode.substring(0, 13);
					priceLookupper.Lookup(itemCode);
				}
				this.UI_ELEMENT.ITEM_CODE.innerHTML = itemCode;
				break;
			case MODE.MODE_QUANTITY:
				break;
			case MODE.MODE_PAYMENT:
				var amount = uiAmountArea.GetDeposit();
				amount = 100 * amount;
				uiAmountArea.UpdateDeposit(amount);
				break;
		}
	},

	/**
	 * Process when TenThousandButton is pushed
	 * Add "10,000" only at deposit
	 */
	onTenThousand : function () {
		if(ModeFlag == MODE.MODE_REGISTER || ModeFlag == MODE.MODE_QUANTITY) return;

		// Add "10,000" to current value
		var amount = Number(uiAmountArea.GetDeposit());
		amount += 10000;
		uiAmountArea.UpdateDeposit(amount);
	},

	/**
	* Process when CashButton is pushed
	* Establish changed quantity if MODE is Change Quantity Mode
	* Execute process about payment if MODE is Payment Mode
	*/
	onCash : function () {
		switch (ModeFlag) {
			case MODE.MODE_REGISTER:
				break;
			case MODE.MODE_QUANTITY:
				var quantity = uiItemListArea.GetCurQuantity();
				quantity = (quantity == "" || quantity == "0") ? 1 : quantity;
				this.purchases.UpdateQuantity(uiItemListArea.GetCurSelId(), quantity);
				var purchase = this.purchases.GetById(uiItemListArea.GetCurSelId());
				uiItemListArea.UpdateCurQuantity(purchase.quantity);
				uiItemListArea.UpdateCurPrice(purchase.quantity * purchase.unitPrice);

				this.RedisplayTotal();
				if (display !== null) {
					display.DisplayPrice("", "", this.purchases.GetTotalAmount());
				}
				if (hfDisplay !== null){
					hfDisplay.DisplayPrice("", "", this.purchases.GetTotalAmount());
				}

				// Switch to Register Item Mode
				this.ChangeMode(MODE.MODE_REGISTER);
				break;

			case MODE.MODE_PAYMENT:
				var total = uiAmountArea.GetTotal();
				var deposit = uiAmountArea.GetDeposit();
				if ( total > deposit ){
					alert("Cash is less than subtotal.");
					return;
				}
				uiAmountArea.UpdateChange(deposit - total);

				// Indicate to Customer Display
				if (display !== null) {
					display.DisplayTotal(deposit, deposit - total);
				}
				if (hfDisplay !== null){
					hfDisplay.DisplayTotal(deposit, deposit - total);
				}

				// Print reciept
				if　(printer !== null){
					printer.PrintReciept(PRINTER_PAPER_WIDTH, this.purchases);
				}

				// Initialize after wait specification time if print successed
				var self = this;
				clearInterval(this.timerId);
				this.timerId = setInterval(function () {
					if ( (printer === null) || (printer.finish) ){
						clearInterval(self.timerId);
						self.purchases.RemoveAll();
						self.InitScreen();
						if (display !== null) {
							display.DisplayMarquee();
						}
						if (hfDisplay !== null){
							hfDisplay.Init();
						}
						self.ChangeMode(MODE.MODE_REGISTER);
					}
				}, 5000);
				break;
			default:
				break;
		}
	},

	/**
	 * Process when SubTotalButton is pushed
	 * Switch to Payment Mode
	 */
	onSubtotal : function () {
		if ( ModeFlag == MODE.MODE_QUANTITY ||
			 ModeFlag == MODE.MODE_PAYMENT ||
			 this.purchases.Count() == 0 )
			 return;
		this.ChangeMode(MODE.MODE_PAYMENT);
	},

	/**
	* Process when RemoveItemButton is pushed
	* Delete selecting item from the list
	*/
	onRemove : function () {
		// Disable if MODE is Payment Mode
		if ( ModeFlag == MODE.MODE_PAYMENT )	return;

		this.purchases.Remove(uiItemListArea.GetCurSelId());
		uiItemListArea.Remove(uiItemListArea.GetCurSelId());
		this.RedisplayTotal();

		this.ChangeMode(MODE.MODE_REGISTER);
	},

	/**
	* Process when RemoveAllItemsButton is pushed
	* Delete all items from the list
	*/
	onRemoveAll : function () {
		// Disable if MODE is Payment Mode or item list is empty
		if ( ModeFlag == MODE.MODE_PAYMENT || this.purchases.Count() == 0)	return;

		// Display warning dialogue
		if ( confirm('Delete all items. Will that be all right?') ){
			this.purchases.RemoveAll();
			uiItemListArea.InitArea();
			uiAmountArea.InitArea();
			if (display !== null) {
				display.DisplayPrice("", "", this.purchases.GetTotalAmount());
			}
			if (hfDisplay !== null){
				hfDisplay.DisplayPrice("", "", this.purchases.GetTotalAmount());
			}
			this.ChangeMode(MODE.MODE_REGISTER);
		}
	},

	/**
	* Callback of product information notification
	*/
	onLookupSuccess : function(itemCode, name, phonetic, unitPrice){
		cashRegister.UI_ELEMENT.ITEM_CODE.innerHTML = "";
		if ( itemCode == "" ){
			alert("Can not find specified item code.");
			return;
		}

		var purchase = this.purchases.GetByItemCode(itemCode);
		if ( purchase != null ){
			// Increment quantity of the item if the item have already been added
			purchase.quantity++;
			uiItemListArea.ItemSelect(purchase.id);
			uiItemListArea.UpdateCurQuantity(purchase.quantity);
			uiItemListArea.UpdateCurPrice(purchase.quantity * purchase.unitPrice);
		} else {
			// Register the item in quantity 1
			purchase = { id:this.GetUniqueID(), itemCode:itemCode, name:name, phonetic:phonetic, unitPrice:unitPrice, quantity:1 };
			this.purchases.Add(purchase);
			uiItemListArea.AddItem(purchase);
		}
		this.RedisplayTotal();
		this.ChangeMode(MODE.MODE_REGISTER);

		// Indicate to Customer Display
		if (display !== null) {
			display.DisplayPrice(phonetic, unitPrice, this.purchases.GetTotalAmount());
		}
		if (hfDisplay !== null){
			hfDisplay.DisplayPrice(name, unitPrice, this.purchases.GetTotalAmount());
		}
	},

	/**
	* Process when receiving item code (barcode)
	*/
	onItemCodeData : function(code){
		if ( ModeFlag == MODE.MODE_QUANTITY ||
			 ModeFlag == MODE.MODE_PAYMENT ||
			 this.isKeyLock ){
			return;
		}
		cashRegister.UI_ELEMENT.ITEM_CODE.innerHTML = code;
		priceLookupper.Lookup(code);
	},

	/**
	* Process when receiving KeyLock from keyboard device
	*/
	onKeyLock : function(enable){
		var value = enable ? "block" : "none";
		document.getElementById('overlay').style.display = value;
		document.getElementById('modalbox').style.display = value;

		this.isKeyLock = enable;
	},

	/**
	 * Recalculate and display total amount when the item list is updated
	 */
	RedisplayTotal : function(){
		var total = this.purchases.GetTotalAmount();

		uiItemListArea.UpdateSubTotal(total);
		uiAmountArea.UpdateTotal(total);
	},

	/**
 	 * Generate a unique value
 	 *
 	 * @return	String	Unique value
	 */
	GetUniqueID : function(){
		var randam = Math.floor(Math.random() * 1000)
		var date = new Date();
		var time = date.getTime();
		return randam + time.toString();
	},

	/**
	* Change the display style in each mode
	*/
	ChangeMode : function (mode) {
		ModeFlag = mode;
		uiItemListArea.ChangeAreaStyle(mode);
		uiAmountArea.ChangeAreaStyle(mode);
		this.BUTTON.REMOVEITEM.disabled = uiItemListArea.IsItemSelect() ? false : true;
		this.BUTTON.REMOVEALLITEMS.disabled = (this.purchases.Count() == 0) ? true : false;

		switch(mode){
			case MODE.MODE_REGISTER:
				this.UI_ELEMENT.ITEM_CODE.style.backgroundColor = "#6A8ABD";
				break;
			case MODE.MODE_QUANTITY:
			case MODE.MODE_PAYMENT:
				this.UI_ELEMENT.ITEM_CODE.style.backgroundColor = "inherit";
				break;
		}
	},
};
