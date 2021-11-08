from django.contrib import admin
from sport_parser.khl.models import KHLTeams, KHLMatch, KHLProtocol


admin.site.register(KHLTeams)
admin.site.register(KHLMatch)
admin.site.register(KHLProtocol)
