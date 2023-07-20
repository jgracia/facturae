//**********************************************************
//* Controller object of item list view area
//**********************************************************
function UIItemListArea () {
	this.STYLE = {
		NORMAL : "ItemRowStyle",
		SELECT : "ItemRowSelectStyle"
	};

	this.UI_ELEMENT_ID = {
		ITEM_QUANTITY:	"Quantity",
		ITEM_SUM:		"Sum"
	};

	this.UI_ELEMENT = {
		ITEM_LIST:		document.getElementById("ItemList"),
		ITEM_HEIGHT:	document.getElementById("ItemHeight"),
		ITEM_LIST_AREA:	document.getElementById("ItemListArea"),
		SUBTOTAL:		document.getElementById("SubTotal"),
	};
	this.BUTTON = {
		REMOVEITEM:		document.getElementById("RemoveItemButton"),
		REMOVEALLITEMS:	document.getElementById("RemoveAllItemsButton")
	}
	this.curSelectId = "";
	this.curSelQuantityElm = null;
	this.curSelPriceElm = null;
	this.itemCount = 0;
	this.InitArea();
	this.InitScrollPosition();
}

UIItemListArea.prototype = {
	/**
	* Return to initial state
	*/
	InitArea : function () {
		this.UpdateSubTotal(0);
		this.RemoveAll();
		this.curSelectId = "";
		this.itemCount = 0;
	},

	/**
	* Add item to the list
	* HTML structure of the item information are as follows
	* <div id="xxxx" className="ItemRow1Style" mousedown="ItemSelect(xxxx);">
	* 	<div className="ItemCol1Style">
	* 		<div className="ItemDivTable">
	* 			<div className="ItemDivCell">
	* 				<div className="ItemDiv"></div>
	* 			</div>
	* 		</div>
	* 	</div>
	* 	<div className="ItemCol2Style">
	* 		<div className="ItemDivTable">
	* 			<div className="ItemDivCell">
	* 				<div className="ItemDiv"></div>
	* 			</div>
	* 		</div>
	* 	</div>
	* 	<div className="ItemCol3Style">
	* 		<div className="ItemDivTable">
	* 			<div className="ItemDivCell">
	* 				<div id="Quantityxxxx" className="ItemDiv"></div>
	* 			</div>
	* 		</div>
	* 	</div>
	* 	<div className="ItemCol4Style">
	* 		<div className="ItemDivTable">
	* 			<div className="ItemDivCell">
	* 				<div id="Sumxxxx" className="ItemDiv"></div>
	* 			</div>
	* 		</div>
	* 	</div>
	* </div>
	*
	* @param	item	Item info
	*					{id:Item list ID, itemCode:Item code, name:Item name, unitPrice:Item unit price, quantity:Item quantity}
	*/
	AddItem : function(item){
		var itemRow = document.createElement('div');
		itemRow.className = "ItemRow1Style";
		itemRow.id = item.id;
		var self = this;
		itemRow.addEventListener("mousedown", function () { self.ItemSelect(item.id); }, false);

		// Create item name part
		var itemColName = document.createElement('div');
		itemColName.className = "ItemCol1Style";
		var itemDivTable = document.createElement('div');
		itemDivTable.className = "ItemDivTable";
		var itemDivCell = document.createElement('div');
		itemDivCell.className = "ItemDivCell";
		var itemDiv = document.createElement('div');
		itemDiv.className = "ItemDiv";
		itemDiv.innerHTML = item.name;

		itemDivCell.appendChild(itemDiv);
		itemDivTable.appendChild(itemDivCell);
		itemColName.appendChild(itemDivTable);
		itemRow.appendChild(itemColName);

		// Create unit price part
		var itemColPrice = document.createElement('div');
		itemColPrice.className = "ItemCol2Style";
		var itemDivTable = document.createElement('div');
		itemDivTable.className = "ItemDivTable";
		var itemDivCell = document.createElement('div');
		itemDivCell.className = "ItemDivCell";
		var itemDiv = document.createElement('div');
		itemDiv.className = "ItemDiv";
		itemDiv.innerHTML = formatter.formatAmount(item.unitPrice, formatter.TYPE.HTML);

		itemDivCell.appendChild(itemDiv);
		itemDivTable.appendChild(itemDivCell);
		itemColPrice.appendChild(itemDivTable);
		itemRow.appendChild(itemColPrice);

		// Create quantity part
		var itemColQuantity = document.createElement('div');
		itemColQuantity.className = "ItemCol3Style";
		var itemDivTable = document.createElement('div');
		itemDivTable.className = "ItemDivTable";
		var itemDivCell = document.createElement('div');
		itemDivCell.className = "ItemDivCell";
		var itemDiv = document.createElement('div');
		itemDiv.className = "ItemDiv";
		itemDiv.id = "Quantity" + item.id;
		itemDiv.innerHTML = item.quantity;

		itemDivCell.appendChild(itemDiv);
		itemDivTable.appendChild(itemDivCell);
		itemColQuantity.appendChild(itemDivTable);
		itemRow.appendChild(itemColQuantity);

		// Create amount part
		var itemColSum = document.createElement('div');
		itemColSum.className = "ItemCol4Style";
		var itemDivTable = document.createElement('div');
		itemDivTable.className = "ItemDivTable";
		var itemDivCell = document.createElement('div');
		itemDivCell.className = "ItemDivCell";
		var itemDiv = document.createElement('div');
		itemDiv.className = "ItemDiv";
		itemDiv.id = "Sum" + item.id;
		var sum = item.unitPrice * item.quantity;
		itemDiv.innerHTML = formatter.formatAmount(sum, formatter.TYPE.HTML);

		itemDivCell.appendChild(itemDiv);
		itemDivTable.appendChild(itemDivCell);
		itemColSum.appendChild(itemDivTable);
		itemRow.appendChild(itemColSum);

		this.UI_ELEMENT.ITEM_LIST.appendChild(itemRow);
		this.ItemSelect(item.id);
		this.itemCount++;
		this.ChangeButtonStyle();
	},

	/**
	* Remove element of specified id from the list
	* @param	id	string	Element id for remove
	*/
	Remove : function(id){
		var element = document.getElementById(id);
		if ( element ){
			this.UI_ELEMENT.ITEM_LIST.removeChild(element);
		}
		this.curSelectId = "";
		this.itemCount--;
		this.ChangeButtonStyle();
	},

	/**
	* Remove all elements from the list
	*/
	RemoveAll : function(){
		while (this.UI_ELEMENT.ITEM_LIST.firstChild) {
			this.UI_ELEMENT.ITEM_LIST.removeChild(this.UI_ELEMENT.ITEM_LIST.firstChild);
		}
		this.itemCount = 0;
		this.InitScrollPosition();
		this.ChangeButtonStyle();
	},

	/**
	*Make item which was clicked selected state
	* @param	id	string	Id of the selected element
	*/
	ItemSelect : function (id) {
		// Disable if MODE is Change Quantity Mode or Payment Mode
		if (ModeFlag == MODE.MODE_QUANTITY || ModeFlag == MODE.MODE_PAYMENT) return;

		// Change appearance of item which has been selected to non-selected state
		var element = document.getElementById(this.curSelectId);
		if ( element ) element.className = this.STYLE.NORMAL;

		// Change appearance of item which is selected to selected state
		element = document.getElementById(id);
		element.className = this.STYLE.SELECT;

		// Save the position information of the selected item
		this.curSelectId = id;
		this.curSelQuantityElm = document.getElementById(this.UI_ELEMENT_ID.ITEM_QUANTITY + this.curSelectId);
		this.curSelPriceElm = document.getElementById(this.UI_ELEMENT_ID.ITEM_SUM + this.curSelectId);
		this.ChangeButtonStyle();
	},

	/**
	* Get id of currently selected
	*/
	GetCurSelId : function(){
		return this.curSelectId;
	},

	/**
	* Check list has been selected
	*/
	IsItemSelect : function(){
		return ( this.curSelectId != "" ) ? true : false;
	},

	/**
	* Get quantity of currently selected
	* @return	quantity
	*/
	GetCurQuantity : function(){
		return ( this.curSelQuantityElm ) ? this.curSelQuantityElm.innerHTML : 0;
	},

	/**
	* Update quantity of currently selected
	* @param	str		Quantity
	*/
	UpdateCurQuantity : function(str){
		if ( this.curSelQuantityElm ){
			this.curSelQuantityElm.innerHTML = Number(str);
		}
	},

	/**
	* Update price of currently selected
	* @param	str		Price
	*/
	UpdateCurPrice : function(str){
		if ( this.curSelPriceElm ){
			this.curSelPriceElm.innerHTML = formatter.formatAmount(str, formatter.TYPE.HTML);
		}
	},

	/**
	* Change subtotal on POS application UI
	*
	* @param	str		string	Subtotal
	*/
	UpdateSubTotal : function(amount){
		this.UI_ELEMENT.SUBTOTAL.innerHTML = formatter.formatAmount(amount, formatter.TYPE.HTML);
	},

	/**
	* Initialize scroll position of registerd item list
	*/
	InitScrollPosition : function () {
		this.UI_ELEMENT.ITEM_LIST.style.top = 0 + "px";
	},

	/**
	*  Switch enable/disable of RemoveItemButton, RemoveAllItemsButton
	*/
	ChangeButtonStyle : function(){
		this.BUTTON.REMOVEITEM.disabled = this.IsItemSelect() ? false : true;
		this.BUTTON.REMOVEALLITEMS.disabled = (this.itemCount == 0) ? true : false;
	},

	/**
	* Change the display style of the quantity area
	*/
	ChangeAreaStyle : function (mode){
		if ( !this.curSelQuantityElm )	return;
		if ( mode == MODE.MODE_QUANTITY ){
			this.curSelQuantityElm.parentNode.parentNode.style.backgroundColor = "#FF8000";
		} else {
			this.curSelQuantityElm.parentNode.parentNode.style.backgroundColor = "inherit";
		}
	},
};
