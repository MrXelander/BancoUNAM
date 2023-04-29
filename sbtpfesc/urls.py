"""sbtpfesc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from login import views

urlpatterns = [
    #path('admin/', admin.site.urls, name="admin"),
    path('login', views.iniciar_sesion, name="login"),
    path('terms', views.terminos, name="terms"),
    path('signup', views.registrar_usuario, name="signup"),
    path('logout', views.logout_view, name="logout"),
    path('', views.dashboard, name="dashboard"),
    path('deposits', views.depositos, name="deposits"),
    path('bankaccounts', views.cuentas_bancarias, name='cuentas'),
    path('bankaccounts/new', views.cuentas_nueva, name='cuenta_nueva'),
    path('bankaccounts/<int:cuenta_id>/', views.detalle_cuenta_bancaria, name='cuenta_detalle'),
    path('transfer', views.transferencias, name="transfers"),
    path('movements', views.movimientos, name="movements"),
    path('editprofile', views.editarCuenta, name="edit"),
    path('loans', views.prestamos, name='loan'),
    path('loans/new', views.prestamos_nuevo, name='nuevo_prestamo')
]
