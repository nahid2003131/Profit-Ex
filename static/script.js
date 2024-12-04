const search = document.querySelector('.input-group input'),
    table_rows = document.querySelectorAll('tbody tr'),
    table_headings = document.querySelectorAll('thead th');

// 1. Searching for specific data of HTML table
search.addEventListener('input', searchTable);

function searchTable() {
    const search_data = search.value.toLowerCase();

    table_rows.forEach((row, i) => {
        const table_data = row.textContent.toLowerCase();
        const isVisible = table_data.indexOf(search_data) >= 0;
        row.classList.toggle('hide', !isVisible);

        // Remove inline style to avoid gaps
        if (!isVisible) {
            row.style.removeProperty('background-color');
        } else {
            row.style.backgroundColor = (i % 2 == 0) ? 'transparent' : '#0000000b';
        }
    });

    const visible_rows = document.querySelectorAll('tbody tr:not(.hide)');
    visible_rows.forEach((visible_row, i) => {
        visible_row.style.backgroundColor = (i % 2 == 0) ? 'transparent' : '#0000000b';
    });
}

// 2. Sorting | Ordering data of HTML table
table_headings.forEach((head, i) => {
    let sort_asc = true;
    head.onclick = () => {
        table_headings.forEach(head => head.classList.remove('active'));
        head.classList.add('active');

        document.querySelectorAll('td').forEach(td => td.classList.remove('active'));
        table_rows.forEach(row => {
            row.querySelectorAll('td')[i].classList.add('active');
        });

        head.classList.toggle('asc', sort_asc);
        sort_asc = head.classList.contains('asc') ? false : true;

        sortTable(i, sort_asc);
    }
});

function sortTable(column, sort_asc) {
    [...table_rows].sort((a, b) => {
        let first_row, second_row;

        if (column === 0) { // If sorting by employee_id
            first_row = parseInt(a.querySelectorAll('td')[column].textContent) || 0;
            second_row = parseInt(b.querySelectorAll('td')[column].textContent) || 0;
        } else {
            first_row = a.querySelectorAll('td')[column].textContent.toLowerCase();
            second_row = b.querySelectorAll('td')[column].textContent.toLowerCase();
        }

        return sort_asc ? (first_row > second_row ? 1 : -1) : (first_row < second_row ? 1 : -1);
    })
        .forEach(sorted_row => document.querySelector('tbody').appendChild(sorted_row));
}
