//////////////// formateador de números ////////////////
var formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
});

// funcion para quitar formato de moneda
function number_format(amount, decimals) {
    amount += ''; // por si pasan un numero en vez de un string
    amount = parseFloat(amount.replace(/[^0-9\.]/g, '')); // elimino cualquier cosa que no sea numero o punto

    decimals = decimals || 0; // por si la variable no fue fue pasada

    // si no es un numero o es igual a cero retorno el mismo cero
    if (isNaN(amount) || amount === 0)
        return parseFloat(0).toFixed(decimals);

    // si es mayor o menor que cero retorno el valor formateado como numero
    amount = '' + amount.toFixed(decimals);

    var amount_parts = amount.split('.'),
            regexp = /(\d+)(\d{3})/;

    while (regexp.test(amount_parts[0]))
        amount_parts[0] = amount_parts[0].replace(regexp, '$1' + ',' + '$2');

    return amount_parts.join('.');
}

function toFloat(num) {
    dotPos = num.indexOf('.');
    commaPos = num.indexOf(',');

    if (dotPos < 0)
        dotPos = 0;

    if (commaPos < 0)
        commaPos = 0;

    if ((dotPos > commaPos) && dotPos)
        sep = dotPos;
    else {
        if ((commaPos > dotPos) && commaPos)
            sep = commaPos;
        else
            sep = false;
    }

    if (sep == false)
        return parseFloat(num.replace(/[^\d]/g, ""));

    return parseFloat(
        num.substr(0, sep).replace(/[^\d]/g, "") + '.' +
        num.substr(sep+1, num.length).replace(/[^0-9]/, "")
    );

}

function getCurrencySymbol (locale, currency) {
  return (0).toLocaleString(
    locale,
    {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }
  ).replace(/\d/g, '').trim()
}
