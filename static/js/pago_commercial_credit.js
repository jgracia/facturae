$(function () {

    // ========= CRÉDITO COMERCIAL ===========

    const commcreditForm = document.getElementById('commcreditForm');
    const fv = FormValidation.formValidation(
        commcreditForm,
        {
            fields: {
                dlg_commercial_credit_amount: {
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
				dlg_commercial_credit_unit_time: {
					validators: {
						notEmpty: {
                            message: 'El tiempo es requerido'
                        }
					}
				},
				dlg_commercial_credit_term: {
					validators: {
                        numeric: {
                            message: 'La cantidad debe ser un número',
                            // The default separators
                            thousandsSeparator: '',
                            decimalSeparator: ','
                        },
                        greaterThan: {
							min: 0,
							message: 'Valor debe ser mayor a cero'
						},
                        notEmpty: {
                            message: 'El valor no puede ser nulo'
                        },
    				}
				},
				dlg_commercial_credit_installments_number: {
					validators: {
						integer: {
                            message: 'El valor no es un número entero válido',
                        },
						greaterThan: {
							min: 0,
							message: 'Valor debe ser mayor a cero'
						},
						notEmpty: {
                            message: 'El valor no puede ser nulo'
                        },
    				}
				},
				dlg_commercial_credit_rate: {
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
						between: {
							min: 0,
							max: 100,
							message: 'La tasa debe estar entre 0 y 100'
						},
    				}
				},
                dlg_commercial_credit_installment_amount: {
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
                }
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
        //var $form     = $(e.target),
        //    validator = $form.data('formValidation');

        if (rowCount('tbl_commcredit') > 0) {
            // sumatoria de transferencias
            var sumatoria_credito_comercial = 0
            $('#tbl_commcredit tr').each(function(row, tr){
                if (row > 0) {
                    var aux = $.trim($(tr).find('td:eq(7)').text());
                    sumatoria_credito_comercial = sumatoria_credito_comercial + toFloat(aux);
                }
            });

            //VERIFICA SI EXISTE LA TABLA TEMPORAL GRID
            if(!isExist("CRÉDITO COMERCIAL")) {
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
                var pagoId = 3 // Id App Forma Pago
                var type_desc = "CRÉDITO COMERCIAL"
                var type_abrev = "CC"
                var markup =  "<tr><td style='display:none;'>" + pagoId + "</td>"
                            + "<td data-title='Descripción'>" + type_desc + "</td>"
                            + "<td data-title='Tipo' class='text-center'>" + type_abrev + "</td>"
                            + "<td data-title='$ Monto' class='numeric'>" + Number(sumatoria_credito_comercial.toFixed(2)).toLocaleString() + "</td>"
                            + "<td data-title='Acción' class='text-center'>"
                                + "<div class='btn-group btn-group-sm'>"
                                    + "<button type='button' data-id=" + pagoId + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
                                + "</div>"
                            + "</td>"
                            + "</tr>";
                $("#tbl_payments tbody").append(markup);

                var record = 'T';
                $('#tbl_commcredit tr').each(function(row, tr) {
                    if (row > 0) {
                        TableData.push({
                            "ptype" : "CC"
                            , "record": record
                            , "nro" : $(tr).find('td:eq(0)').text()
                            , "monto" : $.trim(toFloat($(tr).find('td:eq(1)').text()))
                            , "plazo": $.trim($(tr).find('td:eq(2)').text())
                            , "unidad_tiempo": $.trim($(tr).find('td:eq(3)').text())
                            , "num_cuotas": $.trim($(tr).find('td:eq(4)').text())
                            , "tasa_interes": $.trim(toFloat($(tr).find('td:eq(5)').text()))
                            , "corte": $.trim($(tr).find('td:eq(6)').text())
                            , "cuota": $.trim(toFloat($(tr).find('td:eq(7)').text()))
                        });
                        record = 'F';
                    }
                });

                // Hide the dialog
                $(commcreditForm).parents('.bootbox').modal('hide');
            } else {
                swal("Oops...", "Usted ya ha ingresado esta forma de pago.", "warning");
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
                            title: 'CRÉDITO COMERCIAL',
                            message: commcreditForm,
                            size: 'large',
                            onEscape: true,
                            show: false // We will show it manually later
                        })
                        .on('shown.bs.modal', function() {
                            // Show the cash form
                            commcreditForm.style.display = 'block';

                            // Reset form
                            fv.resetForm(true);

                            // eliminar filas tabla transferencia
                    		document.querySelectorAll("#tbl_commcredit tbody tr").forEach(function(e){e.remove()});

                            //  Ningún registro encontrado
                            var markup = "<tr><td colspan='9' style = 'text-align: center;' bgcolor='Gainsboro'>"
                					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
                			$("#tbl_commcredit tbody").append(markup);

    						var recibido = toFloat(grand_total);

    						$('#commcreditForm')
    							.find('[name="dlg_commercial_credit_amount"]').val(recibido.toLocaleString()).change();

                            $('#commcreditForm')
    							.find('[name="dlg_commercial_credit_rate"]').val(0).change();

    						//ENVIAR EL FOCO AL NOMBRE DE LA TARJETA
    						$('#commcreditForm')
    							.find('[name="dlg_commercial_credit_amount"]').focus().select();
                        })
                        .on('hide.bs.modal', function() {
                            // Bootbox will remove the modal (including the body which contains the login form)
                            // after hiding the modal
                            // Therefor, we need to backup the form

                            commcreditForm.style.display = 'none';
                            document.body.appendChild(commcreditForm);
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

	// ========= Formulario Crédito Comercial ===========
    $('#addCommCredit').click(function(){ agregarCreditoComercial(); return false; });

	function agregarCreditoComercial()
	{
        // Validate the form when click on a link or normal button
        fv
            .validate()
            .then(function(status) {
                if (status == 'Valid') {
                    var commercialcreditMonto=document.getElementById('dlg_commercial_credit_amount').value
            		var commercialcreditTiempo=document.getElementById('dlg_commercial_credit_unit_time').options[document.getElementById('dlg_commercial_credit_unit_time').selectedIndex].text;
            		var commercialcreditPlazo=document.getElementById('dlg_commercial_credit_term').value
            		var commercialcreditNumeroCuotas=document.getElementById('dlg_commercial_credit_installments_number').value
            		var commercialcreditTasa=document.getElementById('dlg_commercial_credit_rate').value
            		var commercialcreditCorte=document.getElementById('dlg_commercial_credit_cutoff_date').value
            		var commercialcreditCuota=document.getElementById('dlg_commercial_credit_installment_amount').value

        			var nFilas = $("#tbl_commcredit tbody tr").length;
        			if (nFilas == 1) {
        				//verifica fila: ¡ Ningún registro encontrado !
        				var childrenId = $("#tbl_commcredit tr td")[0].innerHTML;
        				var texto =  $("#tbl_commcredit tr td:nth(0)").text();

        				if (texto == "¡ Ningún registro encontrado !")
        				{
        					// Quitar Fila: ¡ Ningún registro encontrado !
        					document.querySelectorAll("#tbl_commcredit tbody tr").forEach(function(e){e.remove();});
        				}

        				// activar botón confirmar
        				$("#btnCommCredit").prop('disabled', false);
        			}

        			//var num_letras = parseInt(commercialcreditNumeroCuotas);
                    //var interval_days = parseInt(plazo_dias / num_letras);

                    var unidad = commercialcreditTiempo;
                    var interval_days = 0;
                    if (unidad == "DÍAS") {
                        interval_days = parseInt(commercialcreditPlazo / commercialcreditNumeroCuotas);
        			} else if (unidad == "MESES") {
        				interval_days =  30;
        			} else if (unidad == "AÑOS") {
                        interval_days = 365;
        			}

                    var num_letras = parseInt(commercialcreditNumeroCuotas);
        			for (i = 0; i < num_letras; i++) {
                        var date = new Date(document.getElementById('dlg_commercial_credit_cutoff_date').value);
                        date.setDate(date.getDate() + (interval_days * i) + 1);


                        //var date = moment(mydate.getDate() + (interval_days * i) + 1);

                        var tmpVence = date.toISOString().slice(0,10);
                        console.log(tmpVence);

        				var markup =  "<tr><td data-title='No' class='text-center'>"
        							+(i+1)+"</td>"
        							+ "<td data-title='Monto' class='numeric'>" + commercialcreditMonto + "</td>"
        							+ "<td data-title='Plazo' class='text-center'>" + commercialcreditPlazo + "</td>"
        							+ "<td data-title='Und (tiempo)'>" + commercialcreditTiempo + "</td>"
        							+ "<td data-title='Nro. Cuotas' class='text-center'>" + commercialcreditNumeroCuotas + "</td>"
        							+ "<td data-title='Tasa (% int)' class='numeric'>" + commercialcreditTasa + "</td>"
        							+ "<td data-title='Vence'>" + tmpVence + "</td>"
        							+ "<td data-title='$ Monto' class='numeric'>" + commercialcreditCuota + "</td>"
        							+ "<td data-title='Acción' class='text-center'>"
        								+ "<div class='btn-group btn-group-sm'>"
        									+ "<button type='button' class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
        								+ "</div>"
        							+ "</td>"
        							+ "</tr>";
        				$("#tbl_commcredit tbody").append(markup);
        			}

        		} else {
        			swal("Oops...", "Complete la información solicitada.", "warning");
        		}
            });
	}

	// borrar item tbl_commcredit
	$("#tbl_commcredit").on('click','.deleteButton',function(){
        // eliminar tabla credito
		document.querySelectorAll("#tbl_commcredit tbody tr").forEach(function(e){e.remove()});

		var markup = "<tr><td colspan='9' style = 'text-align: center;' bgcolor='Gainsboro'>"
				+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
		$("#tbl_commcredit tbody").append(markup);

		// desactivar botón confirmar
		$("#btnCommCredit").prop('disabled', true);

	});

	$("#dlg_commercial_credit_amount").bind('keyup mouseup', function () {
		calcularCuota();
	});
	$("#dlg_commercial_credit_term").bind('keyup mouseup', function () {
		calcularCuota();
	});
	$("#dlg_commercial_credit_rate").bind('keyup mouseup', function () {
		calcularCuota();
	});
	$("#dlg_commercial_credit_installments_number").bind('keyup mouseup', function () {
		calcularCuota();
	});
    $("#dlg_commercial_credit_unit_time").change(function(){
        calcularCuota();
    });

	function calcularCuota() {
		var R = 0;
		var n = 0;
		var l = toFloat(document.getElementById('dlg_commercial_credit_installments_number').value);
		var monto_finaciado = document.getElementById('dlg_commercial_credit_amount').value;
		var tasa_interes = document.getElementById('dlg_commercial_credit_rate').value;
		var plazo = document.getElementById('dlg_commercial_credit_term').value;
		var unidad=document.getElementById('dlg_commercial_credit_unit_time').options[document.getElementById('dlg_commercial_credit_unit_time').selectedIndex].text;

		// cambiar fecha de vencimiento
		if (l > 0 && plazo > 0) {
			var fv = document.getElementById("dlg_commercial_credit_cutoff_date");
			var interval_date =  parseInt(plazo / l);

			var date = new Date();
			if (unidad == "DÍAS") {
				date.setDate(date.getDate() + interval_date);
				fv.value = moment(date).format('YYYY-MM-DD');
				//console.log("FECHA DIAS=" + moment(date).format('DD-MM-YYYY'));
			} else if (unidad == "MESES") {
				date.setDate(date.getDate() + interval_date * 30);
				fv.value = moment(date).format('YYYY-MM-DD');
				//console.log("FECHA MESE=" + moment(date).format('DD-MM-YYYY'));
			} else if (unidad == "AÑOS") {
				// AÑOS
				date.setDate(date.getDate() + interval_date * 365);
				fv.value = moment(date).format('YYYY-MM-DD');
				//console.log("FECHA AÑOS=" + moment(date).format('DD-MM-YYYY'));
			}
			//fv.value = new_fv;
		} else {
			console.log("No se puede dividir entre cero.");
		}

		var P = toFloat(monto_finaciado);
		var i = toFloat(tasa_interes) / 100;
		var n = toFloat(plazo) / 30;

		if (i > 0) {
			//VF = VA (1 + n * i)
			//VF = Valor Futuro
			//VA = Valor Actual
			//i = Tasa de interés
			//n = Periodo de tiempo

			if (l > 0) {
				//var dividendo = i * Math.pow(1 + i, n);
				//var divisor = Math.pow(1 + i, n) - 1;
				//R = (P * (dividendo / divisor)).toFixed(2);

				var factor_interes_diario = i / 360;
				var saldo = P;
				var nro_dias = plazo;
				var interes_mensual = factor_interes_diario * saldo * nro_dias;
				var cuota = (saldo + interes_mensual) / l;
				R = cuota.toLocaleString()

			} else {
				R = 0;
				console.log("No se puede dividir entre cero.");
			}
		} else {
			if (l > 0) {
				R = (P / l).toLocaleString()
			} else {
				R = 0;
				console.log("No se puede dividir entre cero.");
			}
		}
		var cuota = document.getElementById("dlg_commercial_credit_installment_amount");
		cuota.value = R;
	}

    /* Binding */

    // Create payment
    $(".js-comm-credit").click(loadForm);

});
