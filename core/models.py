from django.apps import AppConfig
from django.db import models
from django.contrib.auth.models import AbstractUser
from asoron.models import ClienteJuridico, ClienteNatural, Empleado

class Usuario(AbstractUser):
    email=models.EmailField(unique=True)
    username=models.CharField(max_length=50,unique=True)
    fk_usua_clie_natu=models.ForeignKey(ClienteNatural,on_delete=models.CASCADE,null=True,blank=True)
    fk_usua_clie_juri=models.ForeignKey(ClienteJuridico,on_delete=models.CASCADE,null=True,blank=True)
    fk_usua_empl=models.ForeignKey(Empleado,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        verbose_name_plural='Usuario'
  


  
