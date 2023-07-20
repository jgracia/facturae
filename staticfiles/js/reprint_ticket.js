function reprint() {
    $.confirm({
        title: 'Reimprimir!',
        content: '' +
        '<form action="/ajax/reimprimir" class="formName">' +
            '<div class="form-group">' +
                '<label>Ingrese el número de comprobante</label>' +
                '<input type="text" placeholder="Número Interno" class="ticket form-control" required />' +
            '</div>' +
        '</form>',
        buttons: {
            formSubmit: {
                text: 'Reimprimir',
                btnClass: 'btn-blue',
                action: function () {
                    var ticket = this.$content.find('.ticket').val();
                    if(!ticket){
                        $.alert('Comprobante inválido.');
                        return false;
                    }

                    $.ajax({
                        url: "/venta/ticket/reimprimir/",
                        dataType: 'json',
                        method: 'get',
                        data: { ticket: ticket },
                    }).done(function (response) {
                        mensaje('Comprobante impreso satisfactoriamente.', 'green');
                    }).fail(function(){
                        mensaje("Error al imprimir comprobante.", 'error');
                    });
                }
            },
            formCancel: {
                text: 'Cancelar'
            },

        },
        onContentReady: function () {
            this.$content.find('.ticket').focus();

            // bind to events
            var jc = this;
            this.$content.find('form').on('submit', function (e) {
                // if the user submits the form by pressing enter in the field.
                e.preventDefault();
                jc.$$formSubmit.trigger('click'); // reference the button and click it
            });
        }
    });
}
