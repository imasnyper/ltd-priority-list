$(document).ready(() => {
    $('.mon, .tue, .wed, .thu, .fri, .sat, .sun, .noday, .day-table').width((index, currentWidth) => {
        let w = $('.uk-container').width();
        return w / 7;
    });

    $('.single-day-event, .multi-day-start').width((index, currentWidth) => {
        let w = $('uk-container').width();
        return (w / 7) - 30;
    })
});