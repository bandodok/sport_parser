from sport_parser.khl.parsers.request import get_request_content


def get_khl_protocol(match_id):
    """Возвращает протокол по id матча в виде двух списков - для домашней и для гостевой команды"""
    url = f"https://text.khl.ru/text/{match_id}.html"
    soup = get_request_content(url)
    match_status = soup.find('dd', class_="b-period_score")
    if not match_status or match_status.text != 'матч завершен':
        return f'match not found {match_id}'

    # Общего количества бросков нет в протоколе, берется отдельно из текстовой трансляции
    text_stats = soup.find_all('p', class_='e-action_txt')

    match_stats = {}
    for stats in text_stats:
        if 'Статистика матча:' in stats.text or 'Game stats:' in stats.text:
            if match_stats.get('match'):
                continue
            match_stats['match'] = stats.text
        if 'Статистика 1-го периода:' in stats.text or 'Stats of 1st period:' in stats.text:
            match_stats['p1'] = stats.text
        if 'Статистика 2-го периода:' in stats.text or 'Stats of 2nd period:' in stats.text:
            match_stats['p2'] = stats.text
        if 'Статистика 3-го периода:' in stats.text or 'Stats of 3rd period:' in stats.text:
            match_stats['p3'] = stats.text
        if 'Статистика овертайма:' in stats.text or 'Stats of overtime:' in stats.text:
            match_stats['ot'] = stats.text

    sh_home = 0
    sh_guest = 0
    g_home = {}
    g_guest = {}

    score_status = soup.find('dt', class_="b-total_score").h3
    if 'Б' in score_status.text:
        score = score_status.text.split('–')
        score[0] = int(score[0])
        score[1] = int(score[1][:-1])
        if score[0] > score[1]:
            g_home['b'] = 1
            g_guest['b'] = 0
        else:
            g_home['b'] = 0
            g_guest['b'] = 1

    if not match_stats.get('p1') or not match_stats.get('p2') or not match_stats.get('p3'):
        sh_home = match_stats['match'].split(':')[2].split('-')[0].strip()
        sh_guest = match_stats['match'].split(':')[2].split('-')[1].split(' ')[0]
    else:
        for key, value in match_stats.items():
            if key == 'match':
                continue
            sh_home += int(value.split(':')[2].split('-')[0].strip())
            sh_guest += int(value.split(':')[2].split('-')[1].split(' ')[0])
            g_home[key] = int(value.split(':')[4].split('-')[0].strip())
            g_guest[key] = int(value.split(':')[4].split('-')[1].split(' ')[0])

    team_stats = soup.find_all('div', class_="table-responsive")
    head = [x.find_all('th') for x in team_stats][0]
    body = [x.find_all('td') for x in team_stats][0]
    columns = [i.text.strip() for i in head]
    rows = [i.text.strip() for i in body]

    # находим индекс объединенной ячейки чтобы дублировать его во вторую строку
    rowspan = {body.index(i): i.text.strip() for i in body if i.attrs == {'rowspan': '2'}}
    for k, v in rowspan.items():
        len_ = int((len(rows) + 1) / 2)
        rows.insert((k + len_), v)

    stat_dict = {
        'Команда': 'team',
        'Ш': 'g',
        'БВ': 'sog',
        'Штр': 'penalty',
        'ВВбр': 'faceoff',
        '%ВВбр': 'faceoff_p',
        'БлБ': 'blocks',
        'СПр': 'hits',
        'ФоП': 'fop',
        'ВВА': 'time_a',
        'ВВШ': 'vvsh',
        'НВШ': 'nshv',
        'ПД': 'pd'
    }

    row_home = {stat_dict[stat]: value for stat, value in zip(columns, rows)}
    row_guest = {stat_dict[stat]: value for stat, value in zip(columns, rows[len(columns):])}

    row_home.update({
        'match_id': match_id,
        'sh': sh_home,
        'g_1': g_home.get('p1'),
        'g_2': g_home.get('p2'),
        'g_3': g_home.get('p3'),
        'g_ot': g_home.get('ot'),
        'g_b': g_home.get('b'),
    })
    row_guest.update({
        'match_id': match_id,
        'sh': sh_guest,
        'g_1': g_guest.get('p1'),
        'g_2': g_guest.get('p2'),
        'g_3': g_guest.get('p3'),
        'g_ot': g_guest.get('ot'),
        'g_b': g_guest.get('b'),
    })

    return row_update_type(row_home), row_update_type(row_guest)


def row_update_type(row):
    """Приводит некорректные типы данных в протоколах к корректному
    для восприятия базой данных"""
    for stat, value in row.items():
        if stat in ('time_a', 'vvsh', 'nshv'):
            if value == "":
                row[stat] = '00:00:00'
            else:
                row[stat] = f'00:{value}'
        elif not value:
            row[stat] = 0
    return row
