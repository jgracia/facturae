$(function () {

  // ========= COBROS CON TRANSFERECIA ===========

  const transferForm = document.getElementById('transferForm');
  const fvtransfer = FormValidation.formValidation(
    transferForm,
    {
      fields: {
        dlgtransfer_bank_name: {
          validators: {
            notEmpty: {
              message: 'El nombre del banco es requerido'
            }
          }
        },
        dlgtransfer_origin_account: {
          validators: {
  					integer: {
  						message: 'La cuenta debe ser un número',
  					},
            notEmpty: {
              message: 'La cuenta no puede ser nula'
            },
            stringLength: {
              min: 10,
              max: 15,
              message: 'La cuenta debe tener entre 10 y 15 caracteres.'
            }
          }
        },
        dlgtransfer_destination_bank_name: {
          validators: {
            notEmpty: {
              message: 'El nombre del banco es requerido'
            }
          }
        },
        dlgtransfer_destination_account: {
          validators: {
            integer: {
  						message: 'La cuenta debe ser un número',
  						// The default separators
              thousandsSeparator: '',
  						decimalSeparator: '.'
  					},
            notEmpty: {
              message: 'La cuenta no puede ser nula'
            },
            stringLength: {
              min: 10,
              max: 15,
              message: 'La cuenta debe tener entre 10 y 15 caracteres.'
            }
          }
        },
        dlgtransfer_comprobante: {
          validators: {
            notEmpty: {
              message: 'El nombre no puede ser nulo'
            },
          }
        },
        dlgtransfer_fecha: {
          validators: {
            notEmpty: {
              message: 'La fecha es obligatoria y no puede estar vacía'
            },
            date: {
              format: 'DD/MM/YYYY'
            }
          }
        },
  			dlgtransfer_amount: {
  				validators: {
            numeric: {
              message: 'La cantidad debe ser un número',
              // The default separators
              thousandsSeparator: '',
              decimalSeparator: ','
            },
            notEmpty: {
              message: 'El valor no puede ser nulo'
            },
  				}
  			},
      },
      plugins: {
        trigger: new FormValidation.plugins.Trigger(),
        bootstrap: new FormValidation.plugins.Bootstrap(),
        submitButton: new FormValidation.plugins.SubmitButton(),
        icon: new FormValidation.plugins.Icon({
          valid: 'fa fa-check',
          invalid: 'fa fa-times',
          validating: 'fa fa-refresh',
        }),
      },
    }
  )
  .on('core.form.valid', function() {

    var transMonto=document.getElementById('dlgtransfer_amount').value;
    transMonto = toFloat(transMonto);

    var grand_total = toFloat($("#lblTotal").text());

    if (transMonto >= grand_total) {
      //var pagoId = 6 // Id App Forma Pago
      //var type_abrev = "TB"

      var nroComprobante = $('#numero_comprobante').val();
      var proveedor_id = $('#id_supplier').val();
      var almacen_id = $('#id_almacen').val();

      var data = {
        num_fact: nroComprobante,
        proveed_id: proveedor_id,
        grand_total: grand_total,
        importe_recibido: grand_total,
        terminos: 'TB'
      };

      console.log("datos enviados...");
      console.log($(transferForm).serialize() + '&' + $.param(data));

      $.ajax({
        url: "../purchase-payment/",
        dataType: 'json',
        method: 'post',
        data: $(transferForm).serialize() + '&' + $.param(data)
      }).done(function (response) {
        // guardar orden de compra
        if (response.success) {
          var data = {
            'fecha_emision': $("#datepicker").val(),
            'proveedor_id': proveedor_id,
            'nro_comp': nroComprobante,
            'nro_guia': '',
            'almacen_id': almacen_id,
            //'pTableData' : TableData
          };

          var token = jQuery("#transferForm [name=csrfmiddlewaretoken]").val();
          $.ajax({
            headers: { "X-CSRFToken": token },
            url: "{% url 'compra:guardar_orden' %}",
            method: 'POST',
            data: $.param(data),
            dataType: 'json',
            success: function(response, textStatus, xhr) {
              if (!response.success)
                mensaje('El token no es válido', 'error');
              else {
                //poner a cero subtotales
                setZero();
                $.alert({
                  icon: 'fas fa-thumbs-up',
                  title: 'Buen trabajo!',
                  theme: 'material',
                  type: 'green',
                  content: 'Has agregado al inventario los productos!',
                });
              }
            },
            error : function(xhr, textStatus, errorThrown) {
              $.alert({
                icon: 'fas fa-bug',
                title: 'Error!',
                theme: 'material',
                type: 'red',
                content: 'Error al guardar factura!',
              });
            }
          });
        } else {
          mensaje('Error al procesar pago.', 'error');
        }
      }).fail(function(){
        mensaje("Error al procesar pago.", 'error');
      });






      // Hide the dialog
      $(transferForm).parents('.bootbox').modal('hide');
    } else {
      $.alert({
        title: 'Alerta!',
        content: 'Monto inválido.',
      });
    }
  });

  $('[name="dlgtransfer_fecha"]')
    .datepicker({
      format: 'dd/mm/yyyy',
      autoclose: true, // It is false, by default
      language: 'es'
    })
    .on('changeDate', function(e) {
      // Revalidate the date field
      fvtransfer.revalidateField('dlgtransfer_fecha');
    }).on('hide', function(e) {
      e.stopPropagation();
    });

  /* Functions */
  var loadForm = function () {

    var proveedor_id = $('#id_supplier').val();
    if (proveedor_id > 0 ) {
      var nroComprobante = $('#numero_comprobante').val();
      if (nroComprobante != '' && nroComprobante.length == 17) {
        var almacen_id = $('#id_almacen').val();
        if (almacen_id > 0 ) {
          var grand_total = toFloat($("#lblTotal").text());
          if (grand_total > 0) {
            // Show the dialog
            bootbox
              .dialog({
                title: 'COBRO TRANSFERENCIA',
                message: transferForm,
                size: 'large',
                onEscape: true,
                show: false // We will show it manually later
              })
              .on('shown.bs.modal', function() {
                // Show the cash form
                transferForm.style.display = 'block';

                // Reset form
                fvtransfer.resetForm(true);

                var recibido = grand_total;


                //$("#mydate").datepicker("setDate",currentDate);
                var today = new Date();
                var dd = today.getDate();
                var mm = today.getMonth()+1;
                var yyyy = today.getFullYear();
                if(dd<10) {
                  dd='0'+dd;
                }
                if(mm<10) {
                  mm='0'+mm;
                }
                today = dd+'/'+mm+'/'+yyyy;

                $('#transferForm')
                  .find('[name="dlgtransfer_fecha"]').val(today);

                $('#transferForm')
                  .find('[name="dlgtransfer_amount"]').val(recibido.toLocaleString()).change();

                //ENVIAR EL FOCO AL BANCO
                $('#transferForm')
                  .find('[name="dlgtransfer_bank_name"]').focus().click();

                // Set the value for the date input
                //document.querySelector('[name="selectedDate"]').value = $('#embeddingDatePicker').datepicker('getFormattedDate')
              })
              .on('hide.bs.modal', function() {
                transferForm.style.display = 'none';
                document.body.appendChild(transferForm);
              })
              .modal('show');

          } else {
            mensaje('¡ Ningún valor de cobro !', 'error')
          }
        } else {
          mensaje('Seleccione un almacén.', 'error');
        }
      } else {
        mensaje('Revise Nro. Comprobante.', 'error');
      }
    } else {
      mensaje('Revise Proveedor del producto o servicio.', 'error');
    }

  };

  /* Binding */

  // Create payment
  $(".js-bank-transfer").click(loadForm);
});
