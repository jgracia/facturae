// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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

                    var csrftoken = getCookie('csrftoken');
                    $.ajax({
                        headers: { "X-CSRFToken": csrftoken },
                        //url: "/venta/ticket/reimprimir/",
                        url: "/venta/ajax/imprimir_ticket/",
                        dataType: 'json',
                        method: 'post',
                        //data: { ticket: ticket },
                        data: { facturaId: ticket },
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


function modificar_venta() {
  $.alert({
    title: 'Alerta!',
    content: 'Edisión no permitida!',
    type: 'orange',
  });
}

function eliminar_venta() {
  $.alert({
    title: 'Alerta!',
    content: 'Acción no permitida!',
    type: 'red',
  });
}
