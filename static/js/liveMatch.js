const LEAGUE = window.league
const MATCH_ID = window.match_id
const STATUS = window.status
let _BAR_STATS_EXIST = false


function updateScore(team_1_score, team_2_score, status) {
    let score = document.getElementById('score_time')
    score.innerHTML = `${team_1_score} - ${team_2_score}`
    let status_div = document.getElementById('arena')
    status_div.innerHTML = status
    status_div.style.color = '#ffffff'
}


function updateBarStats(data) {
    let body = document.getElementById('match_stats')
    if (!_BAR_STATS_EXIST) {
        Object.keys(data).forEach(function (stat) {
            let value = data[stat]

            let match_stat = document.createElement('div');
            match_stat.className = 'match_stat';

            let match_stat_text = document.createElement('span');
            match_stat_text.className = 'match_stat_text';
            match_stat_text.innerHTML = `${value['long_title']} (${value['short_title']})`;
            match_stat.appendChild(match_stat_text);

            let stat_lines = document.createElement('div');
            stat_lines.className = 'stat_lines';

            let stat_text_left = document.createElement('span');
            stat_text_left.className = 'match_stat_text';
            stat_text_left.style.textAlign = 'right';
            stat_text_left.innerHTML = value['left_value'];
            stat_text_left.id = `${stat}_value_left`
            stat_lines.appendChild(stat_text_left);

            let progress_left = document.createElement('div');
            progress_left.className = 'progress_left';
            stat_lines.appendChild(progress_left);

            let progress_bar_left = document.createElement('span');
            progress_bar_left.className = 'progress-bar_left';
            progress_bar_left.style.width = `${value['left_perc']}%`;
            progress_bar_left.id = `${stat}_perc_left`
            progress_left.appendChild(progress_bar_left)

            let progress_right = document.createElement('div');
            progress_right.className = 'progress_right';
            stat_lines.appendChild(progress_right);

            let progress_bar_right = document.createElement('span');
            progress_bar_right.className = 'progress-bar_right';
            progress_bar_right.style.width = `${value['right_perc']}%`;
            progress_bar_right.id = `${stat}_perc_right`
            progress_right.appendChild(progress_bar_right)

            let stat_text_right = document.createElement('span');
            stat_text_right.className = 'match_stat_text';
            stat_text_right.style.textAlign = 'left';
            stat_text_right.innerHTML = value['right_value'];
            stat_text_right.id = `${stat}_value_right`
            stat_lines.appendChild(stat_text_right);

            match_stat.appendChild(stat_lines)
            body.appendChild(match_stat)

        _BAR_STATS_EXIST = true
        })
    } else {
        Object.keys(data).forEach(function (stat) {
            let value = data[stat]
            let left_value = document.getElementById(`${stat}_value_left`)
            let right_value = document.getElementById(`${stat}_value_right`)
            let left_perc = document.getElementById(`${stat}_perc_left`)
            let right_perc = document.getElementById(`${stat}_perc_right`)
            left_value.innerHTML = value['left_value'];
            right_value.innerHTML = value['right_value'];
            left_perc.style.width = `${value['left_perc']}%`;
            right_perc.style.width = `${value['right_perc']}%`;
        })
    }
}


function getLiveMatchData() {
    const XHR = new XMLHttpRequest();

    XHR.addEventListener( "load", function(event) {
        const response = event.target.response;
        const results = response['results']
        if (results.length === 0) {
            setTimeout(window.location.reload.bind(window.location), 10000)
            return
        }
        const status = results[0]['status']
        const team_1_score = results[0]['team_1_score']
        const team_2_score = results[0]['team_2_score']
        const data = results[0]['data']
        if (status !== 'матч скоро начнется') {
            updateBarStats(data)
        }
        updateScore(team_1_score, team_2_score, status)
    } );

    let url = `/api/live_match/?league=${LEAGUE}&match_id=${MATCH_ID}`
    XHR.open( "GET", url );
    XHR.responseType = 'json';
    XHR.send()
}


if (STATUS === 'live') {
    getLiveMatchData()
    setInterval(getLiveMatchData, 60000)
}
