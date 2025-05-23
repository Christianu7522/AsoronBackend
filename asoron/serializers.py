from rest_framework import serializers
from django.db.models import F
from .models import *
from rest_framework.response import Response
from django.utils import timezone
import pytz
from datetime import date, datetime, timedelta

  
class MetodoFermentacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoFermentacion
        fields = ['meto_ferm_nombre']

class MetodoDestilacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoDestilacion
        fields = ['meto_dest_nombre']
        
        
        
class BarrilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barril
        fields = ['barr_calidad','barr_tipo','barr_tamano','barr_tipo_madera']
        
class BarrilAnejamientoSerializer(serializers.ModelSerializer):
    fk_barr_anej_barr=BarrilSerializer()
    class Meta:
        model = BarrilAnejamiento
        fields = ['barr_anej_anos_barril','fk_barr_anej_barr']
        
    def to_representation(self, instance):
        instance=BarrilAnejamiento.objects.select_related('fk_barr_anej_barr').get(pk=instance.pk)
        return super().to_representation(instance)
        
class AnejamientoSerializer(serializers.ModelSerializer):
    fk_anej_meto_ferm=MetodoFermentacionSerializer()
    fk_anej_meto_dest=MetodoDestilacionSerializer()
    barr_anej_anej = BarrilAnejamientoSerializer(many=True)
    class Meta:
        model = Anejamiento
        fields = ['anej_cantidad_anos','anej_calidad_agua','fk_anej_meto_ferm','fk_anej_meto_dest','barr_anej_anej']
    
    def to_representation(self, instance):
        instance=Anejamiento.objects.prefetch_related('barr_anej_anej').get(pk=instance.pk)
        return super().to_representation(instance)
        
        
class TipoRonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRon
        fields = ['tipo_ron_nombre']
        
class ClasificacionRonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasificacionRon
        fields = ['clasi_ron_nombre']       
        
          
class ClasificacionTipoSerializer(serializers.ModelSerializer):
    fk_clasi_tipo_clasi_ron=ClasificacionRonSerializer()
    fk_clasi_tipo_tipo_ron=TipoRonSerializer()
    
    class Meta:
        model = ClasificacionTipo
        fields = ['fk_clasi_tipo_clasi_ron','fk_clasi_tipo_tipo_ron']
        
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['color_nombre','color_descripcion']

class GradoAlcoholSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradoAlcohol
        fields = ['grad_alco_porcentaje_alcohol']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['prov_razon_social','prov_denominacion_comercial','prov_pagina_web','prov_rif']

class LugarSerializer(serializers.ModelSerializer):
    municipio = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    parroquia=serializers.SerializerMethodField()
    
    class Meta:
        model = Lugar
        fields = ['estado', 'municipio', 'parroquia']

    def get_municipio(self, obj):
        if obj.fk_lugar_lugar:
            return obj.fk_lugar_lugar.lugar_nombre
        return None

    def get_estado(self, obj):
        if obj.fk_lugar_lugar and obj.fk_lugar_lugar.fk_lugar_lugar:
            return obj.fk_lugar_lugar.fk_lugar_lugar.lugar_nombre
        return None

    def get_parroquia(self, obj):
        return obj.lugar_nombre
    
    
class CajaSerializer(serializers.ModelSerializer):
    paleta=serializers.SerializerMethodField()
    cantidad_paleta=serializers.SerializerMethodField()
    bulto=serializers.SerializerMethodField()
    cantidad_bulto=serializers.SerializerMethodField()
    caja=serializers.SerializerMethodField()
    cantidad_caja=serializers.SerializerMethodField()
    
    class Meta:
        model = Caja
        fields = ['paleta','cantidad_paleta','bulto','cantidad_bulto','caja','cantidad_caja']
        
    def get_paleta(self,obj):
        if obj.fk_caja_caja:
            return obj.fk_caja_caja.fk_caja_caja.caja_nombre 
        return None
    
    def get_bulto(self, obj):
        if obj.fk_caja_caja:
            return obj.fk_caja_caja.caja_nombre 
        return None
    
    def get_caja(self, obj):
        return obj.caja_nombre 
    
    def get_cantidad_paleta(self, obj):
        if obj.fk_caja_caja:
            return obj.fk_caja_caja.fk_caja_caja.caja_cantidad 
        return None
    
    def get_cantidad_bulto(self, obj):
        if obj.fk_caja_caja:
            return obj.fk_caja_caja.caja_cantidad 
        return None
    
    def get_cantidad_caja(self, obj):
        return obj.caja_cantidad
    
    
    
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['mate_nombre']
        

class TapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tapa
        fields = ['tapa_nombre']
        
        
class TapaMateSerializer(serializers.ModelSerializer):
    fk_tapa_mate_mate=MaterialSerializer()
    fk_tapa_mate_tapa=TapaSerializer()
    class Meta:
        model = TapaMaterial
        fields = ['fk_tapa_mate_tapa','fk_tapa_mate_mate']
        
    def to_representation(self, instance):
        instance = TapaMaterial.objects.select_related('fk_tapa_mate_tapa', 'fk_tapa_mate_mate').get(pk=instance.pk)
        return super().to_representation(instance)
    
    
class TipoBotellaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoBotella
        fields = ['tipo_bote_altura','tipo_bote_ancho','tipo_bote_capacidad'] 
    
    
class MaterialTipoBotellaSerializer(serializers.ModelSerializer):
    fk_mate_tipo_bote_tipo_bote=TipoBotellaSerializer()
    fk_mate_tipo_bote_mate=MaterialSerializer()
    class Meta:
        model = MaterialTipoBotella
        fields = ['fk_mate_tipo_bote_mate','fk_mate_tipo_bote_tipo_bote']    
    
    def to_representation(self, instance):
        istance=MaterialTipoBotella.objects.select_related('fk_mate_tipo_bote_tipo_bote','fk_mate_tipo_bote_mate').get(pk=instance.pk)
        return super().to_representation(istance)
    


class NotaCataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaCata
        fields = ['nota_cata_nombre','nota_cata_descripcion']

        
class EventoSerializer(serializers.ModelSerializer):
    fk_event_lugar=LugarSerializer()
    class Meta:
        model = Evento
        fields = ['event_nombre','event_descripcion','event_fecha_ini','event_fecha_fin','event_direccion','fk_event_lugar']
    
    def to_representation(self, instance):
        instance=Evento.objects.select_related('fk_event_lugar').get(pk=instance.pk)
        return super().to_representation(instance)
    
    

class PremioSerializer(serializers.ModelSerializer):
    fk_prem_lugar=LugarSerializer()
    
    class Meta:
        model = Premio
        fields = ['prem_nombre','prem_descripcion','prem_direccion','fk_prem_lugar']
    
    def to_representation(self, instance):
        instance=Premio.objects.select_related('fk_prem_lugar').get(pk=instance.pk)
        return super().to_representation(instance)
        
class CataEventoPremioRonSerializer(serializers.ModelSerializer):
    fk_cata_even_premio_ron_evento=EventoSerializer()
    fk_cata_even_premio_ron_premio=PremioSerializer()
    notaCata=serializers.SerializerMethodField(method_name='get_notaCata')
    
    class Meta:
        model = CataEventoPremioRon
        fields = ['cata_even_premio_ron_fecha_premiacion','fk_cata_even_premio_ron_evento','fk_cata_even_premio_ron_premio','notaCata']
    
    def to_representation(self, instance):
        istance=CataEventoPremioRon.objects.select_related('fk_cata_even_premio_ron_evento','fk_cata_even_premio_ron_premio','nota_cata_cata_even_premio_ron').get(pk=instance.pk)
        return super().to_representation(istance)
    
    def get_notaCata(self, obj):
        nota_cata=NotaCata.objects.filter(fk_nota_cata_cata_even_premio_ron=obj.cata_even_premio_ron_id)
        serializer=NotaCataSerializer(nota_cata,many=True)
        return serializer.data
    
        
class RonDetailSerializer(serializers.ModelSerializer):
    fk_ron_clasi_tipo = ClasificacionTipoSerializer()
    fk_ron_anej = AnejamientoSerializer()
    fk_ron_color = ColorSerializer()
    fk_ron_grado_alco = GradoAlcoholSerializer()
    fk_ron_prove = ProveedorSerializer()
    fk_ron_lugar = LugarSerializer()
    comoservir=serializers.SerializerMethodField(method_name='get_comoservir')
    sensancion=serializers.SerializerMethodField(method_name='get_sensancion')
    mateprima=serializers.SerializerMethodField(method_name='get_mateprima')
    premios=serializers.SerializerMethodField(method_name='get_premios')
    
    class Meta:
        model = Ron
        fields = ['ron_id','ron_nombre','ron_descripcion','fk_ron_clasi_tipo','fk_ron_anej','fk_ron_color','fk_ron_grado_alco','fk_ron_prove','fk_ron_lugar','comoservir','sensancion','mateprima','premios']
        
    def get_premios(self, obj):
        premios = CataEventoPremioRon.objects.filter(fk_cata_even_premio_ron_ron=obj.ron_id)
        serializer = CataEventoPremioRonSerializer(premios, many=True)
        return serializer.data
    
    def get_comoservir(self, obj):
        como_servir = ComoServirRon.objects.filter(fk_como_serv_ron_ron=obj.ron_id) \
            .annotate(
                coctel=F('fk_como_serv_ron_como_serv__como_serv_nombre'),
                como_preparar=F('como_serv_ron_descripcion')
            ) \
            .values('coctel', 'como_preparar')
        return list(como_servir)
    
    
    def get_sensancion(self, obj):
        sensacion=SensacionRon.objects.filter(fk_sens_ron_ron=obj.ron_id) \
            .annotate(
                sensacion=F('fk_sens_ron_sens__sens_nombre'),
            ) \
                .values('sensacion')
        return list(sensacion)
    
    
    def get_mateprima(self, obj):
        mateprima=MateriaPrimaRon.objects.filter(fk_mate_prima_ron_ron=obj.ron_id) \
            .annotate(
                mateprima=F('fk_mate_prima_ron_mate_prima__mate_prima_nombre'),
            ) \
                .values('mateprima')
        return list(mateprima)
    
    
    def to_representation(self, instance):
        instance = Ron.objects.select_related(
            'fk_ron_clasi_tipo__fk_clasi_tipo_clasi_ron',
            'fk_ron_clasi_tipo__fk_clasi_tipo_tipo_ron',
            'fk_ron_anej__fk_anej_meto_ferm',
            'fk_ron_anej__fk_anej_meto_dest',
            'fk_ron_color',
            'fk_ron_grado_alco',
            'fk_ron_prove',
            'fk_ron_lugar'
        ).get(pk=instance.pk)
        
        return super().to_representation(instance)


class RonCatalogoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ron
        fields = ['ron_id','ron_nombre']

class RonSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ron
        fields='__all__'







class BoteImagenSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        bote_id=self.context['bote_id']
        return Imagen.objects.create(fk_img_bote_id=bote_id, **validated_data)
    
    class Meta:
        model = Imagen
        fields = ['img_id','img_url']
     
     
     
     
     
class TipoTiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model=TipoTienda
        fields=['tipo_tiend_nombre']
        
class TiendaSerializer(serializers.ModelSerializer):
    fk_tiend_tipo_tiend=TipoTiendaSerializer()
    class Meta:
        model=Tienda
        fields=['tiend_nombre','fk_tiend_tipo_tiend']            
     
    
     
     
     
     
     
     
     
     
class InventarioTiendaBotellaDettailSerializer(serializers.ModelSerializer):
    precio=serializers.SerializerMethodField(method_name='get_precio')
    class Meta:
        model=InventarioTienda
        fields=['inve_tiend_cantidad','precio','inve_tiend_id']
        
    def to_representation(self, instance):
        instance=InventarioTienda.objects.select_related('fk_inve_tiend_tiend').get(pk=instance.pk)
        return super().to_representation(instance)
    
    def get_precio(self, instance):
        precio = HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=instance.inve_tiend_id).select_related('fk_hist_ron_inve_tiend').latest('hist_ron_fecha_fin')
        serializer = HistoricoRonSerializer(precio)
        return serializer.data




class BotellaDetailSerializer(serializers.ModelSerializer):
    fk_bote_caja=CajaSerializer()
    fk_bote_tapa_mate=TapaMateSerializer()
    fk_bote_mate_tipo_bote=MaterialTipoBotellaSerializer()
    fk_bote_ron=RonDetailSerializer()
    imagen=serializers.SerializerMethodField(method_name='get_images')
    inventariotienda=serializers.SerializerMethodField(method_name='get_inventario')
    class Meta:
        model = Botella
        fields = ['bote_id','bote_nombre','bote_descripcion','fk_bote_caja','fk_bote_tapa_mate','fk_bote_mate_tipo_bote','fk_bote_ron','imagen','inventariotienda']

    def get_images(self, obj):
        request = self.context.get('request')
        images = BoteImagenSerializer(obj.bote_images.all(), many=True, context={'request': request}).data
        return images
    
    def get_inventario(self,obj):
        usuario=self.context.get('user')
        
        if usuario.is_authenticated:
            
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
                inventario_botella=InventarioTienda.objects.filter(fk_inve_tiend_bote=obj.bote_id,fk_inve_tiend_tiend__fk_tiend_tipo_tiend__tipo_tiend_nombre='Online').select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend')
                return InventarioTiendaBotellaDettailSerializer(inventario_botella,many=True,context={'request':self.context.get('request')}).data
            
            else:
                if usuario.fk_usua_empl.empl_tiend_empl.filter(empl_tiend_fecha_fin__isnull=True).exists():
                    tienda_empleado = usuario.fk_usua_empl.empl_tiend_empl.filter(empl_tiend_fecha_fin__isnull=True).first()
                    tienda=tienda_empleado.fk_empl_tiend_tiend.tiend_id
                    inventario_botella=InventarioTienda.objects.filter(fk_inve_tiend_bote=obj.bote_id,fk_inve_tiend_tiend=tienda).select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend')
                    return InventarioTiendaBotellaDettailSerializer(inventario_botella,many=True,context={'request':self.context.get('request')}).data
                    
                else:
                    inventario_botella=InventarioTienda.objects.filter(fk_inve_tiend_bote=obj.bote_id,fk_inve_tiend_tiend__fk_tiend_tipo_tiend__tipo_tiend_nombre='Online').select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend')
                    return InventarioTiendaBotellaDettailSerializer(inventario_botella,many=True,context={'request':self.context.get('request')}).data
      
                    
        else:
            inventario_botella=InventarioTienda.objects.filter(fk_inve_tiend_bote=obj.bote_id,fk_inve_tiend_tiend__fk_tiend_tipo_tiend__tipo_tiend_nombre='Online').select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend')
            return InventarioTiendaBotellaDettailSerializer(inventario_botella,many=True,context={'request':self.context.get('request')}).data
      
    
   
    
    
class EventoImagenSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        event_id=self.context['event_id']
        return Imagen.objects.create(fk_img_event_id=event_id, **validated_data)
    class Meta:
        model = Imagen
        fields = ['img_id','img_url']
      

class EventoGetSerializer(serializers.ModelSerializer):
    fk_event_lugar=LugarSerializer()
    imagenes=serializers.SerializerMethodField(method_name='get_images')
    
    class Meta:
        model=Evento
        fields=['event_id','event_nombre','event_descripcion','event_fecha_ini','event_fecha_fin','event_direccion','fk_event_lugar','imagenes']
    
    def get_images(self, obj):
        request = self.context.get('request')
        images = EventoImagenSerializer(obj.event_images.all(), many=True, context={'request': request}).data
        return images
        
    
    
class EventotiendaSerializer(serializers.ModelSerializer):
    inventario=serializers.SerializerMethodField(method_name='get_inventario')
    class Meta:
        model=Tienda
        fields=['tiend_nombre','inventario']    
    
    def get_inventario(self,obj):
        inventario_botella=InventarioTienda.objects.filter(fk_inve_tiend_tiend=obj.tiend_id).select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend')
        return InventarioTiendaSerializer(inventario_botella,many=True,context={'request':self.context.get('request')}).data
    
class EntradaEventoSerializer(serializers.ModelSerializer):
    entr_envt_fecha_inicio=serializers.DateTimeField(format="%d/%m/%Y %H:%M")
    entr_envt_fecha_fin=serializers.DateTimeField(format="%d/%m/%Y %H:%M")
    class Meta:
        model=EntradaEvento
        fields=['entr_envt_id','entr_envt_nombre','entr_envt_descripcion','entr_envt_fecha_inicio','entr_envt_fecha_fin','entr_evnt_cantidad','entr_envt_precio']


class EventoDetailGetSerializer(serializers.ModelSerializer):
    fk_event_lugar=LugarSerializer()
    images=serializers.SerializerMethodField(method_name='get_images')
    fk_event_tien=EventotiendaSerializer()
    entradas=serializers.SerializerMethodField(method_name='get_entradas')
    class Meta:
        model=Evento
        fields=['event_id','event_nombre','event_descripcion','event_fecha_ini','event_fecha_fin','event_direccion','fk_event_lugar','images','fk_event_tien','entradas']

    def to_representation(self, instance):
        instance=Evento.objects.select_related('fk_event_lugar','fk_event_tien').get(pk=instance.pk)
        return super().to_representation(instance)
    
    
    def get_images(self, obj):
        request = self.context.get('request')
        images = EventoImagenSerializer(obj.event_images.all(), many=True, context={'request': request}).data
        return images
    
    
    def get_entradas(self, obj):
        caracas_timezone = pytz.timezone('America/Caracas')
        now_caracas=timezone.now().astimezone(caracas_timezone)
        

        if obj.event_fecha_fin >= now_caracas.date():
            
            entradas=EntradaEvento.objects.filter(fk_entr_envt_evento=obj.event_id)
            serializer=EntradaEventoSerializer(entradas,many=True)
            return serializer.data
        
        else: 
            return None
    
    
    
    
class EventoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Evento
        fields='__all__'

        
        
        
        
        
    
        
        
class BotellaInventarioSerializer(serializers.ModelSerializer):
    imagen=serializers.SerializerMethodField(method_name='get_images')
    class Meta:
        model=Botella
        fields=['bote_id','bote_nombre','bote_descripcion','imagen']
        
    
    def get_images(self, obj):
        request = self.context.get('request')
        images = BoteImagenSerializer(obj.bote_images.all(), many=True, context={'request': request}).data
        return images
    
    









class HistoricoRonSerializer(serializers.ModelSerializer):
    class Meta:
        model=HistoricoRon
        fields=['hist_ron_precio']
        

class InventarioTiendaSerializer(serializers.ModelSerializer):
    fk_inve_tiend_bote = BotellaInventarioSerializer()
    precio=serializers.SerializerMethodField(method_name='get_precio')
    class Meta:
        model=InventarioTienda
        fields=['inve_tiend_cantidad','fk_inve_tiend_bote','precio','inve_tiend_id']
        
    def to_representation(self, instance):
        instance=InventarioTienda.objects.select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend').get(pk=instance.pk)
        return super().to_representation(instance)
    
    def get_precio(self, instance):
        precio = HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=instance.inve_tiend_id,hist_ron_fecha_fin__isnull=True).select_related('fk_hist_ron_inve_tiend').first()
        serializer = HistoricoRonSerializer(precio)
        return serializer.data


        

class OfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Oferta
        fields=['ofer_id','ofer_nombre','ofer_descripcion','ofer_fecha_inicio','ofer_fecha_fin']
    
class OfertaBotellaSerializer(serializers.ModelSerializer):
    fk_ofer_bote_bote=BotellaInventarioSerializer()
    fk_ofer_bote_ofer=OfertaSerializer()
           
    class Meta:
        model=OfertaBotella
        fields=['fk_ofer_bote_bote','fk_ofer_bote_ofer','ofer_bote_porcentaje']
        
        
        
        
        
        
#serializador para obtener el codigo de telefono SOLO VISTA
class CodigoTelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model=TelefonoCodigo
        fields=['telf_cod_codigo']       
        
        
        
        
        
        
        
#serializadores para el empleado SOLO VISTA     
class TelefonoEmpleadoSerializer(serializers.ModelSerializer):
    fk_telf_telf_codi=CodigoTelefonoSerializer()
    
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_empl','fk_telf_telf_codi']
              

class EmpleadoTiendaSerializer(serializers.ModelSerializer):
    fk_empl_tiend_tiend=TiendaSerializer()
    class Meta:
        model=EmpleadoTienda
        fields=['fk_empl_tiend_tiend']

class EmpleadoSerializer(serializers.ModelSerializer):
    tienda=serializers.SerializerMethodField(method_name='get_tienda')
    telefono=serializers.SerializerMethodField(method_name='get_telefono')
    
    class Meta:
        model=Empleado
        fields=['empl_id','empl_nombre','empl_nombre_segundo','empl_apellido','empl_apellido_segundo','empl_cedula_identidad','tienda','telefono']
    
    def get_tienda(self, obj):
        tienda=EmpleadoTienda.objects.filter(fk_empl_tiend_empl=obj.empl_id,empl_tiend_fecha_fin__isnull=True).select_related('fk_empl_tiend_tiend')
        serializer=EmpleadoTiendaSerializer(tienda,many=True)
        return serializer.data

    def get_telefono(self, obj):
        telefono=Telefono.objects.filter(fk_telf_empl=obj.empl_id).select_related('fk_telf_telf_codi')
        serializer=TelefonoEmpleadoSerializer(telefono,many=True)
        return serializer.data
    
    
    
    



#serializadores para el cliente natural
class TelefonoGeneralClienteNatuSerializer(serializers.ModelSerializer):
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_telf_codi','telf_id','fk_telf_clie_natu']
        
class TelefonoPostClienteNatuSerializer(serializers.ModelSerializer):
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_telf_codi','telf_id']
        
    def create(self, validated_data):
        cliente_id=self.context['telf_clie_natu_id']
        return Telefono.objects.create(fk_telf_clie_natu_id=cliente_id, **validated_data)
    
class TelefonoClienteNatuSerializer(serializers.ModelSerializer):
    fk_telf_telf_codi=CodigoTelefonoSerializer()
    
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_clie_natu','fk_telf_telf_codi']   
        
    
class ClienteNaturalSerializer(serializers.ModelSerializer):
    fk_clie_natu_lugar=LugarSerializer()
    telefono=serializers.SerializerMethodField(method_name='get_telefono')
    class Meta:
        model=ClienteNatural
        fields=['clie_natu_id','clie_natu_rif','clie_natu_cedula_identidad','clie_natu_nombre','clie_natu_apellido','clie_natu_segundo_nombre','clie_natu_segundo_apellido','clie_natu_direccion_habitacion','clie_natu_puntos','fk_clie_natu_lugar','telefono']

    def get_telefono(self, obj):
        telefono=Telefono.objects.filter(fk_telf_clie_natu=obj.clie_natu_id).select_related('fk_telf_telf_codi')
        serializer=TelefonoClienteNatuSerializer(telefono,many=True)
        return serializer.data
    
    
#serializador para registrar el cliente natural
class ClienteNaturalFormSerializer(serializers.ModelSerializer):
    fk_clie_natu_lugar=serializers.PrimaryKeyRelatedField(queryset=Lugar.objects.filter(lugar_tipo='parroquia').all())
    codigo_telefono=serializers.PrimaryKeyRelatedField(queryset=TelefonoCodigo.objects.all())
    telefono=serializers.CharField(max_length=7)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)  
    email = serializers.EmailField()
    class Meta:
        model=ClienteNatural
        fields=['clie_natu_id','clie_natu_rif','clie_natu_cedula_identidad','clie_natu_nombre','clie_natu_apellido','clie_natu_segundo_nombre','clie_natu_segundo_apellido','clie_natu_direccion_habitacion','fk_clie_natu_lugar','username','password','email','codigo_telefono','telefono']
    
    def get_lugar(self,obj):
        return LugarSerializer(obj.fk_clie_natu_lugar).data
    


class ClienteNaturalPostSerializer(serializers.ModelSerializer):
    fk_clie_natu_lugar=serializers.PrimaryKeyRelatedField(queryset=Lugar.objects.filter(lugar_tipo='parroquia').all())
 
    class Meta:
        model=ClienteNatural
        fields=['clie_natu_id','clie_natu_rif','clie_natu_cedula_identidad','clie_natu_nombre','clie_natu_apellido','clie_natu_segundo_nombre','clie_natu_segundo_apellido','clie_natu_direccion_habitacion','fk_clie_natu_lugar']
    
    def get_lugar(self,obj):
        return LugarSerializer(obj.fk_clie_natu_lugar).data
    

class NumeroAfiliacionNatuSerializer(serializers.ModelSerializer):
    class Meta:
        model=AfiliadoCodigo
        fields=['afil_codigo_codigo','fk_afil_clie_natu']


#serializadores para el cliente natural

class TelefonoGeneralClienteJuriSerializer(serializers.ModelSerializer):
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_telf_codi','telf_id','fk_telf_clie_juri']
        
        
class TelefonoPostClienteJuriSerializer(serializers.ModelSerializer):
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_telf_codi','telf_id']
        
    def create(self, validated_data):
        cliente_id=self.context['telf_clie_juri_id']
        return Telefono.objects.create(fk_telf_clie_juri_id=cliente_id, **validated_data)
class TelefonoClienteJuriSerializer(serializers.ModelSerializer):
    fk_telf_telf_codi=CodigoTelefonoSerializer()
    class Meta:
        model=Telefono
        fields=['telf_numero','fk_telf_clie_juri','fk_telf_telf_codi']

class TipoComercioSerializer(serializers.ModelSerializer):
    class Meta:
        model=TipoComercio
        fields=['tipo_comer_nombre']

class ClienteJuridicoSerializer(serializers.ModelSerializer):
    fk_clie_juri_lugar_fisica=LugarSerializer()
    fk_clie_juri_lugar_fiscal=LugarSerializer()
    fk_clie_juri_tipo_come=TipoComercioSerializer()
    telefono=serializers.SerializerMethodField(method_name='get_telefono')
    class Meta:
        model=ClienteJuridico
        fields=['clie_juri_id','clie_juri_rif','clie_juri_denominacion_comercial','clie_juri_razon_social','clie_juri_pagina_web','clie_juri_capital_disponible','clie_juri_direccion_fisica','clie_juri_direccion_fiscal','clie_juri_puntos','fk_clie_juri_tipo_come','fk_clie_juri_lugar_fisica','fk_clie_juri_lugar_fiscal','telefono']
        
    def get_telefono(self, obj):
        telefono=Telefono.objects.filter(fk_telf_clie_juri=obj.clie_juri_id).select_related('fk_telf_telf_codi')
        serializer=TelefonoClienteJuriSerializer(telefono,many=True)
        return serializer.data
    
    
#serializador para registrar el cliente Juridico     
class ClienteJuridicoPostSerializer(serializers.ModelSerializer):
    fk_clie_juri_lugar_fisica=serializers.PrimaryKeyRelatedField(queryset=Lugar.objects.filter(lugar_tipo='parroquia').all())
    fk_clie_juri_lugar_fiscal=serializers.PrimaryKeyRelatedField(queryset=Lugar.objects.filter(lugar_tipo='parroquia').all())
    
    class Meta:
        model=ClienteJuridico
        fields=['clie_juri_id','clie_juri_rif','clie_juri_denominacion_comercial','clie_juri_razon_social','clie_juri_pagina_web','clie_juri_capital_disponible','clie_juri_direccion_fisica','clie_juri_direccion_fiscal','fk_clie_juri_tipo_come','fk_clie_juri_lugar_fisica','fk_clie_juri_lugar_fiscal']
    
    def get_lugar(self,obj):
        return LugarSerializer(obj.fk_clie_juri_lugar_fisica).data
    
    def get_lugar_fiscal(self,obj):
        return LugarSerializer(obj.fk_clie_juri_lugar_fiscal).data





class ClienteJuridicoFormSerializer(serializers.ModelSerializer):
    fk_clie_juri_lugar_fisica=serializers.PrimaryKeyRelatedField(queryset=Lugar.objects.filter(lugar_tipo='parroquia').all())
    fk_clie_juri_lugar_fiscal=serializers.PrimaryKeyRelatedField(queryset=Lugar.objects.filter(lugar_tipo='parroquia').all())
    codigo_telefono=serializers.PrimaryKeyRelatedField(queryset=TelefonoCodigo.objects.all())
    telefono=serializers.CharField(max_length=7)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)  
    email = serializers.EmailField()
    class Meta:
        model=ClienteJuridico
        fields=['clie_juri_id','clie_juri_rif','clie_juri_denominacion_comercial','clie_juri_razon_social','clie_juri_pagina_web','clie_juri_capital_disponible','clie_juri_direccion_fisica','clie_juri_direccion_fiscal','fk_clie_juri_tipo_come','fk_clie_juri_lugar_fisica','fk_clie_juri_lugar_fiscal','username','password','email','codigo_telefono','telefono']
    
    def get_lugar(self,obj):
        return LugarSerializer(obj.fk_clie_juri_lugar_fisica).data
    
    def get_lugar_fiscal(self,obj):
        return LugarSerializer(obj.fk_clie_juri_lugar_fiscal).data

class NumeroAfiliacionJuriSerializer(serializers.ModelSerializer):
    class Meta:
        model=AfiliadoCodigo
        fields=['afil_codigo_codigo','fk_afil_clie_juri']


#serializadores SOLO DE VISTA para completar el formulario de registro 
class TelefonoCodigoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=TelefonoCodigo
        fields=['telf_cod_id','telf_cod_codigo']
        
class LugarGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=Lugar
        fields=['lugar_id','lugar_nombre','lugar_tipo','fk_lugar_lugar']
        
class TipoComercioGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=TipoComercio
        fields=['tipo_comer_id','tipo_comer_nombre']
        

class ProvedorFiltroSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Proveedor
        fields=['prov_denominacion_comercial']

class TipoRonFiltroSerializer(serializers.ModelSerializer):
        
        class Meta:
            model=TipoRon
            fields=['tipo_ron_nombre']


class CodigoCarnet(serializers.ModelSerializer):
    class Meta:
        model=AfiliadoCodigo
        fields=['afil_codigo_codigo']

class CarnetNatuSerializer(serializers.ModelSerializer):
    codigo_carnet=serializers.SerializerMethodField(method_name='get_codigo_carnet')
    class Meta:
        model=ClienteNatural
        fields=['clie_natu_cedula_identidad','clie_natu_nombre','clie_natu_apellido','codigo_carnet']

    def get_codigo_carnet(self, obj):
        codigo_carnet=AfiliadoCodigo.objects.filter(fk_afil_clie_natu=obj.clie_natu_id)
        serializer=CodigoCarnet(codigo_carnet,many=True)
        return serializer.data
    

class CarnetJuriSerializer(serializers.ModelSerializer):
    codigo_carnet=serializers.SerializerMethodField(method_name='get_codigo_carnet')
    class Meta:
        model=ClienteJuridico
        fields=['clie_juri_rif','clie_juri_denominacion_comercial','codigo_carnet']
        
    def get_codigo_carnet(self, obj):
        codigo_carnet=AfiliadoCodigo.objects.filter(fk_afil_clie_juri=obj.clie_juri_id)
        serializer=CodigoCarnet(codigo_carnet,many=True)
        return serializer.data
    
class CarritoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Carrito
        fields=['fk_carr_clie_natu','fk_carr_clie_juri','carr_id','carri_empleado','fk_carr_clie_emples']


class BotellaInventarioCarritoSerializer(serializers.ModelSerializer):
    imagen=serializers.SerializerMethodField(method_name='get_images')
    class Meta:
        model=Botella
        fields=['bote_nombre','imagen','bote_id']
        
    
    def get_images(self, obj):
        request = self.context.get('request')
        images = BoteImagenSerializer(obj.bote_images.all(), many=True, context={'request': request}).data
        return images
    
    
    
    
    
class InventarioTiendaCarritoSerializer(serializers.ModelSerializer):
    fk_inve_tiend_bote = BotellaInventarioCarritoSerializer()
    precio=serializers.SerializerMethodField(method_name='get_precio')
    class Meta:
        model=InventarioTienda
        fields=['inve_tiend_id','fk_inve_tiend_bote','precio','inve_tiend_cantidad']
        
    def to_representation(self, instance):
        instance=InventarioTienda.objects.select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend').get(pk=instance.pk)
        return super().to_representation(instance)
    
    def get_precio(self, instance):
        precio = HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=instance.inve_tiend_id,hist_ron_fecha_fin__isnull=True).select_related('fk_hist_ron_inve_tiend').first()
        serializer = HistoricoRonSerializer(precio)
        return serializer.data
 
class OfertaCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Oferta
        fields=['ofer_nombre']
       
    
class OfertaBotellaCarritoSerializer(serializers.ModelSerializer):
    fk_ofer_bote_ofer=OfertaCarritoSerializer()
           
    class Meta:
        model=OfertaBotella
        fields=['ofer_bote_id','fk_ofer_bote_ofer','ofer_bote_porcentaje']

    

class AfiliadoSerializerCarrito(serializers.ModelSerializer):
    class Meta:
        model=Afiliado
        fields=['afil_id','afil_nombre','afil_precio']
        

class EntradaEventoCarritoSerializer(serializers.ModelSerializer):
    fk_entr_envt_evento=serializers.SlugRelatedField(slug_field='event_nombre',read_only=True)
    class Meta:
        model=EntradaEvento
        fields=['entr_envt_id','entr_envt_nombre','entr_envt_precio','fk_entr_envt_evento','entr_evnt_cantidad']
        
        
class CarritoItemSerializer(serializers.ModelSerializer):
    fk_carri_item_inve_tiend=InventarioTiendaCarritoSerializer()
    fk_carri_item_ofer_ron=OfertaBotellaCarritoSerializer()
    fk_carri_item_entr_evento=EntradaEventoCarritoSerializer()
    fk_carri_item_afil=AfiliadoSerializerCarrito()
    class Meta:
        model=CarritoItem
        fields=['carri_item_cantidad','fk_carri_item_inve_tiend','fk_carri_item_ofer_ron','fk_carri_item_entr_evento','fk_carri_item_afil','carri_item_id']

class CarritoGetSerializer(serializers.ModelSerializer):
    items=serializers.SerializerMethodField(method_name='get_items')
    class Meta:
        model=Carrito
        fields=['carr_uuid','items']
        
    def get_items(self, obj):
        items=CarritoItem.objects.filter(fk_carri_item_carri=obj.carr_id)
        serializer=CarritoItemSerializer(items,many=True)
        return serializer.data



class CarritoItemPostSerializer(serializers.ModelSerializer):
    carr_uuid=serializers.CharField(max_length=50,write_only=True,required=False)
    class Meta:
        model=CarritoItem
        fields=['carri_item_cantidad','fk_carri_item_inve_tiend','fk_carri_item_ofer_ron','fk_carri_item_entr_evento','fk_carri_item_afil','carr_uuid','carri_item_id']
    
    def create(self, validated_data):
        uuid=validated_data.pop('carr_uuid')
        carrito=Carrito.objects.get(carr_uuid=uuid)
        carri_id=carrito.carr_id
        
        if 'fk_carri_item_inve_tiend' in validated_data and validated_data['fk_carri_item_inve_tiend'] is not None:
            if 'fk_carri_item_ofer_ron' in validated_data and validated_data['fk_carri_item_ofer_ron'] is not None:
                precio=HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=validated_data['fk_carri_item_inve_tiend'].inve_tiend_id,hist_ron_fecha_fin__isnull=True).select_related('fk_hist_ron_inve_tiend').first()
                carri_precio=precio.hist_ron_precio
                oferta=OfertaBotella.objects.filter(ofer_bote_id=validated_data['fk_carri_item_ofer_ron'].ofer_bote_id).first()
                oferta_porcentaje=oferta.ofer_bote_porcentaje
                carri_item_precio=carri_precio-(carri_precio*oferta_porcentaje/100)
            else:
                carri_item_precio=HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=validated_data['fk_carri_item_inve_tiend'].inve_tiend_id,hist_ron_fecha_fin__isnull=True).select_related('fk_hist_ron_inve_tiend').first()
                carri_item_precio=carri_item_precio.hist_ron_precio
                
        elif ('fk_carri_item_ofer_ron' in validated_data and validated_data['fk_carri_item_ofer_ron'] is not None
            and 'fk_carri_item_inve_tiend' in validated_data and validated_data['fk_carri_item_inve_tiend'] is None):   
               raise serializers.ValidationError({'error': 'Debe seleccionar una botella'})

            
        elif 'fk_carri_item_entr_evento' in validated_data and validated_data['fk_carri_item_entr_evento'] is not None:
            precio=EntradaEvento.objects.filter(entr_envt_id=validated_data['fk_carri_item_entr_evento'].entr_envt_id).first()
            carri_item_precio=precio.entr_envt_precio
        elif 'fk_carri_item_afil' in validated_data and validated_data['fk_carri_item_afil'] is not None:
            carri_item_precio=validated_data['fk_carri_item_afil'].afil_precio
            
                
        return CarritoItem.objects.create(fk_carri_item_carri_id=carri_id, carri_item_precio=carri_item_precio, **validated_data)
    
    def update(self, instance, validated_data): 
        instance.carri_item_cantidad = validated_data.get('carri_item_cantidad', instance.carri_item_cantidad)
        instance.fk_carri_item_inve_tiend = validated_data.get('fk_carri_item_inve_tiend', instance.fk_carri_item_inve_tiend)
        instance.fk_carri_item_ofer_ron = validated_data.get('fk_carri_item_ofer_ron', instance.fk_carri_item_ofer_ron)
        instance.fk_carri_item_entr_evento = validated_data.get('fk_carri_item_entr_evento', instance.fk_carri_item_entr_evento)
        instance.fk_carri_item_afil = validated_data.get('fk_carri_item_afil', instance.fk_carri_item_afil)
        

        if 'fk_carri_item_inve_tiend' in validated_data and validated_data['fk_carri_item_inve_tiend'] is not None:
            if 'fk_carri_item_ofer_ron' in validated_data and validated_data['fk_carri_item_ofer_ron'] is not None:
                precio=HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=validated_data['fk_carri_item_inve_tiend'].inve_tiend_id,hist_ron_fecha_fin__isnull=True).select_related('fk_hist_ron_inve_tiend').first()
                carri_precio=precio.hist_ron_precio
                oferta=OfertaBotella.objects.filter(ofer_bote_id=validated_data['fk_carri_item_ofer_ron'].ofer_bote_id).first()
                oferta_porcentaje=oferta.ofer_bote_porcentaje
                carri_item_precio=carri_precio-(carri_precio*oferta_porcentaje/100)
            else:
                carri_item_precio=HistoricoRon.objects.filter(fk_hist_ron_inve_tiend=validated_data['fk_carri_item_inve_tiend'].inve_tiend_id,hist_ron_fecha_fin__isnull=True).select_related('fk_hist_ron_inve_tiend').first()
                carri_item_precio=carri_item_precio.hist_ron_precio
        
        elif ('fk_carri_item_ofer_ron' in validated_data and validated_data['fk_carri_item_ofer_ron'] is not None
            and 'fk_carri_item_inve_tiend' in validated_data and validated_data['fk_carri_item_inve_tiend'] is None):   
               raise serializers.ValidationError({'error': 'Debe seleccionar una botella'})
               
        elif 'fk_carri_item_entr_evento' in validated_data and validated_data['fk_carri_item_entr_evento'] is not None:
            precio=EntradaEvento.objects.filter(entr_envt_id=validated_data['fk_carri_item_entr_evento'].entr_envt_id).first()
            carri_item_precio=precio.entr_envt_precio
        elif 'fk_carri_item_afil' in validated_data and validated_data['fk_carri_item_afil'] is not None:
            carri_item_precio=validated_data['fk_carri_item_afil'].afil_precio
      
        instance.carri_item_cantidad = validated_data.get('carri_item_cantidad', instance.carri_item_cantidad)
        instance.carri_item_precio = carri_item_precio
        instance.save()
        return instance
    
class BotellaInventarioCarritoOFERTASerializer(serializers.ModelSerializer):
    class Meta:
        model=Botella
        fields=['bote_nombre','bote_id']
        
class OfertaBotellaVerSerializer(serializers.ModelSerializer):
    fk_ofer_bote_ofer=OfertaCarritoSerializer()
    fk_ofer_bote_bote=BotellaInventarioCarritoOFERTASerializer()
           
    class Meta:
        model=OfertaBotella
        fields=['fk_ofer_bote_ofer','ofer_bote_porcentaje','fk_ofer_bote_bote','ofer_bote_id']

class AfiliadoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=Afiliado
        fields=['afil_id','afil_nombre','afil_precio']


class TDCSerializer(serializers.ModelSerializer):
    class Meta:
        model=TarjetaCredito
        fields=['tdc_id','tdc_numero_tarjeta','tdc_nombre_titular','tdc_fecha_vencimiento','tdc_cvv']
    
    def validate_fecha_vencimiento(self, value):
        current_date = date.today()

        if value <= current_date + timedelta(days=30):
            raise serializers.ValidationError("La fecha de vencimiento debe ser al menos un mes en el futuro.")

        return value
    
    def validate(self, data):
        fecha_vencimiento = data.get('tdc_fecha_vencimiento') 
        if self.validate_fecha_vencimiento(fecha_vencimiento) is not None:
            pass
        return super().validate(data)

     
    
    def create(self, validated_data):
        cliente=self.context['cliente']
        if cliente.fk_usua_clie_natu:
            clieid=cliente.fk_usua_clie_natu
            return TarjetaCredito.objects.create(fk_tdc_clie_natu=clieid, **validated_data)
        elif cliente.fk_usua_clie_juri: 
            clieid=cliente.fk_usua_clie_juri
            return TarjetaCredito.objects.create(fk_tdc_clie_juri=clieid, **validated_data)
            
        
class PuntosNatuSerializer(serializers.ModelSerializer):
    class Meta:
        model=Puntos
        fields=['punt_tiene_puntos','fk_punt_clie_natu']
        
class PuntosJuriSerializer(serializers.ModelSerializer):
    class Meta:
        model=Puntos
        fields=['punt_tiene_puntos','fk_punt_clie_juri']
        
class ChequeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cheque
        fields=['cheq_numero_cheque','cheq_banco','chq_nombre_titular']
        
    def create(self, validated_data):
        cliente=self.context['cliente']
        if cliente.fk_usua_clie_natu:
            clieid=cliente.fk_usua_clie_natu
            return Cheque.objects.create(fk_cheq_clie_natu=clieid, **validated_data)
        elif cliente.fk_usua_clie_juri: 
            clieid=cliente.fk_usua_clie_juri
            return Cheque.objects.create(fk_cheq_clie_juri=clieid, **validated_data)
        
class EfectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Efectivo
        fields=['efe_monto']
        
    def create(self, validated_data):
        
        cliente=self.context['cliente']
        if cliente.fk_usua_clie_natu:
            clieid=cliente.fk_usua_clie_natu
            return Efectivo.objects.create(fk_efe_clie_natu=clieid, **validated_data)
        elif cliente.fk_usua_clie_juri: 
            clieid=cliente.fk_usua_clie_juri
            return Efectivo.objects.create(fk_efe_clie_juri=clieid, **validated_data)

class HistoricoPuntoSerializer(serializers.ModelSerializer):
    hist_punt_fecha_inicio=serializers.DateField(format="%d/%m/%Y")
    class Meta:
        model=HistoricoPunto
        fields=['hist_punt_valor','hist_punt_fecha_inicio']

class HistoricoDolarSerializer(serializers.ModelSerializer):
    hist_dolar_fecha_inicio=serializers.DateTimeField(format="%d/%m/%Y" " "  "%H:%M")
    class Meta:
        model=HistoricoDolar
        fields=['hist_dolar_valor','hist_dolar_fecha_inicio']

class VentaOnlineSerializer(serializers.ModelSerializer):
    uuid_carrito=serializers.CharField(max_length=50,write_only=True,required=True)
    tarjeta_id = serializers.IntegerField(write_only=True, min_value=1)
    cantidad_tarjeta = serializers.FloatField(write_only=True, min_value=1)
    puntos_id = serializers.IntegerField(write_only=True, required=False, min_value=1)
    cantidad_puntos = serializers.FloatField(write_only=True, required=False, min_value=1)
    class Meta:
        model=Venta
        fields=['venta_direccion','fk_vent_direccion','uuid_carrito','tarjeta_id','cantidad_tarjeta','puntos_id','cantidad_puntos']
        



class InventarioTiendaVentaSerializer(serializers.ModelSerializer):
    fk_inve_tiend_bote = BotellaInventarioCarritoSerializer()
    
    class Meta:
        model=InventarioTienda
        fields=['fk_inve_tiend_bote']
        
    def to_representation(self, instance):
        instance=InventarioTienda.objects.select_related('fk_inve_tiend_bote__fk_bote_ron','fk_inve_tiend_tiend').get(pk=instance.pk)
        return super().to_representation(instance)



class AfiliadoSerializerVenta(serializers.ModelSerializer):
    class Meta:
        model=Afiliado
        fields=['afil_nombre']

class EntradaEventoVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model=EntradaEvento
        fields=['entr_envt_nombre','entr_envt_precio']

class CarritoItemVENTASerializer(serializers.ModelSerializer):
    fk_carri_item_inve_tiend=InventarioTiendaVentaSerializer()
    fk_carri_item_ofer_ron=OfertaBotellaCarritoSerializer()
    fk_carri_item_entr_evento=EntradaEventoVentaSerializer()
    fk_carri_item_afil=AfiliadoSerializerVenta()
    monto_total=serializers.SerializerMethodField(method_name='get_monto_total')
    class Meta:
        model=CarritoItem
        fields=['carri_item_cantidad','carri_item_precio','monto_total','fk_carri_item_inve_tiend','fk_carri_item_ofer_ron','fk_carri_item_entr_evento','fk_carri_item_afil',]

    def get_monto_total(self, obj):
        monto_total=obj.carri_item_cantidad*obj.carri_item_precio
        monto_total_formateado = "{:.2f}".format(monto_total)
        return monto_total_formateado
class CarritoGetVENTASerializer(serializers.ModelSerializer):
    iten=serializers.SerializerMethodField(method_name='get_items')
    class Meta:
        model=Carrito
        fields=['iten']
        
    def get_items(self, obj):
        items=CarritoItem.objects.filter(fk_carri_item_carri=obj.carr_id)
        serializer=CarritoItemVENTASerializer(items,many=True)
        return serializer.data


class VentaGetSerializer(serializers.ModelSerializer):
    itenes=serializers.SerializerMethodField(method_name='get_itenes')
    fk_vent_direccion=LugarSerializer()
    class Meta:
        model=Venta
        fields=['vent_fecha_venta','vent_monto_total','venta_puntos','venta_direccion','fk_vent_direccion','itenes','vent_id']
    
    def get_itenes(self, obj):
        itenes=Carrito.objects.filter(carr_id=obj.fk_vent_carri.carr_id)
        serializer=CarritoGetVENTASerializer(itenes,many=True)
        return serializer.data


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['vent_fecha_venta','vent_monto_total','venta_puntos','venta_direccion','fk_vent_direccion','fk_vent_carri']

class AfiliadoClienteProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model=AfiliadoClienteProveedor
        fields=['afil_clie_prov_fecha_afiliacion','afil_clie_prov_fecha_vencimiento','fk_afil_clie_prov_afil','fk_afil_clie_prov_clie_juri','fk_afil_clie_prov_clie_natu','fk_afil_clie_prov_prov']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Pago
        fields=['pago_cantidad_pagada','fk_pago_vent','fk_pago_tdc','fk_pago_punt','fk_pago_hist_dolar','fk_pago_hist_punt','pago_tipo_pago']
    
class VentaStatusVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model=VentaStatus
        fields=['venta_stat_status','venta_stat_fecha_inicio','fk_venta_stat_stat_pedi','fk_venta_stat_vent','venta_stat_fecha_fin']

class AfiliadoBooleanSerializer(serializers.ModelSerializer):
    class Meta:
        model=Afiliado
        fields=['afil_id','afil_nombre','afil_precio']
        
class PuntoSerializer(serializers.ModelSerializer):
    cantidad_puntos=serializers.SerializerMethodField(method_name='get_cantidad_puntos')
    class Meta:
        model=Puntos
        fields=['punt_id','cantidad_puntos']
        
    def get_cantidad_puntos(self,obj):
        usuario=self.context['usuario']
        if usuario.fk_usua_clie_natu:
            puntos=ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id).first()
            return puntos.clie_natu_puntos
        elif usuario.fk_usua_clie_juri:
            puntos=ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id).first()
            return puntos.clie_juri_puntos


class VentaStatusGetSerializer(serializers.ModelSerializer):
    hora_inicio=serializers.SerializerMethodField(method_name='get_hora_inicio')
    hora_fin=serializers.SerializerMethodField(method_name='get_hora_fin')
    fecha_inicio=serializers.SerializerMethodField(method_name='get_fecha_inicio')
    fecha_fin=serializers.SerializerMethodField(method_name='get_fecha_fin')
    
    
    fk_venta_stat_stat_pedi=serializers.SlugRelatedField(slug_field='stat_pedi_nombre',read_only=True)
    class Meta:
        model=VentaStatus
        fields=['venta_stat_status','fk_venta_stat_stat_pedi','fecha_inicio','hora_inicio','fecha_fin','hora_fin']
        
    def get_status_venta(self,obj):
        status=VentaStatus.objects.filter(fk_venta_stat_vent=obj.fk_venta_stat_vent.vent_id).all()
        serializer=VentaStatusVentaSerializer(status,many=True)
        return serializer.data

    def get_hora_inicio(self,obj):
        hora_inicio=obj.venta_stat_fecha_inicio.strftime("%H:%M")
        return hora_inicio
    
    def get_hora_fin(self,obj):
        if obj.venta_stat_fecha_fin is None:
            return None
        else:
            hora_fin=obj.venta_stat_fecha_fin.strftime("%H:%M")
            return hora_fin
        
    def get_fecha_inicio(self,obj):
        fecha_inicio=obj.venta_stat_fecha_inicio.strftime("%d/%m/%Y")
        return fecha_inicio
    
    def get_fecha_fin(self,obj):
        if obj.venta_stat_fecha_fin is None:
            return None
        else:
            fecha_fin=obj.venta_stat_fecha_fin.strftime("%d/%m/%Y")
            return fecha_fin
        

class VentaGetSimpleSerializer(serializers.ModelSerializer):
    vent_fecha_venta=serializers.DateTimeField(format="%d/%m/%Y")
    status_venta=serializers.SerializerMethodField(method_name='get_status_venta')
    class Meta:
        model=Venta
        fields=['vent_id','vent_fecha_venta','vent_monto_total','venta_puntos','venta_direccion','fk_vent_direccion','status_venta']
        
    def get_status_venta(self,obj):
        status=VentaStatus.objects.filter(fk_venta_stat_vent=obj.vent_id).all().select_related('fk_venta_stat_stat_pedi')
        serializer=VentaStatusGetSerializer(status,many=True)
        orden_deseado = ["Orden Recibida", "Orden Aprobada", "Orden En Camino", "Orden Entregada"]
        status_ordenado = sorted(serializer.data, key=lambda x: orden_deseado.index(x["fk_venta_stat_stat_pedi"]))

        return status_ordenado

class VentaFisicaSerializer(serializers.ModelSerializer):
    uuid_carrito=serializers.CharField(max_length=50,write_only=True,required=True)
    cantidad_tarjeta = serializers.FloatField(write_only=True, min_value=1)
    cantidad_puntos = serializers.FloatField(write_only=True, required=False, min_value=1)
    cantidad_cheque = serializers.FloatField(write_only=True, required=False, min_value=1)
    cantidad_efectivo = serializers.FloatField(write_only=True, required=False, min_value=1)
    usuario_natu=serializers.IntegerField(write_only=True, required=False)
    usuario_juri=serializers.IntegerField(write_only=True, required=False)    
    class Meta:
        model=Venta
        fields=['venta_direccion','fk_vent_direccion','uuid_carrito','cantidad_tarjeta','cantidad_puntos','cantidad_cheque','cantidad_efectivo','usuario_natu','usuario_juri']
        
class ReporteVentaSerializer(serializers.Serializer):
    fecha_inicio=serializers.DateField(format="%d/%m/%Y")
    fecha_fin=serializers.DateField(format="%d/%m/%Y")
    categoria=serializers.PrimaryKeyRelatedField(queryset=ClasificacionRon.objects.all())
    tipo_ron=serializers.PrimaryKeyRelatedField(queryset=TipoRon.objects.all())
    
class ReporteDashboardSerializer(serializers.Serializer):
    fecha_inicio=serializers.DateField(format="%Y-%m-%d")
    fecha_fin=serializers.DateField(format="%Y-%m-%d")