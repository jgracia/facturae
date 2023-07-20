$(function() {

  //decimal mask
  $(".currency").inputmask('currency',{rightAlign: true  });

  // función intermitente etiqueta cambio o vuelto|
  function blinker() {
    $('.blinking').fadeOut(500);
    $('.blinking').fadeIn(500);
  }
  setInterval(blinker, 2000);

  $('#amount_received').on('input',function(e){
    var monto = $("#dlg_grand_total").val();
    //var total = number_format(monto, 2);
    //var total = Number(monto.replace(/[^0-9.-]+/g,"")).toFixed(2);

    var total = toFloat(monto);
    var recibido = toFloat(this.value);
    var cambio = recibido - total;

    //console.log("Total: " + total);
    //console.log("Recibido: " + recibido);
    //console.log("Cambio: " + cambio);

    if ($.isNumeric(cambio) || recibido === null) {
      var simbolo = getCurrencySymbol('en-US', 'USD');
      if (cambio > 0)
        $("#lblexchange_money").text(simbolo + ' ' + cambio.toLocaleString());
      else
        $("#lblexchange_money").text(simbolo + ' ' + '0'.toLocaleString());
    }
  });

  var token = jQuery("#cashForm [name=csrfmiddlewaretoken]").val();

  $("#cashForm").submit(function(e){
    e.preventDefault();
    // alert(token);
    // var formData = $("#cashForm").serializeArray();
    // console.log(formData);



    var num_comprob = $('#numero_comprobante').val();
    var proveedor_id = $('#id_supplier').val();
    var importe_factura = toFloat($("#lblTotal").text());
    var token = jQuery("#cashForm [name=csrfmiddlewaretoken]").val();
    var importe_recibido = jQuery("#cashForm [name=importe_recibido]").val();

    /*console.log('token=' + token);
    console.log('num_comprob=' + num_comprob);
    console.log('proveedor_id=' + proveedor_id);
    console.log('importe_factura=' + importe_factura);
    console.log('importe_recibido=' + importe_recibido);*/

    $.ajax({
      url: "../../compra/pago_efectivo/",
      method:"POST",
      headers: {'X-CSRFToken': token },
      //data: formData
      data: {
        'num_comprobante': num_comprob,
        'importe_factura': importe_factura,
        'importe_recibido': importe_recibido,
        'proveedor_id': proveedor_id,
        'csrfmiddlewaretoken': token
      }
    })
    .done(function(r,textStatus,xhr){
      if(xhr.status == 200){
        location.reload(true);
      }
      else{
        mensaje(textStatus);
      }
    }).fail(function (error) {
      mensaje(error.responseText);
    });

  });
});
