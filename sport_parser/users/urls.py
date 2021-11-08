from django.urls import path
from sport_parser.users import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.Registration.as_view(), name='registration'),
    path('profile/<int:pk>', views.Profile.as_view(), name='profile'),
]

urlpatterns += staticfiles_urlpatterns()
