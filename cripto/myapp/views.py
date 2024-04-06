
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login  # Importa la función login de Django
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserInfo,Guerrero,Compra,HistorialGold,Withdraw,life,Tower,RegistroCompra,Cofre,CompraCofre
from django.contrib.auth.decorators import login_required
import os
import random
from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404
from datetime import datetime


from django.utils import timezone

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Utiliza la función auth_login para evitar conflictos
            messages.success(request, 'Successful login.')
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión
        else:
            messages.error(request, 'Incorrect credentials. Please try again.')

    return render(request, 'login.html')

@login_required(login_url='/login/')
def home(request):
    if request.method == 'GET':
        # Obtener el usuario logueado
        user = request.user
        # Obtener el objeto UserInfo asociado al usuario logueado
        print("User:", user)  # Agrega este print para verificar el usuario
        user_info = get_object_or_404(UserInfo, user=user)
        
        print("UserInfo:", user_info)  # Agrega este print para verificar UserInfo

        # Obtener todos los objetos Guerrero de la base de datos
        guerreros = Guerrero.objects.all()
        tower_info=Tower.objects.all()
        # Crear una lista para almacenar cada Guerrero junto con su nombre de archivo
        guerreros_con_archivo = []
        cofres = Cofre.objects.all()

        # Iterar sobre cada Guerrero y obtener su nombre de archivo
        for guerrero in guerreros:
            nombre_archivo = os.path.basename(guerrero.imagen.url)
            # Agregar el Guerrero y su nombre de archivo a la lista
            guerreros_con_archivo.append((guerrero, nombre_archivo))
        
        # Pasar la lista de guerreros con sus nombres de archivo y el gold del usuario al contexto
        context = {'guerreros_con_archivo': guerreros_con_archivo, 'user_info': user_info, "tower":tower_info , "cofres":cofres}
        
        return render(request, 'home.html', context)

def seleccionar_guerrero_por_probabilidad(probabilidades):
    # Genera un número aleatorio entre 0 y 1
    random_number = random.random()
    acumulador = 0
    
    for rareza, probabilidad in probabilidades.items():
        acumulador += probabilidad
        if random_number < acumulador:
            return rareza
    
    # Si no se ha devuelto ninguna rareza, devuelve None
    return None

def abrircofre(request, id):
    if request.method == 'POST':
        cofre = CompraCofre.objects.get(id=id)

        
        # Probabilidades de cada rareza
        probabilidades = {
            'Common': 0.45,
            'Uncommon': 0.32,
            'Rare': 0.20,
            'Epic': 0.03
        }
        
        # Selecciona la rareza del Guerrero
        rareza_seleccionada = seleccionar_guerrero_por_probabilidad(probabilidades)
        
        if rareza_seleccionada:
            # Filtra los Guerreros por rareza y nombre
            guerreros_disponibles = Guerrero.objects.filter(tipo='skeleton warrior', rareza=rareza_seleccionada)
            
            if guerreros_disponibles.exists():
                # Realiza un sorteo aleatorio para seleccionar un Guerrero
                guerrero_seleccionado = random.choice(guerreros_disponibles)
                cofre.cofre_abierto = True
                cofre.save()  # Guardar el cambio en la base de datos
                # Crea una instancia de Compra
                compra = Compra.objects.create(
                    usuario=request.user,
                    guerrero=guerrero_seleccionado,
                    total=guerrero_seleccionado.precio,
                    cooldown_actual=guerrero_seleccionado.cooldown
                )
                
                # Agrega un mensaje de éxito con el guerrero adquirido
                messages.success(request, f"Congratulations, you've acquired a {guerrero_seleccionado.nombre}!  {guerrero_seleccionado.rareza}")
                messages.info(request, "Open Chest!")
                
                # Redirige a la página de inventario
                return redirect('/inventario/')
            else:
                # Manejar el caso en que no haya guerreros disponibles para la rareza seleccionada
                messages.error(request, "Sorry, there are no warriors available for this rarity at this time.")
        else:
            # Manejar el caso en que no se haya seleccionado ninguna rareza
            messages.error(request, "Sorry, a warrior could not be selected at this time.")

    # Manejar el caso en que la solicitud no sea POST
    messages.error(request, "The request could not be processed.")
    return redirect('/inventario/')



def user_logout(request):
    auth_logout(request)
    return redirect('/login/')
@login_required(login_url='/login/')
def compracofre(request, id):
    # Obtener el usuario logueado
    user = request.user

    # Obtener el objeto UserInfo asociado al usuario logueado
    user_info = UserInfo.objects.get(user=user)

    # Obtener el cofre con el ID proporcionado
    cofre = Cofre.objects.get(pk=id)

    # Verificar si el usuario tiene suficiente oro para comprar el cofre
    if user_info.gold >= cofre.precio:
        # El usuario tiene suficiente oro para comprar el cofre
        # Restar el precio del cofre del oro del usuario
        user_info.gold -= cofre.precio
        user_info.save()

        # Crear una instancia de CompraCofre
        compra_cofre = CompraCofre.objects.create(
            user=user,
            cofre=cofre,
            cofre_abierto=False,  # El cofre se marca como no abierto por defecto
            fecha_compra=timezone.now()  # Registra la fecha y hora actual de la compra
        )

        # Guardar la instancia en la base de datos
        compra_cofre.save()

        # Mensaje de éxito
        messages.success(request, f"Purchased the Chest{cofre.nombre} successfully!")
        return redirect('/home/')

    else:
        # El usuario no tiene suficiente oro para comprar el cofre
        messages.error(request, "You don't have enough gold to buy this chest.")

    # Redirigir de vuelta a la página de inicio
    return redirect('/home/')





def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password' )
        numero_wallet = request.POST.get('numero_wallet')
        
        # Verificar si el nombre de usuario ya está en uso
        if User.objects.filter(username=username).exists():
            messages.error(request, 'The username is already in use. Please choose another one.')
            return redirect('/register/')

        # Crear el usuario
        user = User.objects.create_user(username=username, email=email, password=password)

        # Verificar si el usuario se creó correctamente
        if user:
            # Crear el objeto UserInfo asociado al usuario
            user_info = UserInfo.objects.create(user=user, numero_wallet=numero_wallet)
            Life = life(user=user, value=50, last_updated=timezone.now())
            Life.save()
            print("se registro life : ")
            print (Life)
            # Verificar si el objeto UserInfo se creó correctamente
            if user_info:

                return redirect('/login/')  # Redireccionar a la página de inicio de sesión después del registro
            else:
                # Eliminar el usuario si el objeto UserInfo no se creó correctamente
                user.delete()
                messages.error(request, 'There was a problem creating your account. Please try again.')
        else:
            messages.error(request, 'There was a problem creating your account. Please try again.')

    return render(request, 'register.html')





from datetime import timedelta

@login_required(login_url='/login/')
def inventario(request):
    compras_usuario = Compra.objects.filter(usuario=request.user)
    user_info = UserInfo.objects.get(user=request.user)
    registro_compras = RegistroCompra.objects.filter(user=request.user)  # Agregar esta línea para obtener las compras de torres
    compra_cofre=CompraCofre.objects.filter(user=request.user)
    # Obtener la hora actual
    hora_actual = timezone.now()


    for compra_torre in registro_compras:
        if compra_torre.hora_habilitacion is None:
            compra_torre.hora_habilitacion = hora_actual - timedelta(days=1)
            compra_torre.save()
            continue
        if hora_actual >= compra_torre.hora_habilitacion:
            compra_torre.habilitado_farmear = True
            compra_torre.save()
        else:
            compra_torre.habilitado_farmear = False
            compra_torre.save()
    # Iterar sobre las compras para verificar y actualizar el estado de habilitado_farmear
    for compra in compras_usuario:
        if compra.hora_habilitacion is None:
            compra.hora_habilitacion = hora_actual - timedelta(days=1)
            compra.save()
            continue 
        if  hora_actual >= compra.hora_habilitacion:
            compra.habilitado_farmear = True
            compra.save()  # Guardar el cambio en la base de datos
        else:
            compra.habilitado_farmear = False
            compra.save()  # Guardar el cambio en la base de datos

    context = {'compras_usuario': compras_usuario, 'user_info': user_info,'registro_compras': registro_compras, 'compras_cofre':compra_cofre}
    return render(request, 'inventario.html', context)



#NO PUEDE COMPRAR MAS TORRES 


@login_required(login_url='/login/')
def compra(request, id):
    user = request.user
    hora_actual = timezone.now() - timedelta(days=1)
    # Verificar si el usuario ya ha comprado una torre de este tipo
    if RegistroCompra.objects.filter(user=user, tower__tipo=id).exists():
        messages.error(request, 'You can only buy one tower of this type')
        return redirect('/home/') 
    
    if not isinstance(id, int):
        tower = Tower.objects.get(tipo=id)
        if user.userinfo.gold < tower.price:
            messages.error(request, 'You dont have enough gold to buy this tower.')
            return redirect('/home/')  
        
    if id == 'A':
                # Verificar si el usuario tiene los guerreros necesarios para la torre tipo A
        common_warriors_count = Compra.objects.filter(usuario=user, guerrero__rareza='Common').count()
        uncommon_warriors_count = Compra.objects.filter(usuario=user, guerrero__rareza='Uncommon').count()
        
        if common_warriors_count >= 3 and uncommon_warriors_count >= 3:
            # Realizar la compra de la torre tipo A

            RegistroCompra.objects.create(user=user, tower=tower, hora_habilitacion=hora_actual)
            # Otra lógica específica para la torre A
            return redirect('/home/')
        else:
            # Mensaje de error si el usuario no tiene los guerreros necesarios
            messages.error(request, 'You dont have the warriors needed to buy this tower.')
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión

    
    elif id == 'B':
        # Verificar si el usuario tiene los guerreros necesarios para la torre tipo B
        rare_warriors_count = Compra.objects.filter(usuario=user, guerrero__rareza='Rare').count()
        
        if rare_warriors_count >= 3:
            # Realizar la compra de la torre tipo B
            RegistroCompra.objects.create(user=user, tower=tower, hora_habilitacion=hora_actual)
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión

        else:
            # Mensaje de error si el usuario no tiene los guerreros necesarios
            messages.error(request, 'You dont have the warriors needed to buy this tower.')
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión

    
    elif id == 'Villager':
        # Verificar si el usuario tiene los aldeanos necesarios para la torre tipo Village
        common_villager_count = Compra.objects.filter(usuario=user, guerrero__rareza='Common').count()
        uncommon_villager_count = Compra.objects.filter(usuario=user, guerrero__rareza='Uncommon').count()
        rare_villager_count = Compra.objects.filter(usuario=user, guerrero__rareza='Rare').count()
        
        if common_villager_count >= 10 and uncommon_villager_count >= 10 and rare_villager_count >= 10:
            # Realizar la compra de la torre tipo Village
            RegistroCompra.objects.create(user=user, tower=tower, hora_habilitacion=hora_actual)
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión
        else:
            # Mensaje de error si el usuario no tiene los aldeanos necesarios
            messages.error(request, 'You dont have the warriors needed to buy this tower.')
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión

        pass
    elif id == 'War':
        # Verificar si el usuario tiene los guerreros necesarios para la torre tipo War
        epic_warriors_count = Compra.objects.filter(usuario=user, guerrero__rareza='Epic').count()
        
        if epic_warriors_count >= 3:
            # Realizar la compra de la torre tipo War
            RegistroCompra.objects.create(user=user, tower=tower, hora_habilitacion=hora_actual)
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión
        else:
            # Mensaje de error si el usuario no tiene los guerreros necesarios
            messages.error(request, 'You dont have the warriors needed to buy this tower.')
            return redirect('/home/')  # Redirecciona a la página de inicio después del inicio de sesión

    else:
        user = request.user
        guerrero = Guerrero.objects.get(pk=id)
        if user.userinfo.gold < guerrero.precio:
            # Mensaje de error si el usuario no tiene suficiente oro
            messages.error(request, 'You dont have enough gold to buy this warrior.')
            return redirect('/home/') 
        else:
            # Obtener el guerrero por su ID
            
            # Calcular el total de la compra
            total = guerrero.precio
            # Crear una instancia de Compra
            compra = Compra(usuario=request.user, guerrero=guerrero, total=total)
            # Guardar la compra en la base de datos
            compra.save()
            user.userinfo.gold -= guerrero.precio
            user.userinfo.save()
            # Obtener todas las compras del usuario
            compras_usuario = Compra.objects.filter(usuario=request.user)
            # Pasar las compras al contexto
            
            user_info = UserInfo.objects.get(user=user)
                    # Obtener la URL del sonido del guerrero
            sonido_url = settings.MEDIA_URL + str(guerrero.sonido)
            context = {'compras_usuario': compras_usuario,'user_info': user_info,'sonido_url': sonido_url}
            # Redirigir a la página de inventario con las compras del usuario
            return redirect('inventario')


@login_required(login_url='/login/')
def farmearTower(request, id):
    if request.method == 'POST':
        user = request.user
        registro_compra = RegistroCompra.objects.get(pk=id)
        
        # Generar un número aleatorio dentro del rango de producción
        oro_ganado = random.randint(registro_compra.tower.produccion_min, registro_compra.tower.produccion_max)
        
        # Actualizar el oro del usuario
        user_info = UserInfo.objects.get(user=user)
        user_info.gold += oro_ganado
        user_info.gold_Total += oro_ganado
        user_info.created_at = timezone.now()

        user_info.save()
        
        # Actualizar el estado de habilitado_farmear y hora_habilitacion
        ahora = timezone.now()
        cooldown_horas = registro_compra.tower.cooldown
        hora_habilitacion = ahora + timezone.timedelta(hours=cooldown_horas)
        
        registro_compra.habilitado_farmear = False
        registro_compra.hora_habilitacion = hora_habilitacion
        registro_compra.save()
        
        HistorialGold.objects.create(user=user, tower=registro_compra.tower, oro_ganado=oro_ganado)

        messages.success(request, f'Farming done successfully. Generated {oro_ganado} golden.')
        return redirect('inventario')

    
    
    
@login_required(login_url='/login/')
def farmear(request, id):
    if request.method == 'POST':
        compra = Compra.objects.get(pk=id)
        guerrero = compra.guerrero
        user_info = UserInfo.objects.get(user=request.user)
        ahora = timezone.now()

        # Verificar si el usuario puede farmear
        if compra:
             # Actualizar el cooldown
            if compra.hora_habilitacion is None or compra.hora_habilitacion < ahora:
                print("id 1 :")
                print(id)
                compra.actualizar_cooldown_actual() 
                # Calcular el oro ganado
                oro_ganado = random.randint(guerrero.produccion_min, guerrero.produccion_max)
                
                # Actualizar el oro del usuario
                user_info.gold += oro_ganado
                user_info.gold_Total += oro_ganado
                user_info.created_at = timezone.now()


                user_info.save()

                # Registrar en el historial de acciones
                HistorialGold.objects.create(user=request.user, guerrero=guerrero, oro_ganado=oro_ganado)

                # Deshabilitar el farmeo hasta que pase el cooldown
                compra.habilitado_farmear = False
                compra.save()

                # Mensaje de éxito
                messages.success(request, f'Farming done successfully. Generated {oro_ganado} golden.')
            else:
                # Mensaje de error si el farmeo no está habilitado
                messages.error(request, 'You cant farm yet. Wait for the cooldown to pass.')
        else:
            # Mensaje de error si no se encuentra la compra del guerrero
            messages.error(request, 'You dont have this warrior in your inventory.')

        # Redirigir a la página de inventario
        return redirect('inventario')

@login_required(login_url='/login/')
def ranking(request):
    # Obtener todos los objetos UserInfo ordenados por gold_Total de mayor a menor
    users_info = UserInfo.objects.order_by('-gold_Total', '-created_at')
    user_info1 = UserInfo.objects.get(user=request.user)
    # Pasar los objetos UserInfo a la plantilla ranking.html
    return render(request, 'ranking.html', {'users_info': users_info , 'user_info1': user_info1})
    
@login_required(login_url='/login/')
def perfil(request):
    user_info = UserInfo.objects.get(user=request.user)
    withdraw_history = Withdraw.objects.filter(user=request.user)
    # Obtener el objeto Life si existe, o crearlo si no existe
    # Llamar al método update_life para actualizar el valor de la vida
    lifes = life.objects.get(user=request.user)
    
    lifes.update_life()
    print("valor:")
    print(lifes.value)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            amount = int(amount)
            if amount <= 0:
                messages.error(request, 'Please enter a valid positive amount.')
                return redirect('/perfil/')
            if user_info.gold >= amount:
                # Crea una nueva solicitud de retiro
                withdraw = Withdraw.objects.create(user=request.user, amount=amount, life=lifes.value)
                # Actualiza el oro del usuario restando la cantidad retirada
                user_info.gold -= amount
                user_info.save()
                lifes.value=50
                lifes.save()
                # Filtrar los registros de RegistroCompra asociados al usuario actual
                registro_compras_usuario = RegistroCompra.objects.filter(user=request.user)

                # Verificar si la solicitud de retiro involucra la torre A
                for compra in registro_compras_usuario:
                    if compra.tower.tipo == 'A':
                        withdraw.tower_A = True
                        break
                    
                    
                # Verificar si la solicitud de retiro involucra la torre B
                for compra in registro_compras_usuario:
                    if compra.tower.tipo == 'B':
                        withdraw.tower_B = True
                        break
                
                print("hola")
                print(withdraw.tower_A)
                withdraw.save()
                messages.success(request, 'Withdrawal request sent successfully.')
            else:
                messages.error(request, 'Insufficient balance to make the withdrawal.')
            return redirect('/perfil/')

    context = {'user_info': user_info, 'withdraw_history': withdraw_history , 'life': lifes}
    return render(request, 'perfil.html', context)
