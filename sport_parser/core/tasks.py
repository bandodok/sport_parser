from celery import shared_task

from sport_parser.core.creator import Creator
from sport_parser.core.models import LiveMatches
from django_celery_beat.models import PeriodicTask


@shared_task(name='update', queue='regular_update')
def update(config):
    creator = Creator(config)
    updater = creator.get_updater()
    updater.update()


@shared_task(name='parse_season', queue='regular_update')
def parse_season(config, season_id):
    creator = Creator(config)
    updater = creator.get_updater()
    updater.parse_season(season_id)


@shared_task(name='schedule_live_match', queue='regular_update')
def schedule_live_match(league, match_id):
    LiveMatches.objects.get_or_create(
        league=league,
        match_id=match_id
    )
    PeriodicTask.objects.get(name=f'{league}_{match_id}_live_match').delete()

