$(document).ready(function () {
    let selectedCustomer;
    $("#id_customer").each(function () {
        selectedCustomer = $(this).children("option:selected").val();
    });
    let changeLink = function () {
        $(".add-another").each(function () {
            let oldUrl = $(this).attr("href");

            let end = oldUrl.indexOf("?");
            if (end !== -1) {
                oldUrl = oldUrl.substring(0, end)
            }
            let newUrl = oldUrl + "?next=" + window.location.pathname;
            newUrl = newUrl + "&cust=" + selectedCustomer;
            $(this).attr("href", newUrl);
        });
    };
    changeLink();

    $("#id_customer").change(function () {
        selectedCustomer = $(this).children("option:selected").val();
        changeLink()
    });
    let customerIndex = window.location.href.indexOf("?cust=");
    if (customerIndex !== -1) {
        let customerNumber = window.location.href.substring(customerIndex + 6, window.location.href.length);
        $("#id_customer").val(customerNumber).change();
    }
});
