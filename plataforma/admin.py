from django.contrib import admin
from .models import Pacientes, DdosPaciente, Refeicao, Opcao

admin.site.register(Pacientes)
admin.site.register(DdosPaciente)
admin.site.register(Refeicao)
admin.site.register(Opcao)