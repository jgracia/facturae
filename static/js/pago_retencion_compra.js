$(function () {
    // ========= COBROS RETENCIÓN ===========

    const retencionForm = document.getElementById('retencionForm');
    const fv = FormValidation.formValidation(
        retencionForm,
        {
            fields: {
                dlgretencion_id_tipo_impuesto: {
                    validators: {
						notEmpty: {
                            message: 'El tipo de impuesto es requerido'
                        }
					}
                },
                dlgretencion_id_impuesto: {
                    validators: {
						notEmpty: {
                            message: 'El impuesto es requerido'
                        }
					}
                },
    			dlgretencion_base_imponible: {
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
                dlgretencion_porcentaje_retencion: {
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
                dlgretencion_valor_retenido: {
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
        if (rowCount('tbl_retencion') > 0) {
            // sumatoria de transferencias
            var sumatoria_retenciones = 0
            $('#tbl_retencion tr').each(function(row, tr){
                if (row > 0) {
                    var aux = $.trim($(tr).find('td:eq(5)').text());
                    sumatoria_retenciones = sumatoria_retenciones + toFloat(aux);
                }
            });

            //VERIFICA SI EXISTE LA TABLA TEMPORAL GRID
            if(!isExist("RETENCIÓN")) {
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
                var pagoId = 0 // Id App Forma Pago: OJO este no existe
                var type_desc = "RETENCIÓN"
                var type_abrev = "RT"
                var markup =  "<tr><td style='display:none;'>" + pagoId + "</td>"
                            + "<td data-title='Descripción'>" + type_desc + "</td>"
                            + "<td data-title='Tipo' class='text-center'>" + type_abrev + "</td>"
                            + "<td data-title='$ Monto' class='numeric'>" + sumatoria_retenciones.toLocaleString() + "</td>"
                            + "<td data-title='Acción' class='text-center'>"
                                + "<div class='btn-group btn-group-sm'>"
                                    + "<button type='button' data-id=" + pagoId + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
                                + "</div>"
                            + "</td>"
                            + "</tr>";
                $("#tbl_payments tbody").append(markup);

                $('#tbl_retencion tr').each(function(row, tr){
                    if (row > 0) {
                        TableData.push({
                            "ptype" : "RT"
                            , "cod_reten" : $.trim($(tr).find('td:eq(0)').text())
                            , "tipo_imp": $.trim($(tr).find('td:eq(1)').text())
                            , "base_imponible": $.trim(toFloat($(tr).find('td:eq(3)').text()))
                            , "porcentaje": $.trim(toFloat($(tr).find('td:eq(4)').text()))
                            , "valor_retenido": $.trim(toFloat($(tr).find('td:eq(5)').text()))
                            , "documento": $.trim($(tr).find('td:eq(6)').text())
                            , "fecha_comp_modifica": $.trim($(tr).find('td:eq(7)').text())
                            , "tipo_doc": $.trim($(tr).find('td:eq(8)').text())
                        });
                    }
                });

                // Hide the dialog
                $(retencionForm).parents('.bootbox').modal('hide');

            } else {
                mensaje('Usted ya ha ingresado esta forma de pago.', 'error');
            }
        }
    });

    /* Functions */

    var loadForm = function () {
        var btn = $(this);
        var nro_comprobante = $("#numero_comprobante").val();
        if (nro_comprobante != '' && nro_comprobante.length == 17) {
            if (rowCount('tbl_payments') > 0) {
                $.ajax({
                    url:  btn.attr("data-url"),
                    success: function(response, textStatus, xhr) {
                        if (response.total_filas > 0) {
            				var grand_total = $("#lblTotal").text();
                            var tipo_documento = '01' // 01=FACTURA, 03=NOTA DEBITO, 07=LIQ. COMPRAS
                            //var fecha_comp_modifica = $("#datepicker").val();
                            //var nro_comprobante = $("#numero_comprobante").val();

                            var date = new Date();
                            var currentDate = date.toISOString().slice(0,10);

                            // Show the dialog
                            bootbox
                                .dialog({
                                    title: 'RETENCIÓN EN COMPRA',
                                    message: retencionForm,
                                    size: 'extra-large',
                                    onEscape: true,
                                    show: false // We will show it manually later
                                })
                                .on('shown.bs.modal', function() {
                                    // Show the cash form
                                    retencionForm.style.display = 'block';

                                    // Reset form
                                    fv.resetForm(true);

                                    // eliminar filas tabla retención
                            		document.querySelectorAll("#tbl_retencion tbody tr").forEach(function(e){e.remove()});

                                    var markup = "<tr><td colspan='10' style = 'text-align: center;' bgcolor='Gainsboro'>"
                        					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
                        			$("#tbl_retencion tbody").append(markup);

                                    $('#retencionForm')
            							.find('[name="dlgretencion_tipo_documento_codigo"]').val(tipo_documento).change();

                                    $('#retencionForm')
                                        .find('[name="dlgretencion_fecha_comp_modifica"]').val(currentDate);

                                    $('#retencionForm')
                                        .find('[name="dlgretencion_numero_comprobante"]').val(nro_comprobante).change();

                                    var recibido = toFloat(grand_total);
            						$('#retencionForm')
            							.find('[name="dlgretencion_base_imponible"]').val(recibido.toLocaleString()).change();

            						//ENVIAR EL FOCO AL TIPO DE IMPUESTO
            						$('#retencionForm')
            							.find('[name="dlgretencion_id_tipo_impuesto"]').focus().click();
                                })
                                .on('hide.bs.modal', function() {
                                    retencionForm.style.display = 'none';
                                    document.body.appendChild(retencionForm);
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
            } else {
                mensaje('No existe descripción de pago.', 'error');
            }
        } else {
            mensaje('Ingrese el Número de Comprobante', 'error');
        }
    };

	// ========= Formulario Retención ===========
    $('#addRetencion').click(function(){ agregarRetencionModal(); return false; });

	function agregarRetencionModal()
	{
        // Validate the form when click on a link or normal button
        fv
            .validate()
            .then(function(status) {
                if (status == 'Valid') {
                    var tipo_impuesto=document.getElementById('dlgretencion_id_tipo_impuesto').options[document.getElementById('dlgretencion_id_tipo_impuesto').selectedIndex].value
                    var cod_impuesto=document.getElementById('dlgretencion_id_impuesto').options[document.getElementById('dlgretencion_id_impuesto').selectedIndex].value
                    var descripcion=document.getElementById('dlgretencion_id_impuesto').options[document.getElementById('dlgretencion_id_impuesto').selectedIndex].text
            		var base_imponible=document.getElementById('dlgretencion_base_imponible').value
            		var porcentaje_retencion=document.getElementById('dlgretencion_porcentaje_retencion').value
            		var valor_retenido=document.getElementById('dlgretencion_valor_retenido').value
                    var documento=document.getElementById('dlgretencion_numero_comprobante').value
                    var fecha_comp_modifica=document.getElementById('dlgretencion_fecha_comp_modifica').value
                    var tipo_documento_codigo=document.getElementById('dlgretencion_tipo_documento_codigo').value

        			var nFilas = $("#tbl_retencion tbody tr").length;
        			if (nFilas == 1) {
        				//verifica fila: ¡ Ningún registro encontrado !
        				var childrenId = $("#tbl_retencion tr td")[0].innerHTML;
        				var texto =  $("#tbl_retencion tr td:nth(0)").text();

        				if (texto == "¡ Ningún registro encontrado !")
        				{
        					// Quitar Fila: ¡ Ningún registro encontrado !
        					document.querySelectorAll("#tbl_retencion tbody tr").forEach(function(e){e.remove();});
        				}

        				// activar botón confirmar
        				$("#btnRetencion").prop('disabled', false);
        			}
        			valor_retenido = parseFloat(valor_retenido).toFixed(2);
                    var markup =  "<tr data-title='Cod. Reten.'><td>" + cod_impuesto + "</td>"
                                + "<td data-title='Código' class='numeric'>" + tipo_impuesto + "</td>"
                                + "<td data-title='Descripción'>" + descripcion + "</td>"
                                + "<td data-title='Base Imponible' class='numeric'>" + base_imponible.toLocaleString() + "</td>"
                                + "<td data-title='Porcentaje' class='numeric'>" + porcentaje_retencion.toLocaleString() + "</td>"
                                + "<td data-title='Total' class='numeric'>" + valor_retenido.toLocaleString() + "</td>"
                                + "<td data-title='Documento'>" + documento + "</td>"
                                + "<td data-title='Fecha'>" + fecha_comp_modifica + "</td>"
                                + "<td data-title='Tipo'>" + tipo_documento_codigo + "</td>"
                                + "<td data-title='Acción' class='text-center'>"
                                    + "<div class='btn-group btn-group-sm'>"
                                        + "<button type='button' data-id=" + cod_impuesto + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
                                    + "</div>"
                                + "</td>"
                                + "</tr>";
        			$("#tbl_retencion tbody").append(markup);
        		} else {
                    mensaje('Complete la información solicitada.', 'error');
        		}
            });
	}

	// borrar item tbl_retencion
	$("#tbl_retencion").on('click','.deleteButton',function(){
		//var id = $(this).attr('data-id');
		$(this).closest('tr').remove();
		//agregar mensaje: ¡ No se ha encontrado ningún registro !
		var rowCount = $("#tbl_retencion td").closest("tr").length;
		if (rowCount == 0) {
			var markup = "<tr><td colspan='10' style = 'text-align: center;' bgcolor='Gainsboro'>"
					+ "<font color='OrangeRed'>¡ Ningún registro encontrado !</font></td></tr>";
			$("#tbl_retencion tbody").append(markup);

			// desactivar botón confirmar
			$("#btnRetencion").prop('disabled', true);
		}
	});

    // evento tipo de impuesto
	$("#dlgretencion_id_tipo_impuesto").change(function () {
		var tipo_impuesto_id = $(this).val();
		var url = "../../retencion/ajax/ajax_load_impuesto/";
		$.ajax({
			url: url,
			data: {
				'impuesto': tipo_impuesto_id
	        },
			success: function (data) {
				$("#dlgretencion_id_impuesto").html(data);
	        }
		});
	});

	// evento impuesto
	$("#dlgretencion_id_impuesto").change(function () {
		var impuesto_codigo = $(this).val();
        var url = "../../retencion/ajax/ajax_get_porcentaje/";
		$.ajax({
			url: url,
			data: {
				'impuesto': impuesto_codigo
	        },
			success: function (data) {
				$("#dlgretencion_porcentaje_retencion").val(toFloat(data.porcentaje).toLocaleString());
                // calcular valor retenido
                var valor_base_imponible=toFloat($("#dlgretencion_base_imponible").val());
        		var porcentaje_retencion = toFloat(data.porcentaje);
        		var valor_retenido = parseFloat((valor_base_imponible * porcentaje_retencion) / 100).toFixed(2);
        		$("#dlgretencion_valor_retenido").val(toFloat(valor_retenido).toLocaleString());
	        }
		});
	});

    $("#dlgretencion_base_imponible").on("keyup mouseup",function (e) {
	    e.preventDefault();
		var valor_base_imponible = toFloat($(this).val());
		var porcentaje_retencion = toFloat($("#dlgretencion_porcentaje_retencion").val());
		var valor_retenido = parseFloat((valor_base_imponible * porcentaje_retencion) / 100).toFixed(2);
		$("#dlgretencion_valor_retenido").val(toFloat(valor_retenido).toLocaleString());
	});

    /* Binding */

    // Create payment
    $(".js-retencion-payment").click(loadForm);

});
