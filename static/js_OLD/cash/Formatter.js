function Formatter(){
	this.currencyMark = "$";
	this.currencyMarkP = "$";
	this.separator = ",";
	this.TYPE = {
		HTML : 1,
		PRINT : 2,
	};
}
Formatter.prototype = {
	/**
	 * Format the amount to display
	 * @param	str	String	String to put a comma to separate thousands
	 * @return		String	String containing a comma to separate thousands
	 */
	formatAmount : function(amount, type){
		var fmtdAmount = new String(amount).replace(/,/g, "");
		while(fmtdAmount != (fmtdAmount = fmtdAmount.replace(/^(-?\d+)(\d{3})/, "$1" + this.separator + "$2")));

		if ( type == this.TYPE.HTML ){
			fmtdAmount = this.currencyMark + fmtdAmount;
		} else {
			fmtdAmount = this.currencyMarkP + fmtdAmount;
		}
		return fmtdAmount;
	},
}
