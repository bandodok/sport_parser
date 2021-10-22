function filterCalendar(elementID) {
    let matches = document.getElementsByClassName('match')
    var x=0
    var status = ''
    switch (elementID) {
        case 'all':
            for(x; x < matches.length; x++) {
                status = matches[x].id
                if (status === 'past_match') {
                    matches[x].style.display = 'flex';
                } else {
                    matches[x].style.display = 'flex';
                }
            }
            document.getElementById('calendarTitle').innerHTML = 'Все матчи';
            break;
        case 'past':
            for(x; x < matches.length; x++) {
                status = matches[x].id
                if (status === 'past_match') {
                    matches[x].style.display = 'flex';
                } else {
                    matches[x].style.display = 'none';
                }
            }
            document.getElementById('calendarTitle').innerHTML = 'Прошедшие матчи';
            break;
        case 'future':
            for(x; x < matches.length; x++) {
                status = matches[x].id
                if (status === 'past_match') {
                    matches[x].style.display = 'none';
                } else {
                    matches[x].style.display = 'flex';
                }
            }
            document.getElementById('calendarTitle').innerHTML = 'Будущие матчи';
            break;
        default:
            break;
    }
    }

window.onload = function() {
    createFinishedMatch('team1', window.first_matches)
    let url = '/khl/calendar_f/' + window.season;
    let f = new XMLHttpRequest();
    f.open('GET', url);
    f.responseType = 'json';
    f.send();
    f.onload = function() {
        const finished_matches = f.response;

        url = '/khl/calendar_u/' + window.season;
        let r = new XMLHttpRequest();
        r.open('GET', url);
        r.responseType = 'json';
        r.send();
        r.onload = function() {
            const unfinished_matches = r.response;
            createUnfinishedMatch('team1', unfinished_matches)
        }
        createFinishedMatch('team1', finished_matches)
    }
};
