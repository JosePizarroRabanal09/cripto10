from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class Tower(models.Model):
    name = models.CharField(max_length=100)
    observacion = models.CharField(max_length=300)
    efecto =models.CharField(max_length=300)
    tipo = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)
    produccion_min = models.IntegerField(default=0)
    produccion_max = models.IntegerField(default=0)
    cooldown = models.IntegerField(default=0)  # Cambiado a IntegerField
    imagen = models.ImageField(upload_to='tower_images/', null=True, blank=True)  # Campo de imagen para la torre


class RegistroCompra(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    habilitado_farmear = models.BooleanField(default=True)  # Nuevo campo para indicar si el farmeo está habilitado
    hora_habilitacion  = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"Compra de {self.tower.name} por {self.user.username} el {self.fecha_compra}"
    
    
class life(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=50)
    last_updated = models.DateTimeField()

    def update_life(self):
        # Verificar si ha pasado al menos un día desde la última actualización
        if timezone.now() - self.last_updated >= timedelta(days=1):
            # Restar 1 al valor de la vida
            self.value -= 1
            # Actualizar la fecha de la última actualización
            self.last_updated = timezone.now()
            # Guardar los cambios en la base de datos
            self.save()
        
        
        
        
class Guerrero(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    COMMON = 'Common'
    UNCOMMON = 'Uncommon'
    RARE = 'Rare'
    EPIC = 'Epic'
    LEGENDARY = 'Legendary'

    RAREZA_CHOICES = [
        (COMMON, 'Common'),
        (UNCOMMON, 'Uncommon'),
        (RARE, 'Rare'),
        (EPIC, 'Epic'),
        (LEGENDARY, 'Legendary'),
    ]
    rareza = models.CharField(max_length=20, choices=RAREZA_CHOICES)
    produccion_min = models.IntegerField(default=0)
    produccion_max = models.IntegerField(default=0)
    precio = models.IntegerField(default=0)  # Campo de precio como entero con valor predeterminado
    cooldown = models.IntegerField(default=0)  # Cambiado a IntegerField
    imagen = models.ImageField()
    sonido = models.FileField()  # Sin especificar upload_to
    mostrar = models.BooleanField(default=True)  # Atributo booleano para indicar si se debe mostrar o no

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numero_wallet = models.CharField(max_length=100)
    gold = models.IntegerField(default=0)
    gold_Total = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)


class Cofre(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField()
    sonido = models.FileField()
    precio = models.IntegerField(default=0)  # Campo de precio como entero con valor predeterminado


    def __str__(self):
        return self.nombre

class CompraCofre(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cofre = models.ForeignKey(Cofre, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    cofre_abierto = models.BooleanField(default=False)

    def __str__(self):
        return f"Compra de {self.cofre.nombre} por {self.user.username} el {self.fecha_compra}"
class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    guerrero = models.ForeignKey(Guerrero, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cooldown_actual = models.IntegerField(default=0)  # Nuevo campo para el cooldown actual
    habilitado_farmear = models.BooleanField(default=True)  # Nuevo campo para indicar si el farmeo está habilitado
    hora_habilitacion = models.DateTimeField(null=True, blank=True)  # Nuevo campo para almacenar la hora de habilitación

    def __str__(self):
        return f'Compra de {self.guerrero.nombre} por {self.usuario.username} el {self.fecha_compra}'
    def actualizar_cooldown_actual(self):
        ahora = timezone.now()
        cooldown_horas = self.guerrero.cooldown  # Suponiendo que el cooldown está en horas
        self.hora_habilitacion = ahora + timezone.timedelta(hours=cooldown_horas)
        self.habilitado_farmear = False
        self.save()

class HistorialGold(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guerrero = models.ForeignKey(Guerrero, on_delete=models.CASCADE, null=True,blank=True)  # Permitir que el campo guerrero sea nulo
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE, null=True, blank=True)  # Permitir valores nulos
    oro_ganado = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    
    
class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_retiro = models.DateTimeField(default=timezone.now)  # Establece el valor predeterminado a la fecha y hora actuales
    tower_A = models.BooleanField(default=False)
    tower_B = models.BooleanField(default=False)
    life = models.IntegerField(default=0)  # Nuevo atributo para almacenar información sobre life

    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Refused'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f'Withdraw for {self.user.username} - Amount: {self.amount} - Status: {self.get_status_display()}'