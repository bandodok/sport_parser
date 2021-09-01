from sport_parser.khl.models import KHLProtocol


def add_khl_protocol_to_database(protocol) -> None:
    """Добавляет данные из протокола в базу данных"""
    for row in protocol:
        KHLProtocol.objects.create(
            team_id=row[0],
            match_id=row[1],
            g=row[2],
            sog=row[3],
            penalty=row[4],
            faceoff=row[5],
            faceoff_p=row[6],
            blocks=row[7],
            hits=row[8],
            fop=row[9],
            time_a=row[10],
            vvsh=row[11],
            nshv=row[12],
            pd=row[13],
            sh=row[14]
        )
