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
    let url = '/khl/calendar_f/' + window.season;
    let f = new XMLHttpRequest();
    f.open('GET', url);
    f.responseType = 'json';
    f.send();
    f.onload = function() {
        const finished_matches = f.response;
        createFinishedMatch(finished_matches)
    }

    url = '/khl/calendar_u/' + window.season;
    let r = new XMLHttpRequest();
    r.open('GET', url);
    r.responseType = 'json';
    r.send();
    r.onload = function() {
        const unfinished_matches = r.response;
        createUnfinishedMatch(unfinished_matches)
    }
};


function createFinishedMatch(finished_matches) {

    Object.keys(finished_matches).forEach(function(key) {
        // key - ключ, match[key] - значение
        var match_id = key;
        var match_data = finished_matches[key];


        var body = document.getElementById('team1')

        var match = document.createElement('a');
        match.href =  "/khl/match/" + match_id + "/"; // 877160

        var div = document.createElement('div');
        div.className = "match";
        div.id = "past_match";


        var team_left = document.createElement('div');
        team_left.className = "team_left";

        var team_left_name = document.createElement('a');
	team_left_name.id = "teamLeft";
	team_left_name.setAttribute("id", "teamLeft");
        team_left_name.href = "/khl/team/" +  match_data["team1_id"]; // 199
        team_left_name.innerHTML = match_data["team1_name"]; // "Авангард"

        var team_left_img_a = document.createElement('a');
        team_left_img_a.href = "/khl/team/" +  match_data["team1_id"]; // 199

        var team_left_img = document.createElement('img');
        team_left_img.src = match_data["team1_image"]; // "https://www.khl.ru/images/teams/ru/1097/34";
        team_left_img.alt = match_data["team1_name"]; // "Авангард";
        team_left_img.className = "last_logo";

        team_left_img_a.appendChild(team_left_img);
        team_left.appendChild(team_left_name);
        team_left.appendChild(team_left_img_a);


        var match_info = document.createElement('div');
        match_info.className = "match_info";

        var date = document.createElement('p');
        date.innerHTML = new Date(match_data["date"]).toLocaleDateString(); // "1.09.2021"

        var score = document.createElement('a');
        score.href = "/khl/match/" + match_id + "/"; // 877160

        var score_p = document.createElement('p');
        score_p.className = "last_score";
        score_p.innerHTML = match_data["team1_score"] + " - " + match_data["team2_score"]; // "4 - 0"

        score.appendChild(score_p);
        match_info.appendChild(date);
        match_info.appendChild(score);



        var team_right = document.createElement('div');
        team_right.className = "team_right";

        var team_right_img_a = document.createElement('a');
        team_right_img_a.href = "/khl/team/" + match_data["team2_id"]; // 189

        var team_right_img = document.createElement('img');
        team_right_img.src = match_data["team2_image"]; // "https://www.khl.ru/images/teams/ru/1097/2"
        team_right_img.alt = match_data["team2_name"]; // "ЦСКА"
        team_right_img.className = "last_logo";

        var team_right_name = document.createElement('a');
	team_right_name.id = "teamRight";
        team_right_name.href = "/khl/team/" + match_data["team2_id"]; // 189
        team_right_name.innerHTML = match_data["team2_name"]; // "ЦСКА"

        team_right_img_a.appendChild(team_right_img);
        team_right.appendChild(team_right_img_a);
        team_right.appendChild(team_right_name);



        div.appendChild(team_left);
        div.appendChild(match_info);
        div.appendChild(team_right);

        match.appendChild(div);
        body.appendChild(match);


    });
}


function createUnfinishedMatch(unfinished_matches) {

    Object.keys(unfinished_matches).forEach(function(key) {
        // key - ключ, match[key] - значение
        var match_id = key;
        var match_data = unfinished_matches[key];


        var body = document.getElementById('team1')

        var match = document.createElement('a');
        match.href =  "/khl/match/" + match_id + "/"; // 877160

        var div = document.createElement('div');
        div.className = "match";
        div.id = "future_match";


        var team_left = document.createElement('div');
        team_left.className = "team_left";

        var team_left_name = document.createElement('a');
	team_left_name.id = "teamLeft";
        team_left_name.href = "/khl/team/" +  match_data["team1_id"]; // 199
        team_left_name.innerHTML = match_data["team1_name"]; // "Авангард"

        var team_left_img_a = document.createElement('a');
        team_left_img_a.href = "/khl/team/" +  match_data["team1_id"]; // 199

        var team_left_img = document.createElement('img');
        team_left_img.src = match_data["team1_image"]; // "https://www.khl.ru/images/teams/ru/1097/34";
        team_left_img.alt = match_data["team1_name"]; // "Авангард";
        team_left_img.className = "last_logo";

        team_left_img_a.appendChild(team_left_img);
        team_left.appendChild(team_left_name);
        team_left.appendChild(team_left_img_a);


        var match_info = document.createElement('div');
        match_info.className = "match_info";

        var date = document.createElement('p');
        date.innerHTML = new Date(match_data["date"]).toLocaleDateString(); // "1.09.2021"

        var score = document.createElement('a');
        score.href = "/khl/match/" + match_id + "/"; // 877160

        var score_p = document.createElement('p');
        score_p.className = "last_score";
        score_p.innerHTML = match_data["time"].substring(0, 5);

        score.appendChild(score_p);
        match_info.appendChild(date);
        match_info.appendChild(score);



        var team_right = document.createElement('div');
        team_right.className = "team_right";

        var team_right_img_a = document.createElement('a');
        team_right_img_a.href = "/khl/team/" + match_data["team2_id"]; // 189

        var team_right_img = document.createElement('img');
        team_right_img.src = match_data["team2_image"]; // "https://www.khl.ru/images/teams/ru/1097/2"
        team_right_img.alt = match_data["team2_name"]; // "ЦСКА"
        team_right_img.className = "last_logo";

        var team_right_name = document.createElement('a');
	team_right_name.id = "teamRight";
        team_right_name.href = "/khl/team/" + match_data["team2_id"]; // 189
        team_right_name.innerHTML = match_data["team2_name"]; // "ЦСКА"

        team_right_img_a.appendChild(team_right_img);
        team_right.appendChild(team_right_img_a);
        team_right.appendChild(team_right_name);



        div.appendChild(team_left);
        div.appendChild(match_info);
        div.appendChild(team_right);

        match.appendChild(div);
        body.appendChild(match);


    });
}
