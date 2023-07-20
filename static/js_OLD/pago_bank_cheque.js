$(function () {
    // ========= COBROS CON CHEQUE ===========

    const chequeForm = document.getElementById('chequeForm');
    const fv = FormValidation.formValidation(
        chequeForm,
        {
            fields: {
                dlgcheque_bank_name: {
                    validators: {
						notEmpty: {
                            message: 'El nombre del banco es requerido'
                        }
					}
                },
				dlgcheque_account: {
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
				dlgcheque_cheque_number: {
					validators: {
    					integer: {
    						message: 'La cuenta debe ser un número',
    					},
                        notEmpty: {
                            message: 'La cuenta no puede ser nula'
                        },
						stringLength: {
							min: 3,
							max: 6,
							message: 'La cuenta debe tener entre 3 y 6 caracteres.'
						}
    				}
				},
    			dlgcheque_amount: {
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
        //var $form = $(e.target);

        if (rowCount('tbl_cheque') > 0) {
            // sumatoria de transferencias
            var sumatoria_cheques = 0
            $('#tbl_cheque tr').each(function(row, tr){
                if (row > 0) {
                    var aux = $.trim($(tr).find('td:eq(4)').text());
                    sumatoria_cheques = sumatoria_cheques + toFloat(aux);
                }
            });

            //VERIFICA SI EXISTE LA TABLA TEMPORAL GRID
            if(!isExist("CHEQUE")) {
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
                var pagoId = 2 // Id App Forma Pago
                var type_desc = "CHEQUE"
                var type_abrev = "CH"
                var markup =  "<tr><td style='display:none;'>" + pagoId + "</td>"
                            + "<td data-title='Descripción'>" + type_desc + "</td>"
                            + "<td data-title='Tipo' class='text-center'>" + type_abrev + "</td>"
                            + "<td data-title='$ Monto' class='numeric'>" + sumatoria_cheques.toLocaleString() + "</td>"
                            + "<td data-title='Acción' class='text-center'>"
                                + "<div class='btn-group btn-group-sm'>"
                                    + "<button type='button' data-id=" + pagoId + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
                                + "</div>"
                            + "</td>"
                            + "</tr>";
                $("#tbl_payments tbody").append(markup);

                $('#tbl_cheque tr').each(function(row, tr){
                    if (row > 0) {
                        TableData.push({
                            "ptype" : "CH"
                            , "banco" : $.trim($(tr).find('td:eq(0)').text())
                            //, "titular": $.trim($(tr).find('td:eq(1)').text())
                            , "cuenta_nro": $.trim($(tr).find('td:eq(1)').text())
                            , "cheque_nro": $.trim($(tr).find('td:eq(2)').text())
                            , "fecha_cheq": $.trim($(tr).find('td:eq(3)').text())
                            , "monto": $.trim(toFloat($(tr).find('td:eq(4)').text()))
                        });
                    }
                });

                // Hide the dialog
                $(chequeForm).parents('.bootbox').modal('hide');

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
    						title: 'COBRO CHEQUE',
    						message: chequeForm,
    						size: 'large',
    						onEscape: true,
    						show: false // We will show it manually later
    					})
    					.on('shown.bs.modal', function() {
                            // Show the cash form
                            chequeForm.style.display = 'block';

                            // Reset form
                            fv.resetForm(true);

                            // eliminar filas tabla cheque
                    		document.querySelectorAll("#tbl_cheque tbody tr").forEach(function(e){e.remove()});

                            var markup = "<tr><td colspan='7' style = 'text-align: center;' bgcolor='Gainsboro'>"
                					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
                			$("#tbl_cheque tbody").append(markup);

                            var recibido = toFloat(grand_total);

    						$('#chequeForm')
    							.find('[name="dlgcheque_amount"]').val(recibido.toLocaleString()).change();

    						//ENVIAR EL FOCO AL BANCO
    						$('#chequeForm')
    							.find('[name="dlgcheque_bank_name"]').focus().click();
    					})
    					.on('hide.bs.modal', function(e) {
                            chequeForm.style.display = 'none';
                            document.body.appendChild(chequeForm);
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

	// ========= Formulario Cheques ===========
    $('#addCheque').click(function(){ agregarCheque(); return false; });

	function agregarCheque()
	{
        // Validate the form when click on a link or normal button
        fv
            .validate()
            .then(function(status) {
                if (status == 'Valid') {
                    var chequeBanco=document.getElementById('dlgcheque_bank_name').options[document.getElementById('dlgcheque_bank_name').selectedIndex].text;
            		//var chequePropietario=document.getElementById('dlgcheque_owner').value
            		var chequeNumeroCuenta=document.getElementById('dlgcheque_account').value
            		var chequeNumeroCheque=document.getElementById('dlgcheque_cheque_number').value
            		var chequeFecha=document.getElementById('dlgcheque_date').value
            		var chequeMonto=document.getElementById('dlgcheque_amount').value

        			var nFilas = $("#tbl_cheque tbody tr").length;
        			if (nFilas == 1) {
        				//verifica fila: ¡ Ningún registro encontrado !
        				var childrenId = $("#tbl_cheque tr td")[0].innerHTML;
        				var texto =  $("#tbl_cheque tr td:nth(0)").text();

        				if (texto == "¡ Ningún registro encontrado !")
        				{
        					// Quitar Fila: ¡ Ningún registro encontrado !
        					document.querySelectorAll("#tbl_cheque tbody tr").forEach(function(e){e.remove();});
        				}

        				// activar botón confirmar
        				$("#btnCheque").prop('disabled', false);
        			}
        			chequeMonto = toFloat(chequeMonto);
        			var markup =  "<tr><td data-title='Banco'>" + chequeBanco + "</td>"
        						//+ "<td data-title='Titular'>" + chequePropietario + "</td>"
        						+ "<td data-title='Nro. Cuenta'>" + chequeNumeroCuenta + "</td>"
        						+ "<td data-title='Nro. Cheque'>" + chequeNumeroCheque + "</td>"
        						+ "<td data-title='Fecha'>" + chequeFecha + "</td>"
        						+ "<td data-title='$ Monto' class='numeric'>" + chequeMonto.toLocaleString() + "</td>"
        						+ "<td data-title='Acción' class='text-center'>"
        							+ "<div class='btn-group btn-group-sm'>"
        								+ "<button type='button' class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
        							+ "</div>"
        						+ "</td>"
        						+ "</tr>";
        			$("#tbl_cheque tbody").append(markup);
        		} else {
                    mensaje('Complete la información solicitada.', 'error');
        		}
            });
	}

	// borrar item tbl_cheque
	$("#tbl_cheque").on('click','.deleteButton',function(){
		//var id = $(this).attr('data-id');
		$(this).closest('tr').remove();
		//agregar mensaje: ¡ No se ha encontrado ningún registro !
		var rowCount = $("#tbl_cheque td").closest("tr").length;
		if (rowCount == 0) {
			var markup = "<tr><td colspan='6' style = 'text-align: center;' bgcolor='Gainsboro'>"
					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
			$("#tbl_cheque tbody").append(markup);

			// desactivar botón confirmar
			$("#btnCheque").prop('disabled', true);
		}
	});


    /* Binding */

    // Create payment
    $(".js-bank-cheque").click(loadForm);

});
