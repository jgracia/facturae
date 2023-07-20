function CustomerDisplayController(eposdevice)
{
	this.commbox = null;
	this.commBoxManager = eposdevice.getCommBoxManager();
	if ( this.commBoxManager == null ){
		throw new Error('The eposdev connection is not completed.');
	}

	this.isOpenCommBox = false;

	this.OK = "OK";
	this.ERROR_COMMBOX_NOT_OPEN = "ERROR_COMMBOX_NOT_OPEN";
	this.SIGNAGE_IMAGE = "img";
	this.SIGNAGE_VIDEO = "video";
	this.LAYOUT_BASED_ON_HEIGHT = "BASED_ON_HEIGHT";
	this.LAYOUT_BASED_ON_WIDTH = "BASED_ON_WIDTH";
}

CustomerDisplayController.prototype = {
	open : function()
	{
		var self = this;
		this.commBoxManager.openCommBox("CustomerDisplay", null,
			function(commbox, code){
				if ( code == "OK" ){
					self.commbox = commbox;
					self.commbox.onreceive = onreceive;
					self.isOpenCommBox = true;
				}
			});
		function onreceive(data)
		{
			if ( !('response' in data.message) || !('params' in data.message ) ){
				return;
			}
			switch( data.message.response ){
				case "actionReply" :
					try {
						self.onactionreply(data.message.params.value);
					} catch(e) {}
					break;
				default :
					break;
			}
		}
	},

	close : function()
	{
		if ( this.commbox == null )	return;
		this.commBoxManager.closeCommBox(this.commbox, null);
		this.commbox = null;
		this.isOpenCommBox = true;
	},

	showPrice : function(description, price)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showPrice", params : {description : description, price : price}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showAmount : function(caption, amount)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showAmount", params : {caption : caption, amount : amount}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showTotal : function(caption, total)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showTotal", params : {caption : caption, total : total}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showCash : function(caption, cash)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showCash", params : {caption : caption, cash : cash}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showChange : function(caption, change)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showChange", params : {caption : caption, change : change}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showGreeting : function(caption)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showGreeting", params : {caption : caption}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	hideNoticeWindow : function(id)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "hideNoticeWindow", params : {id : id}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	displayNoticeWindow : function(id)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "displayNoticeWindow", params : {id : id}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showSignage : function(type, uri, layout)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showSignage", params : {type : type, uri : uri, layout : layout}};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	registerSignage : function(signageInfoList)
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "registerSignage", params : signageInfoList};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	showRegisteredSignage : function()
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "showRegisteredSignage", params : null};
		this.commbox.send(message, null, null);
		return this.OK;
	},

	maximaizeSignage : function()
	{
		if ( !this.isOpenCommBox )	return this.ERROR_COMMBOX_NOT_OPEN;
		var message = {request : "maximaizeSignage", params : null};
		this.commbox.send(message, null, null);
		return this.OK;
	},
};
