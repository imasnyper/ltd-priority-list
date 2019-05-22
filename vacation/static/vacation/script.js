$(document).ready(() => {
    $('td').width((index, currentWidth) => {
        let w = $('.uk-container').width();
        return w / 7;
    })
});