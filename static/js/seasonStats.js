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
    const path = `/${CONFIG}/team/`;
    if (window.event.ctrlKey) {
        open(path + team_id).focus();
    }
    else {
        document.location.href = path + team_id;
    }
}

function middleGotoTeam(team_id) {
    const path = `/${CONFIG}/team/`;
    let e = window.event
    if ((e.button === 4) || (e.button === 1)) {
        open(path + team_id).focus();
    }
}

function toggleGloss() {
    const gloss = document.getElementById('glossary')
    switch (gloss.className) {
        case 'off':
            gloss.className = 'on'
            break
        case 'on':
            gloss.className = 'off'
            break
    }
}

let expandTimer = []

function tooltip(id) {
    let element = document.getElementById(id)
    if (!(id in GLOSSARY)) return
    element.style.transitionDelay = "0.5s, 0.7s, 0.5s, 0.5s, 0.5s, 0.7s, 0.7s"
    element.style.transitionProperty = "opacity, max-height, width, padding-left, padding-right, padding-top, padding-bottom"
    element.style.transitionDuration = "0s, 0.2s, 0.2s, 0.2s, 0.2s, 0.2s, 0.2s"
    element.style.transitionTimingFunction = 'ease-in-out'
    element.style.opacity = '100%'
    element.style.maxHeight = '200px'
    element.style.width = '200px'
    element.style.paddingLeft = '15px'
    element.style.paddingRight = '15px'
    element.style.paddingTop = '10px'
    element.style.paddingBottom = '10px'

    setTimeout(computeStyle, 900, element)
    expandTimer[id] = setTimeout(tooltipExpand, 2500, id);
}

function computeStyle(element) {
    let computedStyle = getComputedStyle(element)
    element.style.maxHeight = computedStyle.height
}

function tooltipExpand(id) {
    let element = document.getElementById(id)

    let extra = GLOSSARY[id]['long']
    if (extra === "" || extra === undefined) return
    element.innerHTML = element.innerHTML + "<br><br>" + extra

    element.style.transitionTimingFunction = 'ease-in-out'
    element.style.transitionDelay = "0s"
    element.style.transitionProperty = "max-height"
    element.style.transitionDuration = "0.7s"
    element.style.maxHeight = '500px'
}

function tooltipHide(id) {
    let element = document.getElementById(id)
    element.style.transitionDelay = "0s"
    element.style.transitionProperty = "opacity, max-height, width, padding-left, padding-right, padding-top, padding-bottom"
    element.style.transitionDuration = "0s"
    element.style.opacity = '0'
    element.style.maxHeight = '0'
    element.style.width = '0'
    element.style.paddingLeft = '0'
    element.style.paddingRight = '0'
    element.style.paddingTop = '0'
    element.style.paddingBottom = '0'
    element.innerHTML = GLOSSARY[id]['short']
    clearTimeout(expandTimer[id])
}
