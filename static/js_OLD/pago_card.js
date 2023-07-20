$(function () {

    // ========= COBROS CON TARJETA ===========

    const cardForm = document.getElementById('cardForm');
    const fv = FormValidation.formValidation(
        cardForm,
        {
            fields: {
                dlgcard_card_name: {
                    validators: {
						notEmpty: {
                            message: 'El nombre de tarjeta es requerido'
                        }
					}
                },
                dlgcard_card_tipo: {
                    validators: {
						notEmpty: {
                            message: 'El tipo de tarjeta es requerido'
                        }
					}
                },
                dlgcard_card_number: {
                    validators: {
                        creditCard: {
                            message: 'El número de tarjeta no es válido'
                        },
                        notEmpty: {
                            message: 'El valor no puede ser nulo'
                        },
                    }
				},
                dlgcard_vaucher_nro: {
                    validators: {
						notEmpty: {
                            message: 'El tipo de tarjeta es requerido'
                        }
					}
                },
    			dlgcard_amount: {
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
        if (rowCount('tbl_card') > 0) {
			// sumatoria de monto tarjetas
			var sumatoria_tarjeta = 0
			$('#tbl_card tr').each(function(row, tr){
				if (row > 0) {
					var aux = $.trim($(tr).find('td:eq(3)').text());
					sumatoria_tarjeta = sumatoria_tarjeta + toFloat(aux);
				}
	        });

			//VERIFICA SI EXISTE LA TABLA TEMPORAL GRID
			if(!isExist("TARJETA DÉBITO")) {
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
                var tipo_tarjeta = $("#dlgcard_card_tipo").val();
                if (tipo_tarjeta == 'TD') {
					var pagoId = 4 // Id App Forma Pago
					var type_desc = "TARJETA DÉBITO"
					var type_abrev = "TD"
                } else {
                    // tarjeta crédito
                    var pagoId = 5 // Id App Forma Pago
					var type_desc = "TARJETA CRÉDITO"
					var type_abrev = "TC"
                }
				var markup =  "<tr><td style='display:none;'>" + pagoId + "</td>"
							+ "<td data-title='Descripción'>" + type_desc + "</td>"
							+ "<td data-title='Tipo' class='text-center'>" + type_abrev + "</td>"
							+ "<td data-title='$ Monto' class='numeric'>" + sumatoria_tarjeta.toLocaleString() + "</td>"
							+ "<td data-title='Acción' class='text-center'>"
								+ "<div class='btn-group btn-group-sm'>"
									+ "<button type='button' data-id=" + pagoId + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
								+ "</div>"
							+ "</td>"
							+ "</tr>";
				$("#tbl_payments tbody").append(markup);

				$('#tbl_card tr').each(function(row, tr) {
					if (row > 0) {
						TableData.push({
							"ptype" : "TD"
							, "tarjeta": $.trim($(tr).find('td:eq(0)').text())
							//, "titular": $.trim($(tr).find('td:eq(1)').text())
							, "tarjeta_nro": $.trim($(tr).find('td:eq(1)').text())
                            , "vaucher_nro": $.trim($(tr).find('td:eq(2)').text())
							//, "expira": ""
							//, "modalidad": "Corriente"
							//, "plazo": "0"
							, "monto": $.trim(toFloat($(tr).find('td:eq(3)').text()))
                            , "tipo_tarjeta": $(tr).find('td:eq(4)').text()
			            });
					}
				});

                // Hide the dialog
				$(cardForm).parents('.bootbox').modal('hide');
			} else {
                mensaje('Usted ya ha ingresado esta forma de pago.', 'error');
			}
		}
    });

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
                            title: 'COBRO TARJETA',
                            message: cardForm,
                            size: 'large',
                            onEscape: true,
                            show: false // We will show it manually later
                        })
                        .on('shown.bs.modal', function() {
                            // Show the card form
                            cardForm.style.display = 'block';

                            // Reset form
                            ///fv.resetForm(true);

                            // eliminar filas tabla tarjetas
                    		document.querySelectorAll("#tbl_card tbody tr").forEach(function(e){e.remove()});

                            //  Ningún registro encontrado
                            var markup = "<tr><td colspan='5' style = 'text-align: center;' bgcolor='Gainsboro'>"
                					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
                			$("#tbl_card tbody").append(markup);

                            var recibido = toFloat(grand_total);

    						$('#cardForm')
    							.find('[name="dlgcard_amount"]').val(recibido.toLocaleString()).change();

    						//ENVIAR EL FOCO AL NOMBRE DE LA TARJETA
    						$('#cardForm')
    							.find('[name="dlgcard_card_name"]').focus().click();

                        })
                        .on('hide.bs.modal', function() {
                            cardForm.style.display = 'none';
                            document.body.appendChild(cardForm);
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
    $('#addCard').click(function(){ agregarTarjeta(); return false; });

	function agregarTarjeta()
	{
        // Validate the form when click on a link or normal button
        fv
            .validate()
            .then(function(status) {
                if (status == 'Valid') {
                    //var cardPropietario=document.getElementById('dlgcard_owner').value
            		var cardNumeroTarjeta=document.getElementById('dlgcard_card_number').value
                    var tarjeta_vaucher_nro = $("#dlgcard_vaucher_nro").val();
            		var cardMonto=document.getElementById('dlgcard_amount').value
                    var nombreTarjeta = $("#dlgcard_card_name").children("option:selected").text();
                    //var tipo_tarjeta = 'TD'
                    var tipo_tarjeta = $("#dlgcard_card_tipo").val();

        			var nFilas = $("#tbl_card tbody tr").length;
        			if (nFilas == 1) {
        				//verifica fila: ¡ Ningún registro encontrado !
        				var childrenId = $("#tbl_card tr td")[0].innerHTML;
        				var texto =  $("#tbl_card tr td:nth(0)").text();

        				if (texto == "¡ Ningún registro encontrado !")
        				{
        					// Quitar Fila: ¡ Ningún registro encontrado !
        					document.querySelectorAll("#tbl_card tbody tr").forEach(function(e){e.remove();});
        				}

        				// activar botón confirmar
        				$("#btnCard").prop('disabled', false);
        			}
        			cardMonto = toFloat(cardMonto);
        			var markup =  "<tr><td data-title='Tarjeta'>" + nombreTarjeta + "</td>"
        						//+ "<td data-title='Titular'>" + cardPropietario + "</td>"
        						+ "<td data-title='Nro. Tarjeta'>" + cardNumeroTarjeta + "</td>"
                                + "<td data-title='Vaucher Nro.'>" + tarjeta_vaucher_nro + "</td>"
        						+ "<td data-title='$ Monto' class='numeric'>" + cardMonto.toLocaleString() + "</td>"
                                + "<td data-title='Tipo' style='display:none;'>" + tipo_tarjeta + "</td>"
        						+ "<td data-title='Acción' class='text-center'>"
        							+ "<div class='btn-group btn-group-sm'>"
        								+ "<button type='button' class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
        							+ "</div>"
        						+ "</td>"
        						+ "</tr>";
        			$("#tbl_card tbody").append(markup);
                } else {
                    mensaje('Complete la información solicitada.', 'error');
        		}
            });

	}

    // borrar item tbl_card
	$("#tbl_card").on('click','.deleteButton',function(){
		//var id = $(this).attr('data-id');
		$(this).closest('tr').remove();
		//agregar mensaje: ¡ No se ha encontrado ningún registro !
		var rowCount = $("#tbl_card td").closest("tr").length;
		if (rowCount == 0) {
			var markup = "<tr><td colspan='5' style = 'text-align: center;' bgcolor='Gainsboro'>"
					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
			$("#tbl_card tbody").append(markup);

			// desactivar botón confirmar
			$("#btnCard").prop('disabled', true);
		}
	});

    /* Binding */

    // Create payment
    $(".js-card").click(loadForm);

});
