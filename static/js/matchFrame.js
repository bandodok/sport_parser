function createMatchFrame(block, finished_matches) {

    Object.keys(finished_matches).forEach(function(key) {
        // key - ключ, match[key] - значение
        let match_data = finished_matches[key];


        let body = document.getElementById(block);

        let match = document.createElement('a');
        match.href =  `/${CONFIG}/match/${match_data["id"]}/`; // 877160

        let div = document.createElement('div');
        div.className = "match";
        div.id = "past_match";


        let team_left = document.createElement('div');
        team_left.className = "team_left";

        let team_left_name = document.createElement('a');
        team_left_name.id = "teamLeft";
	    team_left_name.setAttribute("id", "teamLeft");
        team_left_name.href = `/${CONFIG}/team/${match_data["team1_id"]}`; // 199
        team_left_name.innerHTML = match_data["team1_name"]; // "Авангард"

        let team_left_img = document.createElement('img');
        team_left_img.src = match_data["team1_image"]; // "https://www.khl.ru/images/teams/ru/1097/34";
        team_left_img.alt = match_data["team1_name"]; // "Авангард";
        team_left_img.className = "last_logo";

        team_left.appendChild(team_left_name);
        team_left.appendChild(team_left_img);


        let match_info = document.createElement('div');
        match_info.className = "match_info";

        let date = document.createElement('p');
        date.innerHTML = new Date(match_data["date"]).toLocaleDateString(); // "1.09.2021"

        let score = document.createElement('a');
        score.href = `/${CONFIG}/match/${match_data["id"]}/`; // 877160

        let score_p = document.createElement('p');
        score_p.className = "last_score";
        if (match_data["status"] === 'finished') {
            score_p.innerHTML = match_data["team1_score"]['match'] + " - " + match_data["team2_score"]['match']; // "4 - 0"
        }
        else if (match_data["status"] === 'scheduled') {
            let time = new Date(match_data["date"]).toLocaleTimeString().substring(0, 5);
            if (time[0] === '0') {
                time = time.substring(1, 5)
            }
            score_p.innerHTML = time;
        }
        else {
            score_p.innerHTML = match_data['match_data']["team_1_score"] + " - " + match_data['match_data']["team_2_score"];
            date.innerHTML = 'live'
        }

        score.appendChild(score_p);

        let score_p_extra = document.createElement('p');
        if (match_data["status"] === 'finished') {
            score_p_extra.className = "last_score_extra";
            let period_score = {};
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
            for (const [_, value] of Object.entries(period_score)) {
                score_p_extra.innerHTML = score_p_extra.innerHTML + " " + value
            }
            score.appendChild(score_p_extra);
        }

        if (match_data["status"] === 'postponed') {
            score_p_extra.id = "postponed";
            score_p_extra.innerHTML = "Отменен"
            score.appendChild(score_p_extra);
        }

        if (match_data["status"] !== 'postponed' &&
            match_data["status"] !== 'scheduled' &&
            match_data["status"] !== 'finished') {
            score_p_extra.id = "live";
            score_p_extra.innerHTML = match_data["match_data"]["match_status"]
            score.appendChild(score_p_extra);
        }

        match_info.appendChild(date);
        match_info.appendChild(score);


        let team_right = document.createElement('div');
        team_right.className = "team_right";

        let team_right_img = document.createElement('img');
        team_right_img.src = match_data["team2_image"]; // "https://www.khl.ru/images/teams/ru/1097/2"
        team_right_img.alt = match_data["team2_name"]; // "ЦСКА"
        team_right_img.className = "last_logo";

        let team_right_name = document.createElement('a');
        team_right_name.id = "teamRight";
        team_right_name.href = `/${CONFIG}/team/${match_data["team2_id"]}`; // 189
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
    let body = document.getElementById(block);
    body.innerHTML = '';
}