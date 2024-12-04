const search = document.querySelector('.input-group input');
const tableRows = document.querySelectorAll('tbody tr');
const tableHeadings = document.querySelectorAll('thead th');

// 1. Searching for specific data of HTML table
search.addEventListener('input', searchTable);

function searchTable() {
    const searchData = search.value.toLowerCase();

    tableRows.forEach(row => {
        const rowData = row.textContent.toLowerCase();
        const isVisible = rowData.includes(searchData);
        row.classList.toggle('hide', !isVisible);

        // Remove inline style to avoid gaps
        if (!isVisible) {
            row.style.removeProperty('background-color');
        }
    });

    const visibleRows = document.querySelectorAll('tbody tr:not(.hide)');
    visibleRows.forEach((visibleRow, i) => {
        visibleRow.style.backgroundColor = (i % 2 === 0) ? 'transparent' : '#0000000b';
    });
}

// 2. Sorting | Ordering data of HTML table
tableHeadings.forEach((head, i) => {
    let sortAsc = true;
    head.addEventListener('click', () => {
        tableHeadings.forEach(head => head.classList.remove('active'));
        head.classList.add('active');

        document.querySelectorAll('td').forEach(td => td.classList.remove('active'));
        tableRows.forEach(row => {
            row.querySelectorAll('td')[i].classList.add('active');
        });

        head.classList.toggle('asc', sortAsc);
        sortAsc = !sortAsc;

        sortTable(i, sortAsc);
    });
});

function sortTable(column, sortAsc) {
    const sortedRows = [...tableRows].sort((a, b) => {
        let firstRow, secondRow;

        if (column === 2) { // Sorting by Percentage
            firstRow = parseFloat(a.querySelectorAll('td')[column].textContent.replace('%', '')) || 0;
            secondRow = parseFloat(b.querySelectorAll('td')[column].textContent.replace('%', '')) || 0;
        } else if (column === 0) { // If sorting by employee_id
            firstRow = parseInt(a.querySelectorAll('td')[column].textContent) || 0;
            secondRow = parseInt(b.querySelectorAll('td')[column].textContent) || 0;
        } else {
            firstRow = a.querySelectorAll('td')[column].textContent.toLowerCase();
            secondRow = b.querySelectorAll('td')[column].textContent.toLowerCase();
        }

        return sortAsc ? (firstRow > secondRow ? 1 : -1) : (firstRow < secondRow ? 1 : -1);
    });

    sortedRows.forEach(sortedRow => document.querySelector('tbody').appendChild(sortedRow));
}
