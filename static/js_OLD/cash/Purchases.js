//**********************************************************
//* Item List management
//**********************************************************
function Purchases() {
	this.itemList = new Array();
	this.isDiscount = false;
	this.memberCode = "";
}

Purchases.prototype = {
	/**
	* Add item info to the list
	* @param	item	item information
	*					{id:ID of item list, itemCode:Item code, name:Item name, unitPrice:unit price, quantity:quantity}
	*/
	Add : function(item){
		this.itemList.push(item);
	},

	/**
	* Get item info from the list
	* @param	index	Index number
	*/
	GetByIndex : function(index){
		if ( this.itemList.length <= index )	return null;
		return this.itemList[index];
	},

	/**
	* Get item info by ID
	* @param	id	ID
	*/
	GetById : function(id){
		for(var i=0; i<this.itemList.length; i++){
			if ( this.itemList[i]['id'] == id) {
				break;
			}
		}
		if ( i == this.itemList.length ){
			return null;
		} else {
			return this.itemList[i];
		}
	},

	/**
	* Get item info by item code
	* @param	itemCode	Item code
	*/
	GetByItemCode : function(itemCode){
		for(var i=0; i<this.itemList.length; i++){
			if ( this.itemList[i]['itemCode'] == itemCode) {
				break;
			}
		}
		if ( i == this.itemList.length ){
			return null;
		} else {
			return this.itemList[i];
		}
	},

	/**
	* Remove item from the list by ID
	* @param	id	Remove target ID
	*/
	Remove : function(id){
		for(var i=0; i<this.itemList.length; i++){
			if ( this.itemList[i]['id'] == id) {
				this.itemList.splice(i, 1);
				break;
			}
		}
	},

	/**
	* Remove all items from the list
	*/
	RemoveAll : function (init) {
		this.isDiscount = false;
		if ( this.itemList.length == 0 )	return;
		this.itemList.splice(0, this.itemList.length);
	},

	/**
	* Change item quantity of specified ID
	* @param	id			Change target ID
	* @param	quantity	Change number
	*/
	UpdateQuantity : function (id, quantity) {
		for(var i=0; i < this.itemList.length; i++) {
			if ( this.itemList[i]['id'] == id ){
				this.itemList[i]['quantity'] = quantity;
				break;
			}
		}
	},

	/**
	* Get the list length
	*/
	Count : function(){
		return this.itemList.length;
	},

	/**
	*  Get the total amount of registration items
	*/
	GetTotalAmount : function(){
		var total = 0;
		for(var i=0; i < this.itemList.length; i++) {
			total += this.itemList[i]['quantity'] * this.itemList[i]['unitPrice'];
		}
		return total;
	},

	/**
	 * Calculate total net amount
	 *
	 * @return			number	Total net amount
	 */
	GetTotalNet : function(){
		return this.GetTotalAmount() - this.GetTax();
	},

	/**
	 * Calculate tax
	 *
	 * @param	total	number	Total amount
	 * @return			number	Tax
	 */
	GetTax : function(){
		return Math.round(this.GetTotalAmount() * 5 / 105)
	},

};
