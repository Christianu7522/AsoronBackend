from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


@receiver(pre_save, sender='core.Usuario')
def _pre_save_receiver(sender, **kwargs):   
    complete=0
        
    for field_name in ['fk_usua_clie_natu','fk_usua_clie_juri','fk_usua_empl']:
        if getattr(kwargs['instance'], field_name):
                complete+=1
                
    if complete!=1:
        raise ValidationError("Debe seleccionar un tipo de usuario")
    