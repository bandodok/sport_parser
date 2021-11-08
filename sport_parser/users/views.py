from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from sport_parser.users.forms import RegistrationForm
from django.contrib.auth.mixins import UserPassesTestMixin


class Registration(CreateView):
    form_class = RegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        super(Registration, self).form_valid(form)
        messages.success(self.request, 'Регистрация прошла успешно')
        return redirect(self.success_url)


class Login(LoginView):
    model = User
    template_name = 'users/login.html'

    def form_valid(self, form):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            messages.success(self.request, 'Вы залогинены')
            login(self.request, user)
            return redirect(reverse_lazy('profile', args=[self.request.user.id]))
        else:
            messages.error(
                self.request,
                'Пожалуйста, введите правильные имя пользователя и пароль.')
            return redirect(self.request.META.get('HTTP_REFERER'))


class Profile(UserPassesTestMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def test_func(self):
        obj = self.get_object()
        return obj.id == self.request.user.id

    def handle_no_permission(self):
        messages.error(self.request, 'Permission denied')
        return redirect(self.request.META.get('HTTP_REFERER'))


class Logout(View):

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(self.request, 'Вы разлогинены')
        return redirect('/')
