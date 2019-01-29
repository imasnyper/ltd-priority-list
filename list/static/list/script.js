$(document).ready(function () {
    $(".add-another").each(function () {
        var oldUrl = $(this).attr("href");
        var newUrl = oldUrl + "?next=" + window.location.pathname;
        $(this).attr("href", newUrl);
    });
});