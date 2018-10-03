from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin #função quando sua view é baseada em classe

from .models import User
from .forms import UserAdminCreationForm

class IndexView(LoginRequiredMixin, TemplateView ): #verifica se o usuario esta logado para mostrar o template,a ordem dos metodos importa

    template_name = 'accounts/index.html'


class RegisterView(CreateView):

    model = User
    template_name = 'accounts/register.html'
    form_class = UserAdminCreationForm
    success_url = reverse_lazy('index')

class UpdateUserView(LoginRequiredMixin, UpdateView):

    model = User
    template_name = 'accounts/update_user.html'
    fields = ['name', 'email']
    success_url = reverse_lazy('accounts:index')

    def get_object(self):
        return self.request.user



index = IndexView.as_view()
register = RegisterView.as_view()
update_user = UpdateView.as_view()
# Create your views here.
