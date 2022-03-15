import os
import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sport_parser.settings")
    django.setup()

    from sport_parser.khl.models import KHLSeason
    from sport_parser.nhl.models import NHLSeason

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
