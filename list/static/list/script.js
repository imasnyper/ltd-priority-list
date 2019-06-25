$(document).ready(function () {
    $(".date-input").flatpickr();

    let oldIndex;
    $(".machine-table").sortable({
        containerSelector: 'table',
        itemPath: '> tbody',
        itemSelector: 'tr',
        placeholder: '<tr class="placeholder"/>',
        onDragStart: ($item, container, _super) => {
          oldIndex = $item.index();
        },
        onDrop: ($item, container, _super) => {
            console.log(oldIndex);
            console.log($item.index());
            window.location.href = $item.baseURI + $item.
            _super($item, container);
        }
    })
});
