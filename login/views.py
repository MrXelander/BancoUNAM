import hashlib
import json
import random
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from login.models import Usuario, CuentaBancaria, Transaccion, Prestamo
from decimal import Decimal

def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Encriptar la contraseña ingresada por el usuario con SHA1
        password = hashlib.sha1(password.encode()).hexdigest()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales inválidas, intente de nuevo.')
            return render(request, 'login.html', {'message': "Credenciales inválidas, intente de nuevo."})
    else:
        return render(request, 'login.html')

def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        estado = request.POST.get('estado')
        codigo_postal = request.POST.get('codigo_postal')
        rfc = request.POST.get('rfc')
        tipo = request.POST.get('tipo')
        telefono = request.POST.get('telefono')

        password = hashlib.sha1(password.encode()).hexdigest()

        # Crear un nuevo objeto de Usuario y guardarlo en la base de datos
        try:
            usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                fecha_nacimiento=fecha_nacimiento,
                direccion=direccion,
                ciudad=ciudad,
                estado=estado,
                codigo_postal=codigo_postal,
                rfc=rfc,
                tipo=tipo,
                telefono=telefono
            )
            usuario.save()
            messages.success(request, 'Registro exitoso!')
            return render(request, 'signup.html', {'message': 'Registro exitoso!'})
        except Exception as e:
            messages.error(request, 'No se pudo registrar!')
            return render(request, 'signup.html', {'message': 'No se pudo registrar!'})
    return render(request, 'signup.html')

def terminos(request):
    return render(request, 'terms.html')

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    last_login = user.last_login
    accounts = user.cuenta_bancaria_count()
    cuentas_bancarias = CuentaBancaria.objects.filter(usuario=user)
    saldo_total = cuentas_bancarias.aggregate(Sum('saldo'))['saldo__sum']
    colores_disponibles = ['green', 'olive', 'gray']
    color = random.choice(colores_disponibles)
    transferencias = Transaccion.objects.order_by('-fecha')[:3]
    suma_prestamos = Prestamo.objects.filter(usuario=user).aggregate(Sum('monto_del_prestamo'))['monto_del_prestamo__sum']
    context = {
        'username': username,
        'last_login': last_login,
        'accounts': accounts,
        'cuentas_bancarias': cuentas_bancarias,
        'colores': colores_disponibles,
        'color': color,
        'saldo_total': saldo_total,
        'transferencias': transferencias,
        'suma_prestamos': suma_prestamos
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Ha cerrado sesión exitosamente.')
        return redirect('login')
    return render(request, 'logout.html')

@login_required(login_url='login')
def depositos(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    cuentas_bancarias = user.cuentabancaria_set.all()
    context = {
        'username': username,
        'cuentas_bancarias': cuentas_bancarias
    }
    if request.method == 'POST':
        cuenta_id = request.POST.get('cuenta')
        cantidad = Decimal(request.POST.get('cantidad'))

        if cantidad > 0:
            try:
                cuenta = user.cuentabancaria_set.get(id=cuenta_id)
                transferencia = Transaccion.objects.create(
                    tipo_de_transaccion='Deposito',
                    monto=cantidad,
                    cuenta=cuenta,
                    establecimiento='UNAM',
                    descripcion='Depósito en cuenta bancaria',
                    estado='Completada'
                )
                cuenta.saldo += cantidad
                cuenta.save()
                transferencia.save()
                messages.add_message(request, 70, 'Depósito completado!')
                return redirect('dashboard')
            except Exception as e:
                print(e)
                messages.add_message(request, 90, 'Error durante la transacción!')
                return redirect('dashboard')
        else:
            messages.add_message(request, 80, 'Debe ingresar una cantidad mayor a 0')
            return redirect('deposits')
    return render(request, 'deposits.html', context)

@login_required(login_url='login')
def cuentas_bancarias(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    cuentas_bancarias = CuentaBancaria.objects.filter(usuario=user)
    saldo_total = cuentas_bancarias.aggregate(Sum('saldo'))['saldo__sum']
    colores_disponibles = ['green', 'olive', 'gray']
    context = {
        'username': username,
        'cuentas_bancarias': cuentas_bancarias,
        'colores': colores_disponibles,
        'saldo_total': saldo_total
    }
    return render(request, 'accounts.html', context)

def generar_numero_cuenta():
    bin = "123456"
    random_digits = ''.join([str(random.randint(0, 9)) for i in range(10)])
    return bin + random_digits

@login_required(login_url='login')
def cuentas_nueva(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    context = {
        'username': username,
    }
    if request.method == 'POST':
        tipo_de_cuenta = request.POST.get('tipo_de_cuenta')
        numero_de_cuenta = generar_numero_cuenta()
        num_cuentas = user.cuenta_bancaria_count()
        if num_cuentas >= 3:
            messages.add_message(request, 80, 'Parece que ya tienes mas cuentas de las permitidas!')
            return redirect('cuentas')
        else:
            try:
                cuenta = CuentaBancaria(
                    tipo_de_cuenta = tipo_de_cuenta,
                    numero_de_cuenta = numero_de_cuenta,
                    saldo = 0.0,
                    usuario = user
                )
                cuenta.save()

                transaccion_apertura = Transaccion.objects.create(
                    tipo_de_transaccion='Apertura',
                    monto=0.0,
                    cuenta=cuenta,
                    establecimiento='UNAM',
                    descripcion='Apertura de cuenta bancaria',
                    estado='Completada'
                )
                transaccion_apertura.save()
                messages.add_message(request, 70, 'Cuenta abierta de manera exitosa!')
                return redirect('cuentas')
            except Exception as e:
                print(e)
                messages.add_message(request, 90, 'Oooops, hubo un error!')
                return redirect('cuentas')
    return render(request, 'newaccount.html', context)

@login_required(login_url='login')
def transferencias(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    cuentas_bancarias = user.cuentabancaria_set.all()
    url = os.path.join( os.getcwd(), "static", "bancos.json" )
    with open(url) as f:
        bancos = json.load(f)
    if request.method == 'POST':
        cuenta_origen_id = request.POST.get('cuenta')
        cuenta_origen = get_object_or_404(CuentaBancaria, id=cuenta_origen_id, usuario=user)
        cuenta_destino = request.POST.get('cuenta_destino')
        banco_destino = request.POST.get('banco')
        monto = request.POST.get('monto')
        if cuenta_origen.saldo < int(monto):
            messages.add_message(request, 90, 'Saldo insuficiente!')
            return redirect('dashboard')
        cuenta_origen.saldo -= Decimal(monto)
        cuenta_origen.save()
        if (banco_destino == 'Banco UNAM'):
            transaccion = Transaccion(tipo_de_transaccion='Transferencia', monto=monto, cuenta=cuenta_origen, establecimiento='UNAM', descripcion='Transferencia a cuenta ' + cuenta_destino)
            transaccion.save()
            cuenta = user.cuentabancaria_set.get(numero_de_cuenta=cuenta_destino)
            cuenta.saldo += Decimal(monto)
            cuenta.save()
        else:
            transaccion = Transaccion(tipo_de_transaccion='Transferencia', monto=monto, cuenta=cuenta_origen, establecimiento=banco_destino, descripcion='Transferencia a cuenta ' + cuenta_destino)
            transaccion.save()
        messages.add_message(request, 70, 'Transaccion exitosa!')
        return redirect('dashboard')
    context = {
        'username': username,
        'cuentas_bancarias': cuentas_bancarias,
        'bancos': bancos
    }
    return render(request, 'transfers.html', context)

@login_required(login_url='login')
def movimientos(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    cuentas_bancarias = CuentaBancaria.objects.filter(usuario=user)
    transferencias = Transaccion.objects.order_by('-fecha')
    context = {
        'username': username,
        'cuentas_bancarias': cuentas_bancarias,
        'transferencias': transferencias
    }
    return render(request, 'movements.html', context)

@login_required(login_url='login')
def detalle_cuenta_bancaria(request, cuenta_id):
    cuenta_bancaria = get_object_or_404(CuentaBancaria, pk=cuenta_id)
    context = {
        'cuenta_bancaria': cuenta_bancaria,
        'fecha_de_apertura': cuenta_bancaria.fecha_de_apertura.strftime('%d de %B de %Y')
    }
    if request.method == 'POST':
        if cuenta_bancaria.saldo == 0:
            try:
                cuenta_bancaria.delete()
                messages.add_message(request, 70, 'Cuenta eliminada de manera exitosa!')
                return redirect('cuentas')
            except Exception as e:
                messages.add_message(request, 90, 'Ooops no se pudo eliminar la cuenta')
                return redirect('cuentas')
        else:
            messages.add_message(request, 80, 'No puedes eliminar una cuenta conn fondos $$$')
            return redirect('cuentas')
    return render(request, 'accountdetail.html', context)

@login_required(login_url='login')
def editarCuenta(request):
    user = request.user
    context = {
        'user': user
    }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        estado = request.POST.get('estado')
        codigo_postal = request.POST.get('codigo_postal')
        rfc = request.POST.get('rfc')
        telefono = request.POST.get('telefono')

        # Actualizar la contraseña solo si no está vacía
        if password:
            password = hashlib.sha1(password.encode()).hexdigest()
            user.set_password(password)

        # Actualizar los demás campos del usuario
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.fecha_nacimiento = fecha_nacimiento
        user.direccion = direccion
        user.ciudad = ciudad
        user.estado = estado
        user.codigo_postal = codigo_postal
        user.rfc = rfc
        user.telefono = telefono

        try:
            user.save()
            messages.add_message(request, 70, 'Datos actualizados correctamente')
            return redirect('dashboard')
        except Exception as e:
            print(e)
            messages.add_message(request, 90, 'Error al actualizar datos')
            return redirect('dashboard')
    return render(request, 'editaccount.html', context)

@login_required(login_url='login')
def prestamos(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    prestamos = user.prestamo_set.all()
    suma_prestamos = Prestamo.objects.filter(usuario=user).aggregate(Sum('monto_del_prestamo'))['monto_del_prestamo__sum']
    context = {
        'username': username,
        'prestamos': prestamos,
        'suma_prestamos': suma_prestamos
    }
    return render(request, 'loans.html', context)

@login_required(login_url='login')
def prestamos_nuevo(request):
    user = request.user
    username = user.first_name + " " + request.user.last_name
    cuentas_bancarias = user.cuentabancaria_set.all()
    context = {
        'username': username,
        'cuentas_bancarias': cuentas_bancarias
    }
    if request.method == 'POST':
        canntidad_prestamos = Prestamo.objects.filter(usuario=user).count()
        if canntidad_prestamos >= 3:
            messages.add_message(request, 80, 'Parece que ya tienes mas prestamos de los permitidos!')
            return redirect('dashboard')
        else:
            try:
                cantidad = Decimal(request.POST.get('cantidad'))
                prestamo = Prestamo(
                    monto_del_prestamo = cantidad,
                    tasa_de_interes = 0.55,
                    plazo_del_prestamo = int(request.POST.get('plazo')),
                    usuario = user
                )
                prestamo.calcular_fecha_de_vencimiento()
                prestamo.save()


                cuenta_id = request.POST.get('cuenta')
                cuenta = user.cuentabancaria_set.get(id=cuenta_id)
                transaccion_apertura = Transaccion.objects.create(
                    tipo_de_transaccion='Prestamo',
                    monto=cantidad,
                    cuenta=cuenta,
                    establecimiento='UNAM',
                    descripcion='Apertura de cuenta bancaria',
                    estado='Completada'
                )
                transaccion_apertura.save()

                cuenta.saldo += cantidad
                cuenta.save()
                messages.add_message(request, 70, 'Prestamo exitoso!')
                return redirect('dashboard')
            except Exception as e:
                print(e)
                messages.add_message(request, 90, 'Oooops, hubo un error!')
                return redirect('dashboard')
    return render(request, 'newloan.html', context)