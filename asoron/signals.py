from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_delete
import boto3
from .models import Telefono,PersonaContacto,Imagen,ClienteNatural,ClienteJuridico,Proveedor,AfiliadoCodigo,CarritoItem,Tienda


@receiver(pre_save, sender=Telefono)
def _pre_save_receiver(sender, **kwargs):   
    complete=0
        
    for field_name in [ 'fk_telf_clie_natu', 'fk_telf_clie_juri', 'fk_telf_prov', 'fk_telf_empl','fk_telf_pers_cont']:
        if getattr(kwargs['instance'], field_name):
                complete+=1
                
    if complete!=1:
        raise ValidationError("Debe seleccionar un solo cliente o provedor para el telefono")
    
@receiver(pre_save, sender=PersonaContacto)
def _pre_save_receiver_persona_contacto(sender, **kwargs): 
    complete=0
    
    for field_name in ['fk_pers_cont_prov','fk_pers_cont_clie_juri']:
        if getattr(kwargs['instance'], field_name):
                complete+=1
    if complete!=1:
        raise ValidationError("Debe seleccionar un solo cliente o provedor para la persona de contacto")

@receiver(post_delete, sender=Imagen)
def delete_image_file(sender, instance, **kwargs):                          
    instance.img_url.delete(False)

@receiver(pre_save, sender=AfiliadoCodigo)
def check_unique_entity(sender, **kwargs):
    complete=0
    
    for field_name in ['fk_afil_prov','fk_afil_clie_juri','fk_afil_clie_natu']:
        if getattr(kwargs['instance'], field_name):
                complete+=1
    if complete!=1:
        raise ValidationError("Debe seleccionar un solo cliente o provedor para el afiliado")


@receiver(pre_save, sender=CarritoItem)    
def validar_combinacion_productos(sender, instance, **kwargs):
    tipos_de_producto = [
        instance.fk_carri_item_ofer_ron,
        instance.fk_carri_item_inve_tiend,
        instance.fk_carri_item_entr_evento,
        instance.fk_carri_item_afil,
    ]

    tipos_seleccionados = [tipo for tipo in tipos_de_producto if tipo is not None]

    if len(tipos_seleccionados) > 1:
        if len(tipos_seleccionados) ==2 and (instance.fk_carri_item_ofer_ron is not None and instance.fk_carri_item_inve_tiend is not None):
            oferta=instance.fk_carri_item_ofer_ron.fk_ofer_bote_bote.bote_id
            if instance.fk_carri_item_inve_tiend:
                botella=instance.fk_carri_item_inve_tiend.fk_inve_tiend_bote.bote_id
                if botella!=oferta:
                    raise ValidationError("La oferta no corresponde al producto seleccionado")
            else:
                raise ValidationError("La oferta debe ir acompañada de una botella")
        else:
            raise ValidationError("No puede seleccionar más de un tipo de producto")

@receiver(pre_save, sender=Tienda)
def check_existing_online_tienda(sender, instance, **kwargs):
    if instance.fk_tiend_tipo_tiend.tipo_tiend_nombre.lower() == 'online':
        existing_online_tienda = Tienda.objects.filter(fk_tiend_tipo_tiend__tipo_tiend_nombre__iexact='Online').exclude(tiend_id=instance.tiend_id)
        if existing_online_tienda.exists():
            raise ValidationError('Ya existe una tienda en línea. Solo puede haber una tienda en línea en el sistema.')

@receiver(pre_save, sender=CarritoItem)
def check_inventario(sender, instance, **kwargs):
    if instance.fk_carri_item_inve_tiend:
        if instance.fk_carri_item_inve_tiend.inve_tiend_cantidad < instance.carri_item_cantidad:
            raise ValidationError('No hay suficiente inventario para el producto seleccionado')
    elif instance.fk_carri_item_entr_evento:
        if instance.fk_carri_item_entr_evento.entr_evnt_cantidad < instance.carri_item_cantidad:
            raise ValidationError('No hay suficiente inventario para el producto seleccionado')