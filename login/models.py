import datetime
import random
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=5)
    password = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13)
    tipo = models.CharField(max_length=50)
    telefono = models.CharField(max_length=10)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'fecha_nacimiento', 'direccion', 'ciudad', 'estado', 'codigo_postal', 'password', 'rfc', 'tipo', 'telefono']

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'usuarios'
    
    def ultimo_inicio_sesion(self):
        user_logs = self.userlog_set.order_by('-fecha_login')[:1]
        if user_logs:
            return user_logs[0].fecha_login
        else:
            return None
        
    def cuenta_bancaria_count(self):
        return self.cuentabancaria_set.count()

class CuentaBancaria(models.Model):
    tipo_de_cuenta = models.CharField(max_length=50)
    numero_de_cuenta = models.CharField(max_length=16, unique=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_de_apertura = models.DateField(default=timezone.now)
    fecha_de_expiracion = models.DateField(default=timezone.now() + timezone.timedelta(days=1460))
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'cuentas_bancarias'
    
    def ultimos_cuatro_digitos(self):
        return self.numero_de_cuenta[-4:]

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('deposito', 'Depósito'),
        ('retiro', 'Retiro'),
        ('compra', 'Compra'),
        ('transferencia', 'Transferencia'),
        ('apertura', 'Apertura'),
        ('cancelacion', 'Cancelación')
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('cancelado', 'Cancelado')
    ]
    tipo_de_transaccion = models.CharField(max_length=50, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(default=timezone.now)
    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE)
    establecimiento = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    class Meta:
        managed = False
        db_table = 'transacciones'

class Prestamo(models.Model):
    monto_del_prestamo = models.DecimalField(max_digits=10, decimal_places=2)
    tasa_de_interes = models.DecimalField(max_digits=10, decimal_places=2)
    plazo_del_prestamo = models.IntegerField()
    fecha_de_inicio = models.DateField(default=timezone.now)
    fecha_de_vencimiento = models.DateField()
    estado_del_prestamo = models.CharField(max_length=50, default='Sin pagar')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'prestamos'

    def calcular_fecha_de_vencimiento(self):
        fecha_actual = timezone.now()
        plazo_meses = self.plazo_del_prestamo
        fecha_vencimiento = fecha_actual + timezone.timedelta(days=plazo_meses*30)
        self.fecha_de_vencimiento = fecha_vencimiento
        self.save()