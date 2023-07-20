//**********************************************************
//* Object of control display area for transaction amount
//**********************************************************
function UIAmountArea () {
	this.UI_ELEMENT = {
		TOTAL:			document.getElementById("Total"),
		DEPOSIT:		document.getElementById("Deposit"),
		CHANGE:			document.getElementById("Change"),
	};
	this.total = 0;
	this.deposit = 0;
	this.InitArea();
}

UIAmountArea.prototype = {
	/**
	* Return to the initial state
	*/
	InitArea : function () {
		this.UpdateTotal(0);
		this.UpdateDeposit(0);
		this.UpdateChange(0);
	},

	/**
	* Get total amount
	* @return	Total amount
	*/
	GetTotal : function () {
		return this.total;
	},
	/**
	* Update display of total amount
	* @param	amount	total amount
	*/
	UpdateTotal : function (amount) {
		this.total = amount;
		this.UI_ELEMENT.TOTAL.innerHTML = formatter.formatAmount(amount, formatter.TYPE.HTML);
	},

	/**
	* Get deposit amount
	* @return	Deposit amount
	*/
	GetDeposit : function () {
		return ( this.deposit == 0 ) ? "" : this.deposit;
	},
	/**
	* Update display of deposit amount
	* @param	amount	Deposit amount
	*/
	UpdateDeposit : function (amount) {
		this.deposit = amount;
		this.UI_ELEMENT.DEPOSIT.innerHTML = formatter.formatAmount(amount, formatter.TYPE.HTML);
	},

	/**
	* Update display of change amount
	* @param	amount	Change amount
	*/
	UpdateChange : function (amount) {
		this.UI_ELEMENT.CHANGE.innerHTML = formatter.formatAmount(amount, formatter.TYPE.HTML);
	},

	/**
	* Change the display style in each mode
	*/
	ChangeAreaStyle : function (mode) {
		switch(mode){
			case MODE.MODE_REGISTER:
			case MODE.MODE_QUANTITY:
				this.UI_ELEMENT.DEPOSIT.style.backgroundColor = "inherit";
				break;
			case MODE.MODE_PAYMENT:
				this.UI_ELEMENT.DEPOSIT.style.backgroundColor = "#6A8ABD";
				break;
		}
	},
};
