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
