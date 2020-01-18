$(document).ready(function () {
    $(".date-input").flatpickr();

    let oldIndex;
    $(".machine-table").sortable({
        containerSelector: 'table',
        itemPath: '> tbody',
        itemSelector: 'tr',
        placeholder: '<tr class="placeholder"/>',
        delay: 0.5,
        onDragStart: ($item, container, _super) => {
          oldIndex = $item.index();
        },
        onDrop: ($item, container, _super) => {
            let new_order = $item.index() + 1;
            // let machine_name = $item.closest('table').find('.machine-name')[0].innerText;
            let job_href = $item.children()[1].firstElementChild.attributes['0'].nodeValue;
            let job_and_machine = job_href.substring(5);
            console.log(job_and_machine);
            window.location.href = "job/to/" + job_and_machine + "/" + new_order;
            _super($item, container);
        }
    })
});
