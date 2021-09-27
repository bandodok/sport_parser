document.addEventListener('DOMContentLoaded', () => {

    const getSort = ({ target }) => {
        const order = (target.dataset.order = -(target.dataset.order || -1));
        const index = [...target.parentNode.cells].indexOf(target);
        const collator = new Intl.Collator(['en', 'ru'], { numeric: true });
        const comparator = (index, order) => (a, b) => order * collator.compare(
            a.children[index].innerHTML,
            b.children[index].innerHTML
        );

        for(const tBody of target.closest('table').tBodies)
            tBody.append(...[...tBody.rows].sort(comparator(index, order)));

        for(const cell of target.parentNode.cells)
            cell.classList.toggle('sorted', cell === target);
    };

    document.querySelectorAll('.table_sort thead').forEach(tableTH => tableTH.addEventListener('click', () => getSort(event)));

});

function gotoTeam(team_id) {
    const path = "/khl/team/";
    if (window.event.ctrlKey) {
        open(path + team_id).focus();
    }
    else {
        document.location.href = path + team_id;
    }
}

function middleGotoTeam(team_id) {
    const path = "/khl/team/";
    e = window.event
    if ((e.button === 4) || (e.button === 1)) {
        open(path + team_id).focus();
    }
}