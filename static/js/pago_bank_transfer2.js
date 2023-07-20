$(function () {

    // ========= COBROS CON TRANSFERECIA ===========

    const transferForm = document.getElementById('transferForm');
    const fv = FormValidation.formValidation(
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

        if (rowCount('tbl_transfer') > 0) {
            // sumatoria de transferencias
            var sumatoria_transferencias = 0
            $('#tbl_transfer tr').each(function(row, tr){
                if (row > 0) {
                    var aux = $.trim($(tr).find('td:eq(3)').text());
                    sumatoria_transferencias = sumatoria_transferencias + toFloat(aux);
                }
            });

            //VERIFICA SI EXISTE LA TABLA TEMPORAL GRID
            if(!isExist("TRANSFERENCIA")) {
                var nFilas = $("#tbl_payments tbody tr").length;
                if (nFilas == 1) {
                    //verifica fila: ¡ Ningún registro encontrado !
                    var childrenId = $("#tbl_payments tr td")[0].innerHTML;
                    if (!$.isNumeric(childrenId))
                    {
                        // Quitar Fila: ¡ Ningún registro encontrado !
                        document.querySelectorAll("#tbl_payments tbody tr").forEach(function(e){e.remove();});
                    }
                }
                var pagoId = 6 // Id App Forma Pago
                var type_desc = "TRANSFERENCIA"
                var type_abrev = "TB"
                var markup =  "<tr><td style='display:none;'>" + pagoId + "</td>"
                            + "<td data-title='Descripción'>" + type_desc + "</td>"
                            + "<td data-title='Tipo' class='text-center'>" + type_abrev + "</td>"
                            + "<td data-title='$ Monto' class='numeric'>" + sumatoria_transferencias.toLocaleString() + "</td>"
                            + "<td data-title='Acción' class='text-center'>"
                                + "<div class='btn-group btn-group-sm'>"
                                    + "<button type='button' data-id=" + pagoId + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
                                + "</div>"
                            + "</td>"
                            + "</tr>";
                $("#tbl_payments tbody").append(markup);

                $('#tbl_transfer tr').each(function(row, tr){
                    if (row > 0) {
                        TableData.push({
                            "ptype" : "TB"
                            , "cta_origen": $.trim($(tr).find('td:eq(0)').text())
                            , "cta_destino": $.trim($(tr).find('td:eq(1)').text())
                            , "nro_comp": $.trim($(tr).find('td:eq(2)').text())
                            , "monto": $.trim(toFloat($(tr).find('td:eq(3)').text()))
                            , "banco_origen": $.trim($(tr).find('td:eq(4)').text())
                            , "banco_destino": $.trim($(tr).find('td:eq(5)').text())
                            , "fecha_transf": $.trim($(tr).find('td:eq(6)').text())
                        });
                    }
                });

                // Hide the dialog
                $(transferForm).parents('.bootbox').modal('hide');
            } else {
                mensaje('Usted ya ha ingresado esta forma de pago.', 'error');
            }
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
            fv.revalidateField('dlgtransfer_fecha');
        }).on('hide', function(e) {
            e.stopPropagation();
        });

        /*$('#dlgtransfer_fecha').datepicker({
            format: 'dd/mm/yyyy',
            autoclose: true,
            language: 'es'
        }).on('hide', function(e) {
            e.stopPropagation();
        });*/

    /* Functions */
    var loadForm = function () {
        var btn = $(this);
        $.ajax({
            url:  btn.attr("data-url"),
            success: function(response, textStatus, xhr) {
                if (response.total_filas > 0) {
    				var grand_total = $("#lblTotal").text();

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
                            fv.resetForm(true);

                            // eliminar filas tabla transferencia
                    		document.querySelectorAll("#tbl_transfer tbody tr").forEach(function(e){e.remove()});

                            //  Ningún registro encontrado
                            var markup = "<tr><td colspan='5' style = 'text-align: center;' bgcolor='Gainsboro'>"
                					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
                			$("#tbl_transfer tbody").append(markup);

                            var recibido = toFloat(grand_total);

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
                    mensaje('¡ Ningún registro encontrado !', 'error');
    			}
            },
            error : function(xhr, textStatus, errorThrown) {
              $.alert({
                icon: 'fas fa-bug',
                title: 'Error!',
                theme: 'material',
                type: 'red',
                content: errorThrown,
              });
            }
        });
    };


	// ========= Formulario Transferencias ===========
    $('#addTransfer').click(function(){ agregarTransferencia(); return false; });

	function agregarTransferencia()
	{
        // Validate the form when click on a link or normal button
        fv
            .validate()
            .then(function(status) {
                if (status == 'Valid') {
                    var transBanco=document.getElementById('dlgtransfer_bank_name').options[document.getElementById('dlgtransfer_bank_name').selectedIndex].text;
            		var transCuenta_Origen=document.getElementById('dlgtransfer_origin_account').value
            		//var transPropietario=document.getElementById('dlgtransfer_owner_account').value
                    var transBancoDestino=document.getElementById('dlgtransfer_destination_bank_name').options[document.getElementById('dlgtransfer_destination_bank_name').selectedIndex].text;
            		var transCuenta_Destino=document.getElementById('dlgtransfer_destination_account').value
                    var transNroComprobante=document.getElementById('dlgtransfer_comprobante').value
            		//var transFecha=document.getElementById('dlgtransfer_fecha').value
                    var transFecha=moment($("#dlgtransfer_fecha").val(), "YYYY-MM-DD").format('YYYY-MM-DD');
                    //console.log(transFecha);
            		var transMonto=document.getElementById('dlgtransfer_amount').value;

        			var nFilas = $("#tbl_transfer tbody tr").length;
        			if (nFilas == 1) {
        				//verifica fila: ¡ Ningún registro encontrado !
        				var childrenId = $("#tbl_transfer tr td")[0].innerHTML;
        				var texto =  $("#tbl_transfer tr td:nth(0)").text();

        				if (texto == "¡ Ningún registro encontrado !")
        				{
        					// Quitar Fila: ¡ Ningún registro encontrado !
        					document.querySelectorAll("#tbl_transfer tbody tr").forEach(function(e){e.remove();});
        				}

        				// activar botón confirmar
        				$("#btnTransfer").prop('disabled', false);
        			}
        			transMonto = toFloat(transMonto);
        			var markup =  "<tr><td data-title='Cta. Origen'>" + transCuenta_Origen + "</td>"
        						+ "<td data-title='Cta. Destino'>" + transCuenta_Destino + "</td>"
                                + "<td data-title='Nro. Comprobante'>" + transNroComprobante + "</td>"
        						+ "<td data-title='$ Monto' class='numeric'>" + transMonto.toLocaleString() + "</td>"
                                + "<td data-title='Banco Origen' style='display:none;'>" + transBanco + "</td>"
                                + "<td data-title='Banco Destino' style='display:none;'>" + transBancoDestino + "</td>"
                                + "<td data-title='Fecha Transferencia' style='display:none;'>" + transFecha + "</td>"
        						+ "<td data-title='Acción' class='text-center'>"
        							+ "<div class='btn-group btn-group-sm'>"
        								+ "<button type='button' class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
        							+ "</div>"
        						+ "</td>"
        						+ "</tr>";
        			$("#tbl_transfer tbody").append(markup);
                } else {
                    mensaje('Complete la información solicitada.', 'error');
        		}
            });

	}

	// borrar item tbl_payments
	$("#tbl_transfer").on('click','.deleteButton',function(){
		//var id = $(this).attr('data-id');
		$(this).closest('tr').remove();
		//agregar mensaje: ¡ No se ha encontrado ningún registro !
		var rowCount = $("#tbl_transfer td").closest("tr").length;
		if (rowCount == 0) {
			var markup = "<tr><td colspan='5' style = 'text-align: center;' bgcolor='Gainsboro'>"
					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
			$("#tbl_transfer tbody").append(markup);

			// desactivar botón confirmar
			$("#btnTransfer").prop('disabled', true);
		}
	});

    //$('#datetimePicker').datetimepicker({format: 'DD/MM/YYYY'});




    /* Binding */

    // Create payment
    $(".js-bank-transfer").click(loadForm);

});
