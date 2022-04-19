import os
import django
from django.utils import timezone


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sport_parser.settings")
    django.setup()

    from sport_parser.khl.models import KHLSeason
    from sport_parser.nhl.models import NHLSeason
    from django.contrib.auth.models import User
    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    # Create superuser
    try:
        User.objects.get(username=os.getenv('ADMIN_USERNAME'))
    except django.contrib.auth.models.User.DoesNotExist:
        User.objects.create_superuser(
            username=os.getenv('ADMIN_USERNAME'),
            password=os.getenv('ADMIN_PASSWORD'),
        )

    # Default celery beat schedule tasks
    interval, _ = IntervalSchedule.objects.get_or_create(every=10, period='minutes')
    sec_interval, _ = IntervalSchedule.objects.get_or_create(every=1, period='seconds')
    min_interval, _ = IntervalSchedule.objects.get_or_create(every=1, period='minutes')
    update_list = [
        "khl",
        "nhl"
    ]
    for item in update_list:
        task, created = PeriodicTask.objects.get_or_create(
            name=f'{item}_update',
            interval_id=interval.id,
            task='update',
            args=f'["{item}"]',
            one_off=False,
            enabled=True,
            queue='regular_update'
        )
        if created:
            task.start_time = timezone.now()
        task.save()

    task, created = PeriodicTask.objects.get_or_create(
        name='update_live_matches',
        interval_id=min_interval.id,
        task='update_live_matches',
        one_off=False,
        enabled=True,
        queue='update_live_matches'
    )
    if created:
        task.start_time = timezone.now()
    task.save()

    # KHL season settings
    KHLSeason.objects.get_or_create(id=21, external_id=1097)
    KHLSeason.objects.get_or_create(id=20, external_id=1045)
    KHLSeason.objects.get_or_create(id=19, external_id=851)
    KHLSeason.objects.get_or_create(id=18, external_id=671)
    KHLSeason.objects.get_or_create(id=17, external_id=468)

    # NHL season settings
    NHLSeason.objects.get_or_create(id=21, external_id=20212022)
    NHLSeason.objects.get_or_create(id=20, external_id=20202021)
    NHLSeason.objects.get_or_create(id=19, external_id=20192020)
    NHLSeason.objects.get_or_create(id=18, external_id=20182019)
    NHLSeason.objects.get_or_create(id=17, external_id=20172018)


if __name__ == '__main__':
    main()
