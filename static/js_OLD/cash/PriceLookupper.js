//**********************************************************
//* Search the database of item information
//**********************************************************
function PriceLookupper() {
	this.onLookupSuccess = null;
	this.items = {
		"1000000001013" : {"name" : "T-shirt",      "dname" : "T-shirt",      "price" : "25"},
		"1000000001020" : {"name" : "Sox",          "dname" : "Sox",          "price" :  "6"},
		"1000000001037" : {"name" : "Skirt",        "dname" : "Skirt",        "price" : "34"},
		"1000000001044" : {"name" : "Leggings",     "dname" : "Leggings",     "price" : "20"},
		"1000000001051" : {"name" : "Jacket",       "dname" : "Jacket",       "price" : "80"},
		"1000000001068" : {"name" : "Parka",        "dname" : "Parka",        "price" : "70"},
		"1000000001075" : {"name" : "Camisole top", "dname" : "Camisole top", "price" : "20"},
		"1000000001082" : {"name" : "Jeans",        "dname" : "Jeans",        "price" : "90"},
		"1000000001099" : {"name" : "Cut & Sewn",   "dname" : "Cut & Sewn",   "price" : "45"},
		"1000000001105" : {"name" : "Pullover",     "dname" : "Pullover",     "price":  "38"},
		"1000000001110" : {"name" : "Test",         "dname" : "Test",         "price":  "58"},
		"1000000001120" : {"name" : "Ejemplo",      "dname" : "Ejemplo",      "price":  "68"}
	};
}


PriceLookupper.prototype = {
	/**
	 * Get item information from the item code
	 * @param	itemCode	Number of item code
	 */
	Lookup: function (itemCode) {
		var item = this.items[itemCode];
		if ( item != undefined ){
			this.onLookupSuccess(itemCode, item.name, item.dname, item.price);
		} else {
			this.onLookupSuccess("");
		}
	}
};
