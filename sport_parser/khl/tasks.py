from celery import shared_task

from sport_parser.khl.creator import Creator


@shared_task(name='update')
def update(config):
    creator = Creator(config)
    updater = creator.get_updater()
    updater.update()


@shared_task(name='parse_season')
def parse_season(config, season_id):
    creator = Creator(config)
    updater = creator.get_updater()
    updater.parse_season(season_id)
