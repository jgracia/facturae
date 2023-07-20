$(function () {

    // ========= COBROS EN EFECTIVO ===========

    const cashForm = document.getElementById('cashForm');
    const fv = FormValidation.formValidation(
        cashForm,
        {
            fields: {
                // validadores pagos efectivo
                amount_received: {
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

        var amount = cashForm.querySelector('[name="amount_received"]').value;

        //var $form = $(e.target),
        //    amount   = $form.find('[name="amount_received"]').val();

        //VERIFICA SI EXISTE LA TABLA TEMPORAL GRID
        if(!isExist("EFECTIVO")) {
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

            var monto = $("#dlg_grand_total").val();
            var gra_total = toFloat(monto);
            var recibido = toFloat(amount);

            var cambio = recibido - gra_total;
            if (cambio >= 0)
                amount = gra_total;
            else
                amount = recibido;

            var pagoId = 1 // Id App Forma Pago
            var type_desc = "EFECTIVO"
            var type_abrev = "EF"

            //amount = parseFloat(amount).toFixed(2);
            var markup =  "<tr><td style='display:none;'>" + pagoId + "</td>"
                        + "<td data-title='Descripción'>" + type_desc + "</td>"
                        + "<td data-title='Tipo' class='text-center'>" + type_abrev + "</td>"
                        + "<td data-title='$ Monto' class='numeric'>" + amount.toLocaleString() + "</td>"
                        + "<td data-title='Acción' class='text-center'>"
                            + "<div class='btn-group btn-group-sm'>"
                                + "<button type='button' data-id=" + pagoId + " class='btn btn-warning deleteButton'><i class='fas fa-trash'></i></button>"
                            + "</div>"
                        + "</td>"
                        + "</tr>";
            $("#tbl_payments tbody").append(markup);

            TableData.push({
                "ptype" : "EF"
                , "monto": amount
            });

            // Hide the dialog
            $(cashForm).parents('.bootbox').modal('hide');

        } else {
            $.alert({
              icon: 'fas fa-bug',
              title: 'Error!',
              theme: 'material',
              type: 'red',
              content: 'Usted ya ha ingresado esta forma de pago.',
            });
        }
    });

    /* Functions */
    var loadForm = function () {
        var btn = $(this);

        console.log(btn.attr("data-url"));
        $.ajax({
            url:  btn.attr("data-url"),
            success: function(response, textStatus, xhr) {
                console.log(response);
                if (response.total_filas > 0) {
                    var grand_total = $("#lblTotal").text();

                    // Show the dialog
                    bootbox
                        .dialog({
                            title: 'COBRO EN EFECTIVO',
                            message: cashForm,
                            //size: 'small',
                            onEscape: true,
                            show: false // We will show it manually later
                        })
                        .on('shown.bs.modal', function() {
                            // Show the cash form
                            cashForm.style.display = 'block';

                            // Reset form
                            fv.resetForm(true);

                            $('#cashForm')
                                .find('[name="lblGrandTotal"]').text(grand_total);
                            $('#cashForm')
                                .find('[name="dlg_grand_total"]').val(grand_total);

                            var simbolo = getCurrencySymbol('en-US', 'USD');
                            $("#lblexchange_money").text(simbolo + ' ' + '0'.toLocaleString());

                            //ENVIAR EL FOCO A MONTO RECIBIDO
                            var recibido =  toFloat(grand_total);

                            $('#cashForm')
                                .find('[name="amount_received"]').val(recibido.toLocaleString()).change();

                            $('#cashForm')
                                .find('[name="amount_received"]').focus().select();
                        })
                        .on('hide.bs.modal', function() {
                            // Bootbox will remove the modal (including the body which contains the login form)
                            // after hiding the modal
                            // Therefor, we need to backup the form

                            cashForm.style.display = 'none';
                            document.body.appendChild(cashForm);
                        })
                        .modal('show');

                } else {
                    mensaje('¡ Ningún registro encontrado !', 'error')
                }
            },
            error : function(xhr, textStatus, errorThrown) {
              $.alert({
                icon: 'fas fa-bug',
                title: 'Error!',
                theme: 'material',
                type: 'red',
                content: 'Error al totalizar items',
              });
            }
        });
    };

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

    /* Binding */

    // Create payment
    $(".js-cash-payment").click(loadForm);

});
