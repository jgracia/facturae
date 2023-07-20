function UIDeviceStateArea(){
}

UIDeviceStateArea.prototype = {
	/**
	* Update connection status of TM-DT
	*/
	ShowConnectStatus : function (status, device) {
		if ( (status == "reconnecting") || (status == "clear") ){
			$('#status_printer').html("");
			$('#status_display').html("");
			$('#status_keyboard').html("");
			$('#status_scanner').html("");
			$('#indicator_printer').html("");
			$('#indicator_display').html("");
			$('#indicator_keyboard').html("");
			$('#indicator_scanner').html("");

		} else if ( status == "reconnect" ){
			this.ShowDeviceStatus("printer", printer.status);
			this.ShowDeviceStatus("display", display.status);
			this.ShowDeviceStatus("keyboard", keyboard.status);
			this.ShowDeviceStatus("scanner", scanner.status);
		}
	},

	/**
	* Update device status
	*/
	ShowDeviceStatus : function(deviceName, status){
		var indicatorElmName = '#indicator_' + deviceName;
		var statusElmName = '#status_' + deviceName;
		var content = "";
		switch( status ){
			case "OK":		content = '<img src="img/ok.png" alt="OK" title="OK">';	break;
			case "RETRY":	content = '<img src="img/loader.gif" alt="Loading" title="Loading">';	break;
			default:		content = '<img src="img/ng.png" alt="NG" title="NG">';	break;
		}
		$(indicatorElmName).html(content);
		$(statusElmName).html(status);
	},
};
