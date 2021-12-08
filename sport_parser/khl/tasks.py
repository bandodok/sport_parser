from sport_parser.celery import app
from sport_parser.khl.config import Creator


@app.task(name='update')
def update(config):
    creator = Creator(config)
    updater = creator.get_updater()
    updater.update()


@app.task(name='parse_season')
def parse_season(config, season_id):
    creator = Creator(config)
    updater = creator.get_updater()
    updater.parse_season(season_id)
