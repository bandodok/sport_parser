/**
 * Создает блоки матчей.
 * @param {string} block id блока, внутри которого будут созданы блоки матчей
 * @param {Map} matches словарь с информацией по матчам
 */
function createMatchFrame(block, matches) {

    Object.keys(matches).forEach(function(key) {
        // key - ключ, match[key] - значение
        let match_data = matches[key];

        let body = document.getElementById(block);

        let match = document.createElement('a');
        match.href =  `/${CONFIG}/match/${match_data["id"]}/`;

        let div = document.createElement('div');
        div.className = "match";
        div.id = "past_match";

        let team_left = document.createElement('div');
        team_left = setLeftTeam(team_left, match_data)

        let match_info = document.createElement('div');
        match_info.className = "match_info";

        let date = document.createElement('p');
        date = setDate(date, match_data);

        let score = document.createElement('a');
        score = setScore(score, match_data);

        match_info.appendChild(date);
        match_info.appendChild(score);

        let team_right = document.createElement('div');
        team_right = setRightTeam(team_right, match_data)

        div.appendChild(team_left);
        div.appendChild(match_info);
        div.appendChild(team_right);

        match.appendChild(div);
        body.appendChild(match);
    });
}


/**
 * Очищает блок с матчами.
 * @param {string} block id блока, который будет очищен
 */
function clearBody(block) {
    let body = document.getElementById(block);
    body.innerHTML = '';
}


/**
 * Формирует представление даты матча.
 * Если матч идет сейчас, вместо даты прописывается 'live'.
 * @param {HTMLElement} block блок даты
 * @param {Map} match_data данные матча
 * @returns {HTMLElement} блок даты
 */
function setDate(block, match_data) {
    block.innerHTML = new Date(match_data["date"]).toLocaleDateString();
    if (match_data["status"] === 'live') {
        block.innerHTML = 'live'
    }
    return block
}


/**
 * Формирует представление счета матча.
 * Если матч запланирован, то вместо счета будет показано время.
 * @param {HTMLElement} block блок счета матча
 * @param {Map} match_data данные матча
 * @returns {HTMLElement} блок счета матча
 */
function setScore(block, match_data) {
    block.href = `/${CONFIG}/match/${match_data["id"]}/`;

    let score_p = document.createElement('p');
    score_p.className = "last_score";

    if (['scheduled', 'postponed'].includes(match_data["status"])) {
        let time = new Date(match_data["date"]).toLocaleTimeString().substring(0, 5);
        if (time[0] === '0') {
            time = time.substring(1, 5)
        }
        score_p.innerHTML = time;
    }
    else {
        score_p.innerHTML = `${match_data["team1_score"]['match']} - ${match_data["team2_score"]['match']}`;
    }
    block.appendChild(score_p);
    block = setExtraScore(block, match_data)
    return block
}


/**
 * Формирует представление дополнительной информации под счетом матча.
 * Если матч запланирован, ничего не будет добавлено.
 * Если матч завершен, будет показан счет по периодам и были ли в матче овертайм или буллиты.
 * Если матч идет сейчас, будет отображен статус 'live' и показан текущий период.
 * @param {HTMLElement}block блок счета матча
 * @param {Map} match_data данные матча
 * @returns {HTMLElement} блок счета матча
 */
function setExtraScore(block, match_data) {
    let score_p_extra = document.createElement('p');

    if (match_data["status"] === 'scheduled') {
        return block
    }
    else if (match_data["status"] === 'finished') {
        score_p_extra.className = "last_score_extra";
        let period_score = {};
        period_score['p1'] = ` ${match_data["team1_score"]['p1']}-${match_data["team2_score"]['p1']} `
        period_score['p2'] = ` ${match_data["team1_score"]['p2']}-${match_data["team2_score"]['p2']} `
        period_score['p3'] = ` ${match_data["team1_score"]['p3']}-${match_data["team2_score"]['p3']} `

        if (match_data["penalties"] === true) {
            score_p_extra.innerHTML = 'Б<br>'
            period_score['ot'] = `${match_data["team1_score"]['ot']}-${match_data["team2_score"]['ot']}`
            period_score['b'] = `${match_data["team1_score"]['b']}-${match_data["team2_score"]['b']}`
        }
        if (match_data["overtime"] === true) {
            score_p_extra.innerHTML = 'ОТ<br>'
            period_score['ot'] = `${match_data["team1_score"]['ot']}-${match_data["team2_score"]['ot']}`
        }
        for (const [_, value] of Object.entries(period_score)) {
            score_p_extra.innerHTML = score_p_extra.innerHTML + " " + value
        }
    }

    else if (match_data["status"] === 'postponed') {
        score_p_extra.id = "postponed";
        score_p_extra.innerHTML = "Отменен"
    }

    else {
        score_p_extra.id = "live";
        score_p_extra.innerHTML = match_data["live_status"]
    }
    block.appendChild(score_p_extra);
    return block
}

/**
 * Формирует представление команды слева.
 * @param {HTMLElement} block блок команды слева
 * @param {Map} match_data данные матча
 * @returns {HTMLElement} блок команды слева
 */
function setLeftTeam(block, match_data) {
    block.className = "team_left";

    let team_left_name = document.createElement('a');
    team_left_name.id = "teamLeft";
    team_left_name.setAttribute("id", "teamLeft");
    team_left_name.href = `/${CONFIG}/team/${match_data["team1_id"]}`;
    team_left_name.innerHTML = match_data["team1_name"];

    let team_left_img = document.createElement('img');
    team_left_img.src = match_data["team1_image"];
    team_left_img.alt = match_data["team1_name"];
    team_left_img.className = "last_logo";

    block.appendChild(team_left_name);
    block.appendChild(team_left_img);
    return block
}


/**
 * Формирует представление команды справа.
 * @param {HTMLElement} block блок команды справа
 * @param {Map} match_data данные матча
 * @returns {HTMLElement} блок команды справа
 */
function setRightTeam(block, match_data) {
    block.className = "team_right";

    let team_right_img = document.createElement('img');
    team_right_img.src = match_data["team2_image"];
    team_right_img.alt = match_data["team2_name"];
    team_right_img.className = "last_logo";

    let team_right_name = document.createElement('a');
    team_right_name.id = "teamRight";
    team_right_name.href = `/${CONFIG}/team/${match_data["team2_id"]}`;
    team_right_name.innerHTML = match_data["team2_name"];

    block.appendChild(team_right_img);
    block.appendChild(team_right_name);
    return block
}