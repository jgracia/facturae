function HfDisplayObject(eposdev){

	//**********************************************************
	//* Constants
	//**********************************************************
	this.STR_DEPOSIT	= "Cash",
	this.STR_CHANGE		= "Change";
	this.STR_SUBTOTAL	= "Subtotal";
	this.STR_WELCOME	= "Welcome to Epson sample shop";
	this.STR_SEEYOU		= "Please visit us again soon";
	//**********************************************************
	//* Variables
	//**********************************************************
	this.eposdev = eposdev;
	this.cdc = new CustomerDisplayController(eposdev);
	this.cdc.open();

	var self = this;
	var retryCount = 0;
	this.intervalId = setInterval(
						function(){
							if ( self.cdc.isOpenCommBox || retryCount < 5 ){
								clearInterval(self.intervalId);
								self.DisplaySignage();
							}
							retryCount++;
						}, 2000);
}

HfDisplayObject.prototype = {

	/**
	* Display image
	*/
	DisplaySignage : function(){
		var imgs = [
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/01.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/02.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/03.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/04.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/05.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/06.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
			{type:this.cdc.SIGNAGE_IMAGE, uri:"./img/07.jpg", layout:this.cdc.LAYOUT_BASED_ON_HEIGHT, displaytime:15},
		];
		this.cdc.registerSignage(imgs);
		this.cdc.showGreeting(this.STR_WELCOME);
		this.cdc.showPrice("", 0);
		this.cdc.showAmount("", 0)
		this.cdc.showChange("", 0);
		this.cdc.showRegisteredSignage();
		this.cdc.maximaizeSignage();
	},

	/**
	* Initialization
	*/
	Init : function(){
		this.cdc.showPrice("", 0);
		this.cdc.showAmount("", 0)
		this.cdc.showChange("", 0);
		this.cdc.showGreeting(this.STR_WELCOME);
		this.cdc.maximaizeSignage();
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
	DisplayPrice : function (itemName, itemPrice, subTotal) {
		this.cdc.showPrice(itemName, itemPrice);
		this.cdc.showAmount(this.STR_SUBTOTAL, subTotal)
	},

	/**
	* Display String at Payment
	*
	* @param	deposit	int		Deposit amount
	* @param	change	int		Change amount
	*
	* @return			void
	*/
	DisplayTotal : function (deposit, change) {
		this.cdc.showCash(this.STR_DEPOSIT, deposit);
		this.cdc.showChange(this.STR_CHANGE, change);
		this.cdc.showGreeting(this.STR_SEEYOU);
	},
};
