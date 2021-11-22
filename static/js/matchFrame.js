function createMatchFrame(block, finished_matches) {

    Object.keys(finished_matches).forEach(function(key) {
        // key - ключ, match[key] - значение
        var match_data = finished_matches[key];


        var body = document.getElementById(block)

        var match = document.createElement('a');
        match.href =  "/khl/match/" + match_data["id"] + "/"; // 877160

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

        var team_left_img = document.createElement('img');
        team_left_img.src = match_data["team1_image"]; // "https://www.khl.ru/images/teams/ru/1097/34";
        team_left_img.alt = match_data["team1_name"]; // "Авангард";
        team_left_img.className = "last_logo";

        team_left.appendChild(team_left_name);
        team_left.appendChild(team_left_img);


        var match_info = document.createElement('div');
        match_info.className = "match_info";

        var date = document.createElement('p');
        date.innerHTML = new Date(match_data["date"]).toLocaleDateString(); // "1.09.2021"

        var score = document.createElement('a');
        score.href = "/khl/match/" + match_data["id"] + "/"; // 877160

        var score_p = document.createElement('p');
        score_p.className = "last_score";
        if (match_data["finished"] === true) {
            score_p.innerHTML = match_data["team1_score"]['match'] + " - " + match_data["team2_score"]['match']; // "4 - 0"
        }
        else {
            score_p.innerHTML = match_data["time"].substring(0, 5);
        }

        score.appendChild(score_p);

        if (match_data["finished"] === true) {
            var score_p_extra = document.createElement('p');
            score_p_extra.className = "last_score_extra";
            var period_score = {};
            period_score['p1'] = " " + match_data["team1_score"]['p1'] + "-" + match_data["team2_score"]['p1'] + " "
            period_score['p2'] = " " + match_data["team1_score"]['p2'] + "-" + match_data["team2_score"]['p2'] + " "
            period_score['p3'] = " " + match_data["team1_score"]['p3'] + "-" + match_data["team2_score"]['p3'] + " "

            if (match_data["penalties"] === true) {
                score_p_extra.innerHTML = 'Б<br>'
                period_score['ot'] = match_data["team1_score"]['ot'] + "-" + match_data["team2_score"]['ot']
                period_score['b'] = match_data["team1_score"]['b'] + "-" + match_data["team2_score"]['b']
            }
            if (match_data["overtime"] === true) {
                score_p_extra.innerHTML = 'ОТ<br>'
                period_score['ot'] = match_data["team1_score"]['ot'] + "-" + match_data["team2_score"]['ot']
            }
            for (const [key, value] of Object.entries(period_score)) {
                score_p_extra.innerHTML = score_p_extra.innerHTML + " " + value
            }
            score.appendChild(score_p_extra);
        }

        match_info.appendChild(date);
        match_info.appendChild(score);



        var team_right = document.createElement('div');
        team_right.className = "team_right";

        var team_right_img = document.createElement('img');
        team_right_img.src = match_data["team2_image"]; // "https://www.khl.ru/images/teams/ru/1097/2"
        team_right_img.alt = match_data["team2_name"]; // "ЦСКА"
        team_right_img.className = "last_logo";

        var team_right_name = document.createElement('a');
	    team_right_name.id = "teamRight";
        team_right_name.href = "/khl/team/" + match_data["team2_id"]; // 189
        team_right_name.innerHTML = match_data["team2_name"]; // "ЦСКА"

        team_right.appendChild(team_right_img);
        team_right.appendChild(team_right_name);



        div.appendChild(team_left);
        div.appendChild(match_info);
        div.appendChild(team_right);

        match.appendChild(div);
        body.appendChild(match);


    });
}


function clearBody(block) {
    var body = document.getElementById(block);
    body.innerHTML = '';
}