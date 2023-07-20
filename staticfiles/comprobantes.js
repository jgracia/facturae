$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-comprobante .modal-content").html("");
        $("#modal-comprobante").modal("show");
      },
      success: function (data) {
        $("#modal-comprobante .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#comprobante-table tbody").html(data.html_comprobante_list);
          $("#modal-comprobante").modal("hide");
        }
        else {
          $("#modal-comprobante .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */

  // Create comprobante
  $(".js-create-comprobante").click(loadForm);
  $("#modal-comprobante").on("submit", ".js-comprobante-create-form", saveForm);

  // Update comprobante
  $("#comprobante-table").on("click", ".js-update-comprobante", loadForm);
  $("#modal-comprobante").on("submit", ".js-comprobante-update-form", saveForm);

  // Delete comprobante
  $("#comprobante-table").on("click", ".js-delete-comprobante", loadForm);
  $("#modal-comprobante").on("submit", ".js-comprobante-delete-form", saveForm);

});
