import string
import qrcode
from .serializers import *
from .models import *
from rest_framework.viewsets import ModelViewSet
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION,DELETION,CHANGE
from .permissions import *
from .pagintation import DefaultPagination,CustomPagination,EventoPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import  Table, Image
from reportlab.lib import colors
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.utils import timezone
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
import pytz
from django.db import connection, transaction
from core.serializers import UserCreateSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
import secrets
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage, ImageDraw as ImageDraw, ImageFont as ImageFont
from django.db.models import OuterRef, Subquery
from .envios import enviar_correo

class LogEntryViewSetMixin:
    def log_action(self, instance, action_flag):
        
        if  self.request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(instance)
            object_id = getattr(instance, instance._meta.pk.name)
            LogEntry.objects.log_action(
            user_id=self.request.user.id,
            content_type_id=content_type.id,
            object_id=object_id,
            object_repr=str(instance),
            action_flag=action_flag,
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self.log_action(instance, ADDITION)

    def perform_destroy(self, instance):
        self.log_action(instance, DELETION)
        instance.delete()
    
    def perform_update(self, serializer):
        instance = serializer.save()
        self.log_action(instance, CHANGE)








class EventoDetailViewSet(ModelViewSet):
    pagination_class = DefaultPagination
    permission_classes = [IsReadOnly]

    def get_queryset(self):
        return Evento.objects.filter(pk=self.kwargs['pk'])
    
    def get_serializer_class(self):
        method=self.request.method
        if method=='GET':
            return EventoDetailGetSerializer
           
    def get_serliazer_context(self):
        return {'request': self.request}
    

class EventoViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    pagination_class = EventoPagination
    serializer_class=EventoGetSerializer
    
    def get_queryset(self):
        caracas_timezone = pytz.timezone('America/Caracas')
        now_caracas=timezone.now().astimezone(caracas_timezone)
        
        ya_hechos_param=self.request.query_params.get('pasados')
        
        queryset = Evento.objects.prefetch_related('event_images').select_related('fk_event_lugar').filter(event_fecha_fin__gte=now_caracas.date())
        
        if ya_hechos_param:
            queryset=Evento.objects.prefetch_related('event_images').select_related('fk_event_lugar').filter(event_fecha_fin__lt=now_caracas.date())
        
        return queryset
    
            
    
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    
class InventarioTiendaViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    pagination_class = DefaultPagination
    serializer_class=InventarioTiendaSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def get_queryset(self):
        ron_nombre_param=self.request.query_params.get('nombre_ron')
        ron_calisifcacion_param=self.request.query_params.get('clasificacion_ron')
        ron_tipo_param=self.request.query_params.get('tipo_ron')
        ron_grado_alcohol_param=self.request.query_params.get('grado_alcohol')
        ron_anejamientos_param=self.request.query_params.get('anejamiento')
        ron_proveedor_param=self.request.query_params.get('proveedor')
        ron_precio_order=self.request.query_params.get('order_by')
        ron_min_price=self.request.query_params.get('min_price')
        ron_max_price=self.request.query_params.get('max_price')
        
        queryset = InventarioTienda.objects.select_related('fk_inve_tiend_bote', 'fk_inve_tiend_tiend')
        usuario=self.request.user
        
        
        if usuario.is_authenticated:
            
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
                queryset = queryset.filter(fk_inve_tiend_tiend__fk_tiend_tipo_tiend__tipo_tiend_nombre='Online')
        
            else:
                if usuario.fk_usua_empl.empl_tiend_empl.filter(empl_tiend_fecha_fin__isnull=True).exists():
                
                    tienda_empleado = usuario.fk_usua_empl.empl_tiend_empl.filter(empl_tiend_fecha_fin__isnull=True).first()
                    tienda=tienda_empleado.fk_empl_tiend_tiend.tiend_id
                    queryset = queryset.filter(fk_inve_tiend_tiend__pk=tienda)
                    
                else:
                    queryset = queryset.filter(fk_inve_tiend_tiend__fk_tiend_tipo_tiend__tipo_tiend_nombre='Online')
                    
        else:
            
            queryset = queryset.filter(fk_inve_tiend_tiend__fk_tiend_tipo_tiend__tipo_tiend_nombre='Online')
            
        if ron_nombre_param:
            queryset = queryset.filter(fk_inve_tiend_bote__bote_nombre__icontains=ron_nombre_param)

        if ron_calisifcacion_param:
            queryset = queryset.filter(fk_inve_tiend_bote__fk_bote_ron__fk_ron_clasi_tipo__fk_clasi_tipo_clasi_ron__clasi_ron_nombre=ron_calisifcacion_param)

        if ron_tipo_param:
            queryset = queryset.filter(fk_inve_tiend_bote__fk_bote_ron__fk_ron_clasi_tipo__fk_clasi_tipo_tipo_ron__tipo_ron_nombre=ron_tipo_param)
           
        if ron_anejamientos_param:
            queryset = queryset.filter(fk_inve_tiend_bote__fk_bote_ron__fk_ron_anej__anej_cantidad_anos__lte=ron_anejamientos_param)   
            
        if ron_proveedor_param:
            queryset = queryset.filter(fk_inve_tiend_bote__fk_bote_ron__fk_ron_prove__prov_denominacion_comercial__icontains=ron_proveedor_param)

        if ron_grado_alcohol_param:
            queryset = queryset.filter(fk_inve_tiend_bote__fk_bote_ron__fk_ron_grado_alco__grad_alco_porcentaje_alcohol=ron_grado_alcohol_param)
        
        if ron_precio_order == 'precio':
            queryset = queryset.annotate(
                ultimo_precio=Subquery(
                    HistoricoRon.objects.filter(
                        fk_hist_ron_inve_tiend=OuterRef('pk'),
                        hist_ron_fecha_fin__isnull=True
                    ).values('hist_ron_precio')[:1]
                )
            ).order_by('ultimo_precio')

        elif ron_precio_order == '-precio':
            queryset = queryset.annotate(
                ultimo_precio=Subquery(
                    HistoricoRon.objects.filter(
                        fk_hist_ron_inve_tiend=OuterRef('pk'),
                        hist_ron_fecha_fin__isnull=True
                    ).values('hist_ron_precio')[:1]
        )
        ).order_by('-ultimo_precio')
            
        if ron_min_price:
            queryset = queryset.annotate(
                ultimo_precio=Subquery(
                    HistoricoRon.objects.filter(
                        fk_hist_ron_inve_tiend=OuterRef('pk'),
                        hist_ron_fecha_fin__isnull=True
                    ).values('hist_ron_precio')[:1]
                )
            ).filter(ultimo_precio__gte=ron_min_price)
        
        if ron_max_price:
            queryset = queryset.annotate(
                ultimo_precio=Subquery(
                    HistoricoRon.objects.filter(
                        fk_hist_ron_inve_tiend=OuterRef('pk'),
                        hist_ron_fecha_fin__isnull=True
                    ).values('hist_ron_precio')[:1]
                )
            ).filter(ultimo_precio__lte=ron_max_price)
            
        
        return queryset
    
class BotellaDetailViewSet(ModelViewSet):
    serializer_class = BotellaDetailSerializer
    permission_classes = [IsReadOnly]

    def get_queryset(self):
        return Botella.objects.filter(bote_id=self.kwargs['pk']).select_related('fk_bote_ron')

    def get_serializer_context(self):
        return {'request': self.request,'user':self.request.user}


class OfertaViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    serializer_class = OfertaBotellaSerializer
    
    def get_queryset(self):
        caracas_timezone = pytz.timezone('America/Caracas')
        now_caracas=timezone.now().astimezone(caracas_timezone)
        return OfertaBotella.objects.select_related('fk_ofer_bote_bote', 'fk_ofer_bote_ofer').filter(fk_ofer_bote_ofer__ofer_fecha_fin__gte=now_caracas.date())
    
    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'])
    def pdf(self, request, pk=None):
        queryset = self.get_queryset()
        back_ground_path = 'images/diarioronero.png'
        background_image = ImageReader(back_ground_path)
        pdf_bytes = BytesIO()
        width, height = background_image.getSize()
        pdf = canvas.Canvas(pdf_bytes, pagesize=(width, height))
        pdf.drawImage(background_image, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='c')
        table_data = [["Nombre", "Fecha Fin", "Descuento", "Imagen"]]

        for instance in queryset:
            table_data.append([
                instance.fk_ofer_bote_bote.bote_nombre,
                instance.fk_ofer_bote_ofer.ofer_fecha_fin.strftime("%d/%m/%Y"),
                "{} %".format(instance.ofer_bote_porcentaje),
                Image(instance.fk_ofer_bote_bote.bote_images.first().img_url.url, width=50, height=50)
            ])


        table = Table(table_data, colWidths=[300, 80, 100, 100])
        table.setStyle([

            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ])


        table_width, table_height = table.wrap(0, 0)

      
        x_position = (width - table_width) / 2
        y_position = -20

        table.drawOn(pdf, x_position, y_position)
        pdf.showPage()
        pdf.save()


        pdf_bytes.seek(0)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="your_pdf_filename.pdf"'
        return response

class EmpleadoViewSet(ModelViewSet):
    pagination_class = DefaultPagination
    serializer_class = EmpleadoSerializer
    permission_classes=[IsAuthenticated,IsReadOnly]

    def get_queryset(self):
        usuario=self.request.user
        if usuario.fk_usua_empl:
            queryset=Empleado.objects.filter(empl_id=usuario.fk_usua_empl.empl_id)
            return queryset
        else:
            return Empleado.objects.none()
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    
class ClienteNaturalViewSet(ModelViewSet):
    
    pagination_class = DefaultPagination
    permission_classes=[IsAuthenticated]

    def get_serializer_class(self):
        method=self.request.method
        if method=='GET':
            return ClienteNaturalSerializer
        elif method=='POST':
            return ClienteNaturalFormSerializer
        else :
            return ClienteNaturalPostSerializer
        

    def get_queryset(self):
        usuario=self.request.user
        
        if usuario.fk_usua_clie_natu:
            queryset=ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id)
            return queryset
        else:
            return ClienteNatural.objects.none()
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            sid = transaction.savepoint()
            cliente_natural_data = {
                'clie_natu_rif': request.data.get('clie_natu_rif', ''),
                'clie_natu_cedula_identidad': request.data.get('clie_natu_cedula_identidad', ''),
                'clie_natu_nombre': request.data.get('clie_natu_nombre', ''),
                'clie_natu_apellido': request.data.get('clie_natu_apellido', ''),
                'clie_natu_segundo_nombre': request.data.get('clie_natu_segundo_nombre', ''),
                'clie_natu_segundo_apellido': request.data.get('clie_natu_segundo_apellido', ''),
                'clie_natu_direccion_habitacion': request.data.get('clie_natu_direccion_habitacion', ''),
                'fk_clie_natu_lugar': request.data.get('fk_clie_natu_lugar', None),
            }

            cliente_natural_serializer = ClienteNaturalPostSerializer(data=cliente_natural_data)
            cliente_natural_serializer.is_valid(raise_exception=True)
            cliente_natural_instance = cliente_natural_serializer.save()


            usuario_data = {
                'username': request.data.get('username', ''),
                'password': request.data.get('password', ''),
                'email': request.data.get('email', ''),
                'fk_usua_clie_natu': cliente_natural_instance.clie_natu_id,
            }

            usuario_serializer = UserCreateSerializer(data=usuario_data)
            usuario_serializer.is_valid(raise_exception=True)
            usuario_instance=usuario_serializer.save()
            
            telefono_data=  {
                'telf_numero': request.data.get('telefono', ''),
                'fk_telf_telf_codi': request.data.get('codigo_telefono', None),
                'fk_telf_clie_natu': cliente_natural_instance.clie_natu_id,
            }
            
            telefono_data_serializer = TelefonoGeneralClienteNatuSerializer(data=telefono_data)
            telefono_data_serializer.is_valid(raise_exception=True)
            telefono_data_serializer.save()
            
            codigo_autogenerado = secrets.token_hex(4)[:8].upper()
            
            while True:
                if AfiliadoCodigo.objects.filter(afil_codigo_codigo=codigo_autogenerado).exists():
                    codigo_autogenerado = secrets.token_hex(4)[:8].upper()
                else:
                    break
            
            afiliado_data={
                'fk_afil_clie_natu':cliente_natural_instance.clie_natu_id,
                'afil_codigo_codigo':codigo_autogenerado,
            }
            
            afiliado_data_serializer = NumeroAfiliacionNatuSerializer(data=afiliado_data)
            afiliado_data_serializer.is_valid(raise_exception=True)
            afiliado_data_serializer.save()
            
            puntos_data={
                'fk_punt_clie_natu':cliente_natural_instance.clie_natu_id,
                'punt_tiene_puntos':True,
            }
            puntos_data_serializer=PuntosNatuSerializer(data=puntos_data)
            puntos_data_serializer.is_valid(raise_exception=True)
            puntos_data_serializer.save()
            
            refresh = RefreshToken.for_user(usuario_instance)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
                
            return Response({'access':access_token,'refresh':refresh_token}, status=status.HTTP_201_CREATED)
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    
class TelefonoClienteNaturalViewSet(ModelViewSet):
    serializer_class = TelefonoPostClienteNatuSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Telefono.objects.filter(fk_telf_clie_natu__clie_natu_id=self.request.user.fk_usua_clie_natu.clie_natu_id)
    
    
    def get_serializer_context(self):
        return {'telf_clie_natu_id': self.request.user.fk_usua_clie_natu.clie_natu_id}    
    
    
    
class ClienteJuridicoViewSet(ModelViewSet):
        
        pagination_class = DefaultPagination
        permission_classes=[IsAuthenticated]
    
        def get_serializer_class(self):
            method=self.request.method
            if method=='GET':
                return ClienteJuridicoSerializer
            elif method=='POST':
                return ClienteJuridicoFormSerializer
            else:
                return ClienteJuridicoPostSerializer
    
        def get_queryset(self):
            usuario=self.request.user
            
            if usuario.fk_usua_clie_juri:
                queryset=ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id)
                return queryset
            else:
                return ClienteJuridico.objects.none()
        
        def get_serializer_context(self):
            return {'request': self.request}
        
        def get_permissions(self):
            if self.action == 'create':
                return [AllowAny()]
            return super().get_permissions()
        
        def destroy(self, request, *args, **kwargs):
            raise MethodNotAllowed("DELETE")

        @transaction.atomic
        def create(self, request, *args, **kwargs):
            try:
                sid=transaction.savepoint()
                cliente_juridico_data = {
                    'clie_juri_rif': request.data.get('clie_juri_rif', ''),
                    'clie_juri_denominacion_comercial': request.data.get('clie_juri_denominacion_comercial', ''),
                    'clie_juri_razon_social': request.data.get('clie_juri_razon_social', ''),
                    'clie_juri_pagina_web': request.data.get('clie_juri_pagina_web', ''),
                    'clie_juri_capital_disponible': request.data.get('clie_juri_capital_disponible', ''),
                    'clie_juri_direccion_fisica': request.data.get('clie_juri_direccion_fisica', ''),
                    'clie_juri_direccion_fiscal': request.data.get('clie_juri_direccion_fiscal', ''),
                    'fk_clie_juri_tipo_come': request.data.get('fk_clie_juri_tipo_come', None),
                    'fk_clie_juri_lugar_fisica': request.data.get('fk_clie_juri_lugar_fisica', None),
                    'fk_clie_juri_lugar_fiscal': request.data.get('fk_clie_juri_lugar_fiscal', None),
                }
                
                cliente_juridico_serializer = ClienteJuridicoPostSerializer(data=cliente_juridico_data)
                cliente_juridico_serializer.is_valid(raise_exception=True)
                cliente_juridico_instance = cliente_juridico_serializer.save()
                
                usuario_data = {
                    'username': request.data.get('username', ''),
                    'password': request.data.get('password', ''),
                    'email': request.data.get('email', ''),
                    'fk_usua_clie_juri': cliente_juridico_instance.clie_juri_id,
                }
                
                usuario_serializer = UserCreateSerializer(data=usuario_data)
                usuario_serializer.is_valid(raise_exception=True)
                usuario_instance= usuario_serializer.save()
                
                telefono_data = {
                    'telf_numero': request.data.get('telefono', ''),
                    'fk_telf_telf_codi': request.data.get('codigo_telefono', None),
                    'fk_telf_clie_juri': cliente_juridico_instance.clie_juri_id,
                    }
                
                telefono_data_serializer = TelefonoGeneralClienteJuriSerializer(data=telefono_data)
                telefono_data_serializer.is_valid(raise_exception=True)
                telefono_data_serializer.save()
                
                codigo_autogenerado = secrets.token_hex(4)[:8].upper()
            
                while True:
                    if AfiliadoCodigo.objects.filter(afil_codigo_codigo=codigo_autogenerado).exists():
                        codigo_autogenerado = secrets.token_hex(4)[:8].upper()
                    else:
                        break
            
                afiliado_data={
                'fk_afil_clie_juri':cliente_juridico_instance.clie_juri_id,
                'afil_codigo_codigo':codigo_autogenerado,
                 }
            
                afiliado_data_serializer = NumeroAfiliacionJuriSerializer(data=afiliado_data)
                afiliado_data_serializer.is_valid(raise_exception=True)
                afiliado_data_serializer.save()
                
                puntos_data={
                'fk_punt_clie_juri':cliente_juridico_instance.clie_juri_id,
                'punt_tiene_puntos':True,
                }
                puntos_data_serializer=PuntosJuriSerializer(data=puntos_data)
                puntos_data_serializer.is_valid(raise_exception=True)
                puntos_data_serializer.save()
                
                refresh = RefreshToken.for_user(usuario_instance)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                
                return Response({'access':access_token,'refresh':refresh_token}, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                transaction.savepoint_rollback(sid)
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            
    
class TelefonoClienteJuridicoViewSet(ModelViewSet):
    serializer_class = TelefonoPostClienteJuriSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Telefono.objects.filter(fk_telf_clie_juri__clie_juri_id=self.request.user.fk_usua_clie_juri.clie_juri_id)
    def get_serializer_context(self):
        return {'telf_clie_juri_id': self.request.user.fk_usua_clie_juri.clie_juri_id}
    
    
    
class LugarViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    serializer_class = LugarGetSerializer
    queryset = Lugar.objects.all()

    def list(self, request, *args, **kwargs):
        tipo_lugar = request.query_params.get('tipo_lugar')
        lugar_id = request.query_params.get('lugar_id')

        if tipo_lugar == 'estado':
            queryset = self.queryset.filter(lugar_tipo='estado')
        elif tipo_lugar == 'municipio':
            queryset = self.queryset.filter(lugar_tipo='municipio', fk_lugar_lugar__lugar_id=lugar_id)
        elif tipo_lugar == 'parroquia':
            queryset = self.queryset.filter(lugar_tipo='parroquia', fk_lugar_lugar__lugar_id=lugar_id)
        else:
            queryset = self.queryset

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  
    
    
class TipoComercioViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    serializer_class = TipoComercioGetSerializer
    queryset = TipoComercio.objects.all()
    
    
    def get_serializer_context(self):
        return {'request': self.request}
    

class TelefonoCodigoViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    serializer_class =TelefonoCodigoGetSerializer
    queryset = TelefonoCodigo.objects.all()
    
    def get_serializer_context(self):
        return {'request': self.request}
    
class ProvedorFiltroViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    serializer_class = ProvedorFiltroSerializer
    queryset = Proveedor.objects.all()
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    
    
    
    
    
class TipoRonFiltroViewSet(ModelViewSet):
    permission_classes = [IsReadOnly]
    serializer_class = TipoRonFiltroSerializer
    queryset = TipoRon.objects.all()
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    
    
class ClienteNaturalEmpleadoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClienteNaturalSerializer
    queryset = ClienteNatural.objects.all()
   
    def get_serializer_class(self):
        method=self.request.method
        if self.request.user.fk_usua_empl:
            if method=='GET':
                return ClienteNaturalSerializer
            elif method=='POST':
                return ClienteNaturalFormSerializer
            else :
                return ClienteNaturalFormSerializer
        else :
            raise PermissionDenied("ACCESO DENEGADO")
    
    def get_queryset(self):
        cedula_param=self.request.query_params.get('cedula')
        usuario=self.request.user
        

        if usuario.fk_usua_empl:
            queryset = ClienteNatural.objects.all()
            if cedula_param:
                queryset = queryset.filter(clie_natu_cedula_identidad=cedula_param)
            
            return queryset
        
        else:
            return ClienteNatural.objects.none()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            sid = transaction.savepoint()
            cliente_natural_data = {
                'clie_natu_rif': request.data.get('clie_natu_rif', ''),
                'clie_natu_cedula_identidad': request.data.get('clie_natu_cedula_identidad', ''),
                'clie_natu_nombre': request.data.get('clie_natu_nombre', ''),
                'clie_natu_apellido': request.data.get('clie_natu_apellido', ''),
                'clie_natu_segundo_nombre': request.data.get('clie_natu_segundo_nombre', ''),
                'clie_natu_segundo_apellido': request.data.get('clie_natu_segundo_apellido', ''),
                'clie_natu_direccion_habitacion': request.data.get('clie_natu_direccion_habitacion', ''),
                'fk_clie_natu_lugar': request.data.get('fk_clie_natu_lugar', None),
            }

            cliente_natural_serializer = ClienteNaturalPostSerializer(data=cliente_natural_data)
            cliente_natural_serializer.is_valid(raise_exception=True)
            cliente_natural_instance = cliente_natural_serializer.save()

            random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))    
            
            usuario_data = {
                'username': request.data.get('username', ''),
                'password': random_password,
                'email': request.data.get('email', ''),
                'fk_usua_clie_natu': cliente_natural_instance.clie_natu_id,
            }

            usuario_serializer = UserCreateSerializer(data=usuario_data)
            usuario_serializer.is_valid(raise_exception=True)
            usuario_instance=usuario_serializer.save()
            
            telefono_data=  {
                'telf_numero': request.data.get('telefono', ''),
                'fk_telf_telf_codi': request.data.get('codigo_telefono', None),
                'fk_telf_clie_natu': cliente_natural_instance.clie_natu_id,
            }
            
            telefono_data_serializer = TelefonoGeneralClienteNatuSerializer(data=telefono_data)
            telefono_data_serializer.is_valid(raise_exception=True)
            telefono_data_serializer.save()
            
            codigo_autogenerado = secrets.token_hex(4)[:8].upper()
            
            while True:
                if AfiliadoCodigo.objects.filter(afil_codigo_codigo=codigo_autogenerado).exists():
                    codigo_autogenerado = secrets.token_hex(4)[:8].upper()
                else:
                    break
            
            afiliado_data={
                'fk_afil_clie_natu':cliente_natural_instance.clie_natu_id,
                'afil_codigo_codigo':codigo_autogenerado,
            }
            
            afiliado_data_serializer = NumeroAfiliacionNatuSerializer(data=afiliado_data)
            afiliado_data_serializer.is_valid(raise_exception=True)
            afiliado_data_serializer.save()
            
            puntos_data={
                'fk_punt_clie_natu':cliente_natural_instance.clie_natu_id,
                'punt_tiene_puntos':True,
            }
            puntos_data_serializer=PuntosNatuSerializer(data=puntos_data)
            puntos_data_serializer.is_valid(raise_exception=True)
            puntos_data_serializer.save()
            
            data=cliente_natural_serializer.data
            transaction.savepoint_commit(sid)
            enviar_correo(usuario_instance.username,random_password,usuario_instance.email)
            return Response(data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    def get_serializer_context(self):
        return {'request': self.request}
    
    
    
    
class ClienteJuridicoEmpleadoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ClienteJuridico.objects.all()
   
    def get_serializer_class(self):
        method=self.request.method
        if self.request.user.fk_usua_empl:
            if method=='GET':
                return ClienteJuridicoSerializer
            elif method=='POST':
                return ClienteJuridicoFormSerializer
            else :
                return ClienteJuridicoFormSerializer
        else: 
            raise PermissionDenied("ACCESO DENEGADO")
        
    
    def get_queryset(self):
        rif_param=self.request.query_params.get('rif')
        usuario=self.request.user
        
        if usuario.fk_usua_empl:
            queryset = ClienteJuridico.objects.all()
            if rif_param:
                queryset = queryset.filter(clie_juri_rif=rif_param)
            
            return queryset
                    
        else:
            return ClienteJuridico.objects.none()
        
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            sid=transaction.savepoint()
            cliente_juridico_data = {
                    'clie_juri_rif': request.data.get('clie_juri_rif', ''),
                    'clie_juri_denominacion_comercial': request.data.get('clie_juri_denominacion_comercial', ''),
                    'clie_juri_razon_social': request.data.get('clie_juri_razon_social', ''),
                    'clie_juri_pagina_web': request.data.get('clie_juri_pagina_web', ''),
                    'clie_juri_capital_disponible': request.data.get('clie_juri_capital_disponible', ''),
                    'clie_juri_direccion_fisica': request.data.get('clie_juri_direccion_fisica', ''),
                    'clie_juri_direccion_fiscal': request.data.get('clie_juri_direccion_fiscal', ''),
                    'fk_clie_juri_tipo_come': request.data.get('fk_clie_juri_tipo_come', None),
                    'fk_clie_juri_lugar_fisica': request.data.get('fk_clie_juri_lugar_fisica', None),
                    'fk_clie_juri_lugar_fiscal': request.data.get('fk_clie_juri_lugar_fiscal', None),
            }
                
            cliente_juridico_serializer = ClienteJuridicoPostSerializer(data=cliente_juridico_data)
            cliente_juridico_serializer.is_valid(raise_exception=True)
            cliente_juridico_instance = cliente_juridico_serializer.save()
            random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))    
            
            usuario_data = {
                    'username': request.data.get('username', ''),
                    'password':random_password,
                    'email': request.data.get('email', ''),
                    'fk_usua_clie_juri': cliente_juridico_instance.clie_juri_id,
            }
                
            usuario_serializer = UserCreateSerializer(data=usuario_data)
            usuario_serializer.is_valid(raise_exception=True)
            usuario_instance= usuario_serializer.save()
                
            telefono_data = {
                    'telf_numero': request.data.get('telefono', ''),
                    'fk_telf_telf_codi': request.data.get('codigo_telefono', None),
                    'fk_telf_clie_juri': cliente_juridico_instance.clie_juri_id,
                }
                
            telefono_data_serializer = TelefonoGeneralClienteJuriSerializer(data=telefono_data)
            telefono_data_serializer.is_valid(raise_exception=True)
            telefono_data_serializer.save()
                
            codigo_autogenerado = secrets.token_hex(4)[:8].upper()
            
            while True:
                if AfiliadoCodigo.objects.filter(afil_codigo_codigo=codigo_autogenerado).exists():
                    codigo_autogenerado = secrets.token_hex(4)[:8].upper()
                else:
                    break
            
            afiliado_data={
            'fk_afil_clie_juri':cliente_juridico_instance.clie_juri_id,
            'afil_codigo_codigo':codigo_autogenerado,
                }
            
            afiliado_data_serializer = NumeroAfiliacionJuriSerializer(data=afiliado_data)
            afiliado_data_serializer.is_valid(raise_exception=True)
            afiliado_data_serializer.save()
            
            puntos_data={
                'fk_punt_clie_juri':cliente_juridico_instance.clie_juri_id,
                'punt_tiene_puntos':True,
            }
            puntos_data_serializer=PuntosJuriSerializer(data=puntos_data)
            puntos_data_serializer.is_valid(raise_exception=True)
            puntos_data_serializer.save()
            
            
            data=cliente_juridico_serializer.data
            transaction.savepoint_commit(sid)
            enviar_correo(usuario_instance.username,random_password,usuario_instance.email)
            return Response(data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_serializer_context(self):
        return {'request': self.request}
    
class CarnetViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,IsReadOnly]
    serializer_class = CarnetNatuSerializer
    
    def get_serializer_class(self):
        if self.request.user.fk_usua_clie_natu:
            return CarnetNatuSerializer
        elif self.request.user.fk_usua_clie_juri:
            return CarnetJuriSerializer
        else:
            raise PermissionDenied("ACCESO DENEGADO")
        
    
    def get_queryset(self):
        caracas_timezone = pytz.timezone('America/Caracas')
        now_caracas=timezone.now().astimezone(caracas_timezone)
        
        usuario=self.request.user
        if usuario.is_authenticated and (usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri):
            if usuario.fk_usua_clie_natu and AfiliadoClienteProveedor.objects.filter(fk_afil_clie_prov_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id,afil_clie_prov_fecha_vencimiento__gte=now_caracas.date()).exists():
                queryset=ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id)
                return queryset
            elif usuario.fk_usua_clie_juri and AfiliadoClienteProveedor.objects.filter(fk_afil_clie_prov_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id,afil_clie_prov_fecha_vencimiento__gte=now_caracas.date()).exists():
                queryset=ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id)
                return queryset      
            else:
                return PermissionDenied("ACCESO DENEGADO")
        else:
            return PermissionDenied("ACCESO DENEGADO")
    
    @action(detail=False, methods=['get'])
    def pdf(self, request):
        persona = self.get_queryset().first()
        serializer = self.get_serializer(persona)
        carnet = serializer.data
        
        
        if carnet.get('clie_natu_cedula_identidad'):
            cedula = carnet.get('clie_natu_cedula_identidad',[0])
            nombre= carnet.get('clie_natu_nombre',[0])
            apellido= carnet.get('clie_natu_apellido',[0])
            codigo_carnet = carnet.get('codigo_carnet', [])
            codigo=codigo_carnet[0].get('afil_codigo_codigo')
            
        elif carnet.get('clie_juri_rif'):
            cedula = carnet.get('clie_juri_rif',[0])
            nombre= carnet.get('clie_juri_denominacion_comercial',[0])
            apellido=''
            codigo_carnet=carnet.get('codigo_carnet', [])
            codigo=codigo_carnet[0].get('afil_codigo_codigo')
            
        qr= qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5
        )
        back_ground_path = 'images/carnet.png'
        
        qr.add_data(cedula)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#FDD08D", back_color="#31212B")
        img_rgba=PILImage.alpha_composite(PILImage.new('RGBA', img.size, (255,255,255,0)), img.convert('RGBA'))
       
        
        
        background_image = ImageReader(back_ground_path)
      
        
        pdf_bytes = BytesIO()
        pdf = canvas.Canvas(pdf_bytes, pagesize=(200, 100))
        
        
        pdf.drawImage(background_image, 0, 0, width=200, height=100, preserveAspectRatio=False, anchor='c')
        pdf.drawInlineImage(img_rgba, 130, 35, width=70, height=70, preserveAspectRatio=False, anchor='c')
        pdf.setFont('Helvetica-Bold', 5)
        pdf.setFillColor(colors.white)
        pdf.drawString(10, 10, 'N°{}'.format(codigo))
        pdf.drawString(150, 10, '{}'.format(nombre + ' ' + apellido))
        pdf.drawString(170, 20, '{}'.format(cedula))
        
        
        pdf.showPage()
        pdf.save()
        
        pdf_bytes.seek(0)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="carnet.pdf"'
        return response
    
    @action(detail=False, methods=['get'])
    def image(self, request):
        persona = self.get_queryset().first()
        serializer = self.get_serializer(persona)
        carnet = serializer.data

        if carnet.get('clie_natu_cedula_identidad'):
            cedula = carnet.get('clie_natu_cedula_identidad', [0])
            nombre = carnet.get('clie_natu_nombre', [0])
            apellido = carnet.get('clie_natu_apellido', [0])
            codigo_carnet = carnet.get('codigo_carnet', [])
            codigo = codigo_carnet[0].get('afil_codigo_codigo')

        elif carnet.get('clie_juri_rif'):
            cedula = carnet.get('clie_juri_rif', [0])
            nombre = carnet.get('clie_juri_denominacion_comercial', [0])
            apellido = ''
            codigo_carnet = carnet.get('codigo_carnet', [])
            codigo = codigo_carnet[0].get('afil_codigo_codigo')

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5
        )
        
        qr.add_data(cedula)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#FDD08D", back_color="#31212B")
        img_rgba = PILImage.alpha_composite(PILImage.new('RGBA', img.size, (255, 255, 255, 0)), img.convert('RGBA'))

        background_image = PILImage.open('images/carnet.png')

        image = PILImage.new('RGBA', background_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        image.paste(background_image, (0, 0))
        img_rgba_resized = img_rgba.resize((1500, 1500))
        image.paste(img_rgba_resized, (3300, 200), img_rgba_resized)

        font_siz=200
        font=ImageFont.truetype('arial.ttf', font_siz)
        font_siz2=100
        font2=ImageFont.truetype('arial.ttf', font_siz2)
        draw.text((260, 2200), 'N°{}'.format(codigo), font=font, fill='white')
        draw.text((3000, 2200), '{}'.format(nombre + ' ' + apellido), font=font, fill='white')
        draw.text((4080, 2100), '{}'.format(cedula), font=font2, fill='white')

        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        response = HttpResponse(image_bytes, content_type='image/png')
        response['Content-Disposition'] = 'filename="carnet_image.png"'
        return response
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    
    
class CarritoViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    
    def get_serializer_class(self):
        method=self.request.method
        if method=='GET':
            return CarritoGetSerializer
        elif method=='POST':
            return CarritoCreateSerializer
        else:
            return CarritoCreateSerializer
    
    def get_queryset(self,*args,**kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                queryset=Carrito.objects.filter(fk_carr_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id,carri_comprado=False,carri_empleado=False)
                if  queryset.exists():
                    return queryset
                else:
                    nuevo_carrito_data={
                        'fk_carr_clie_natu': usuario.fk_usua_clie_natu.clie_natu_id,
                    }
                    nuevo_carrito_serializer=CarritoCreateSerializer(data=nuevo_carrito_data)
                    nuevo_carrito_serializer.is_valid(raise_exception=True)
                    carrito=nuevo_carrito_serializer.save()
                    return Carrito.objects.filter(carr_uuid=carrito.carr_uuid)
            elif usuario.fk_usua_clie_juri:
                queryset=Carrito.objects.filter(fk_carr_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id,carri_comprado=False,carri_empleado=False)
                if  queryset.exists():
                    return queryset
                else:
                    nuevo_carrito_data={
                        'fk_carr_clie_juri': usuario.fk_usua_clie_juri.clie_juri_id,
                    }
                    nuevo_carrito_serializer=CarritoCreateSerializer(data=nuevo_carrito_data)
                    nuevo_carrito_serializer.is_valid(raise_exception=True)
                    carrito=nuevo_carrito_serializer.save()
                    return Carrito.objects.filter(carr_uuid=carrito.carr_uuid)
            elif usuario.fk_usua_empl:
                queryset=Carrito.objects.filter(carri_comprado=False,carri_empleado=True,fk_carr_clie_emples=usuario.fk_usua_empl.empl_id)
                if queryset.exists():
                    return queryset
                else:
                    nuevo_carrito_data={
                        'fk_carr_clie_emples': usuario.fk_usua_empl.empl_id,
                        'carri_empleado': True,
                    }
                    nuevo_carrito_serializer=CarritoCreateSerializer(data=nuevo_carrito_data)
                    nuevo_carrito_serializer.is_valid(raise_exception=True)
                    carrito=nuevo_carrito_serializer.save()
                    return Carrito.objects.filter(carr_uuid=carrito.carr_uuid)
            
        else:
            return Response({'error': 'NO AUTENTICADO'}, status=status.HTTP_401_UNAUTHORIZED)
        

    def create(self, request, *args, **kwargs):
        return Response({'error': 'No se permite la creación'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def update(self, request, *args, **kwargs):
            return Response({'error': 'No se permite la actualización'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
            return Response({'error': 'No se permite la eliminación'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    
class CarritoItemViewSet(ModelViewSet):
    def get_serializer_class(self):
        method=self.request.method
        if method=='POST' or method=='PUT':
            return CarritoItemPostSerializer
        else: 
            return CarritoItemSerializer
            
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                carritos_filtrados = Carrito.objects.filter(
                    fk_carr_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id,
                    carri_comprado=False,
                    carri_empleado=False
                )
                carritos_ids = carritos_filtrados.values_list('carr_id', flat=True)
                carrito_items = CarritoItem.objects.filter(fk_carri_item_carri__in=carritos_ids)
                return carrito_items
            
            elif usuario.fk_usua_clie_juri:
                carritos_filtrados = Carrito.objects.filter(
                    fk_carr_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id,
                    carri_comprado=False,
                    carri_empleado=False
                )
                carritos_ids = carritos_filtrados.values_list('carr_id', flat=True)
                carrito_items = CarritoItem.objects.filter(fk_carri_item_carri__in=carritos_ids)
                return carrito_items
            
            elif usuario.fk_usua_empl:
                carritos_filtrados = Carrito.objects.filter(
                    carri_comprado=False,
                    carri_empleado=True,
                    fk_carr_clie_emples=usuario.fk_usua_empl.empl_id
                )
                carritos_ids = carritos_filtrados.values_list('carr_id', flat=True)
                carrito_items = CarritoItem.objects.filter(fk_carri_item_carri__in=carritos_ids)
                return carrito_items
        else:
            return Response({'error': 'NO AUTENTICADO'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def create(self, request, *args, **kwargs):
        
        data_item={
            'carri_item_cantidad': request.data.get('carri_item_cantidad'),
            'fk_carri_item_inve_tiend': request.data.get('fk_carri_item_inve_tiend'),
            'fk_carri_item_ofer_ron': request.data.get('fk_carri_item_ofer_ron'),
            'fk_carri_item_entr_evento': request.data.get('fk_carri_item_entr_evento'),
            'fk_carri_item_afil': request.data.get('fk_carri_item_afil'),
            'carr_uuid': request.data.get('carr_uuid'),
        }
        serializado=CarritoItemPostSerializer(data=data_item)
        serializado.is_valid(raise_exception=True)
        serializado.save()
        
        response_data=CarritoItemSerializer(serializado.instance).data
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance_pk = response.data.get('carri_item_id') 
        updated_instance = CarritoItem.objects.get(pk=instance_pk)
        
        custom_serialized_data = CarritoItemSerializer(updated_instance).data
       
        return Response(custom_serialized_data, status=status.HTTP_200_OK)

class OfertaCarritoViewSet(ModelViewSet):
    serializer_class=OfertaBotellaVerSerializer
    permission_classes=[IsReadOnly]
    
    def get_queryset(self):
        botella_param=self.request.query_params.get('botella')
        
        caracas_timezone = pytz.timezone('America/Caracas')
        now_caracas=timezone.now().astimezone(caracas_timezone)
        queryset= OfertaBotella.objects.select_related('fk_ofer_bote_bote', 'fk_ofer_bote_ofer').filter(fk_ofer_bote_ofer__ofer_fecha_fin__gte=now_caracas.date())

        if botella_param:
            queryset=queryset.filter(fk_ofer_bote_bote__bote_id=botella_param)
        
        return queryset

class AfiliadoViewSet(ModelViewSet):
    serializer_class=AfiliadoGetSerializer
    permission_classes=[IsReadOnly]
    def get_queryset(self):
        return Afiliado.objects.all()
    

class TDCviewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    
    def get_serializer_class(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
               return TDCSerializer
            else:
                raise PermissionDenied("ACCESO DENEGADO")
        else:
            raise PermissionDenied("ACCESO DENEGADO")
    
    def get_queryset(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                return TarjetaCredito.objects.filter(fk_tdc_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id)
            elif usuario.fk_usua_clie_juri:
                return TarjetaCredito.objects.filter(fk_tdc_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id)
            else:
                return TarjetaCredito.objects.none()
        else:
            return TarjetaCredito.objects.none()
        
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                data={
                    'tdc_numero_tarjeta': request.data.get('tdc_numero_tarjeta'),
                    'tdc_cvv': request.data.get('tdc_cvv'),
                    'tdc_fecha_vencimiento': request.data.get('tdc_fecha_vencimiento'),
                    'tdc_nombre_titular': request.data.get('tdc_nombre_titular'),
                }
                context={'cliente':usuario}
                serializado=TDCSerializer(data=data,context=context)
                serializado.is_valid(raise_exception=True)
                serializado.save()
                return Response(serializado.data, status=status.HTTP_201_CREATED)
            elif usuario.fk_usua_clie_juri:
                data={
                    'tdc_numero_tarjeta': request.data.get('tdc_numero_tarjeta'),
                    'tdc_cvv': request.data.get('tdc_cvv'),
                    'tdc_nombre_titular': request.data.get('tdc_nombre_titular'),
                    'tdc_fecha_vencimiento': request.data.get('tdc_fecha_vencimiento'),
                }
                context={'cliente':usuario}
                serializado=TDCSerializer(data=data,context=context)
                serializado.is_valid(raise_exception=True)
                serializado.save()
                return Response(serializado.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'NO ERES CLIENTE'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'NO AUTENTICADO'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class ChequeViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    def get_serializer_class(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
               return ChequeSerializer
            else:
                raise PermissionDenied("ACCESO DENEGADO")
        else:
            raise PermissionDenied("ACCESO DENEGADO")
        
    def get_queryset(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                return Cheque.objects.filter(fk_cheq_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id)
            elif usuario.fk_usua_clie_juri:
                return Cheque.objects.filter(fk_cheq_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id)
            else:
                return Cheque.objects.none()
        else:
            return Cheque.objects.none()
        
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                data={
                    'cheq_numero_cheque': request.data.get('cheq_numero_cheque'),
                    'chq_nombre_titular': request.data.get('chq_nombre_titular'),
                    'cheq_banco': request.data.get('cheq_banco'),
                }
                context={'cliente':usuario}
                serializado=ChequeSerializer(data=data,context=context)
                serializado.is_valid(raise_exception=True)
                serializado.save()
                return Response(serializado.data, status=status.HTTP_201_CREATED)
            elif usuario.fk_usua_clie_juri:
                data={
                    'cheq_numero_cheque': request.data.get('cheq_numero_cheque'),
                    'chq_nombre_titular': request.data.get('chq_nombre_titular'),
                    'cheq_banco': request.data.get('cheq_banco'),
                }
                context={'cliente':usuario}
                serializado=ChequeSerializer(data=data,context=context)
                serializado.is_valid(raise_exception=True)
                serializado.save()
                return Response(serializado.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'NO ERES CLIENTE'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'NO AUTENTICADO'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class EfectivoViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    
    def get_serializer_class(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
               return EfectivoSerializer
            else:
                raise PermissionDenied("ACCESO DENEGADO")
        else:
            raise PermissionDenied("ACCESO DENEGADO")
    
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                data={
                    'efe_monto': request.data.get('efe_monto'),
                }
                context={'cliente':usuario}
                serializado=EfectivoSerializer(data=data,context=context)
                serializado.is_valid(raise_exception=True)
                serializado.save()
                return Response(serializado.data, status=status.HTTP_201_CREATED)
            elif usuario.fk_usua_clie_juri:
                data={
                    'efe_monto': request.data.get('efe_monto'),
                }
                context={'cliente':usuario}
                serializado=EfectivoSerializer(data=data,context=context)
                serializado.is_valid(raise_exception=True)
                serializado.save()
                return Response(serializado.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'NO ERES CLIENTE'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'NO AUTENTICADO'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def get_queryset(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                return Efectivo.objects.filter(fk_efe_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id)
            elif usuario.fk_usua_clie_juri:
                return Efectivo.objects.filter(fk_efe_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id)
            else:
                return Efectivo.objects.none()
        else:
            return Efectivo.objects.none()
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class HistoricoDolarViewSet(ModelViewSet):
    permission_classes=[IsReadOnly]
    serializer_class=HistoricoDolarSerializer
    def get_queryset(self):
        return HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True)
    
class HistoricoPuntoViewSet(ModelViewSet):
    permission_classes=[IsReadOnly]
    serializer_class=HistoricoPuntoSerializer
    def get_queryset(self):
        return HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True)
    

class VentaViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    
    def get_serializer_class(self):
        usuario=self.request.user
        method=self.request.method
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
               if method=='GET':
                   return VentaGetSimpleSerializer
               else:
                   return VentaOnlineSerializer
            elif usuario.fk_usua_empl:
                return VentaFisicaSerializer
        else:
            raise PermissionDenied("ACCESO DENEGADO")
    
    def get_queryset(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                carritos=Carrito.objects.filter(fk_carr_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id,carri_comprado=True)
                carritos_ids=carritos.values_list('carr_id',flat=True)
                return Venta.objects.filter(fk_vent_carri__in=carritos_ids)
            elif usuario.fk_usua_clie_juri:
                carritos=Carrito.objects.filter(fk_carr_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id,carri_comprado=True)
                carritos_ids=carritos.values_list('carr_id',flat=True)
                return Venta.objects.filter(fk_vent_carri__in=carritos_ids)
            elif usuario.is_superuser:
                return Venta.objects.all()
            else:
                return Venta.objects.none()
        else:
            return Venta.objects.none()

    
    @action(detail=True, methods=['get'])
    def pdf(self,request,*args,**kwargs):
        venta=self.get_object()
        serializer=VentaGetSerializer(venta)
        venta_data=serializer.data
        usuario=self.request.user
        
        
        if usuario.fk_usua_clie_natu:
            cedula=usuario.fk_usua_clie_natu.clie_natu_cedula_identidad
            nombre=usuario.fk_usua_clie_natu.clie_natu_nombre
            apellido=usuario.fk_usua_clie_natu.clie_natu_apellido
        elif usuario.fk_usua_clie_juri:
            cedula=usuario.fk_usua_clie_juri.clie_juri_rif
            nombre=usuario.fk_usua_clie_juri.clie_juri_denominacion_comercial
            apellido=''
            
        fecha_str=venta_data.get('vent_fecha_venta')
        
        objeto_fecha1 = datetime.fromisoformat(fecha_str[:-6]) 
        fecha_formateada1 = objeto_fecha1.strftime("%Y-%m-%d")
        
        formatted_fecha = fecha_formateada1
        
        total=venta_data.get('vent_monto_total')
        direccion=venta_data.get('venta_direccion')
        numero_factura=venta_data.get('vent_id')
        itenes=venta_data.get('itenes')
        
        
        back_ground_path = 'images/Factura.png'
        background_image = ImageReader(back_ground_path)
        pdf_bytes = BytesIO()
        width, height = background_image.getSize()
        pdf = canvas.Canvas(pdf_bytes, pagesize=(width, height))
        pdf.drawImage(background_image, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='c')
        
        pdf.setFont('Helvetica', 15)
        pdf.setFillColor(colors.black)
        pdf.drawString(280, 1351, '{}'.format(nombre + ' ' + apellido))
        pdf.drawString(905, 1351, '{}'.format(cedula))
        pdf.drawString(170, 1322, '{}'.format(direccion))
        pdf.drawString(1115, 1502, '{}'.format(numero_factura))
        pdf.setFont('Helvetica', 20)
        pdf.drawString(1080, 1526, '{}'.format(formatted_fecha))
        pdf.setFont('Helvetica', 25)
        pdf.drawString(1080,67, '{}'.format(total))
        
        table_data = [["", "", '', "", ""]]

        for item in itenes:
            for iten in item["iten"]:
                try:
                    if iten["fk_carri_item_inve_tiend"]:
                        producto_nombre = iten["fk_carri_item_inve_tiend"]["fk_inve_tiend_bote"]["bote_nombre"]
                    elif iten["fk_carri_item_entr_evento"]:
                        producto_nombre = iten["fk_carri_item_entr_evento"]["entr_envt_nombre"]
                    elif iten["fk_carri_item_afil"]:
                        producto_nombre = iten["fk_carri_item_afil"]["afil_nombre"]
                    else:
                        producto_nombre = ""

                    cantidad = iten["carri_item_cantidad"]
                    precio_unitario = round(iten["carri_item_precio"], 2)  
                    descuento = '00%'
                    if iten.get('fk_carri_item_ofer_ron'):
                         descuento = str(iten['fk_carri_item_ofer_ron'].get('ofer_bote_porcentaje', 0)) +'%'
                    total = iten["monto_total"]

                    table_data.append([producto_nombre, cantidad, precio_unitario, descuento, total])
                except KeyError as e:
                    print(f"KeyError: {e}")
                    print(f"Error in item: {iten}")
        
        table = Table(table_data, colWidths=[750,100,100,60,200])
        table.setStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ])

        table_height = table.wrapOn(pdf, width, height)[1]

# Set the starting y-coordinate accordingly
        start_y = height - 370 - table_height  # Adjust the distance from the top as needed

        # Draw the table at the calculated position
        table.drawOn(pdf, 70, start_y)
        pdf.showPage()
        pdf.save()

        pdf_bytes.seek(0)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="venta.pdf"'

        return response

    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            sid = transaction.savepoint() 
            usuario = self.request.user
            caracas = pytz.timezone('America/Caracas')
            now_caracas = timezone.now().astimezone(caracas)
            
            if not usuario.is_authenticated:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'NO AUTENTICADO'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if usuario.fk_usua_clie_natu:
                return self._create_natu(usuario, now_caracas, request,sid)
            
            if usuario.fk_usua_clie_juri:
                return self._create_juri(usuario, now_caracas, request,sid)
            
            if usuario.fk_usua_empl:
                return self._create_empleado(usuario, now_caracas, request,sid)
        
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _create_natu(self, usuario, now_caracas, request,sid):
        
        if AfiliadoClienteProveedor.objects.filter(fk_afil_clie_prov_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id, afil_clie_prov_fecha_vencimiento__gte=now_caracas.date()).exists():
            carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
            itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
            total = 0
            
            for iten in itenes:
                total += iten.carri_item_precio*iten.carri_item_cantidad
            pago_data_1={}
            pago_data_2={}
            total=round(total,2)
            data_venta = {
                'vent_fecha_venta': now_caracas,
                'venta_direccion': request.data.get('venta_direccion'),
                'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                'fk_vent_carri': carrito.carr_id,
                'vent_monto_total': total,
            }
            
            pago=0.0
            
            if float(request.data.get('cantidad_tarjeta'))>0:
                pago_data_1={
                    'fk_pago_tdc':request.data.get('tarjeta_id'),
                    'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                
                pago=pago+float(request.data.get('cantidad_tarjeta'))
            
            if float(request.data.get('cantidad_puntos'))  > 0:
                cliente=ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id).first()
                puntos=cliente.clie_natu_puntos
                
                if puntos<float(request.data.get('cantidad_puntos')):
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                
                pago_data_2={
                    'fk_pago_punt':request.data.get('puntos_id'),
                    'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id).update(clie_natu_puntos=puntos-float(request.data.get('cantidad_puntos')))
                puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
            
            
            
            if pago==total:
                carrito=Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                return self._save_venta(data_venta,pago_data_1,pago_data_2)
            
            elif pago>total:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif pago<total:
                transaction.savepoint_rollback(sid)
                return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            pago_data_1={}
            pago_data_2={}
            
            carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
            itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
            control = False
            
            for iten in itenes:
                if iten.fk_carri_item_afil is not None:
                    primaria = iten.fk_carri_item_afil
                    control = True
            
            if control:
                data_afiliacion = {
                    'fk_afil_clie_prov_clie_natu': usuario.fk_usua_clie_natu.clie_natu_id,
                    'afil_clie_prov_fecha_afiliacion': now_caracas.date(),
                    'afil_clie_prov_fecha_vencimiento': now_caracas.date() + timedelta(days=30),
                    'fk_afil_clie_prov_afil': primaria.afil_id,
                }
                
                total = 0
                for iten in itenes:
                    total += iten.carri_item_precio*iten.carri_item_cantidad
                total=round(total,2)
                data_venta = {
                    'vent_fecha_venta': now_caracas,
                    'venta_direccion': request.data.get('venta_direccion'),
                    'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                    'fk_vent_carri': carrito.carr_id,
                    'vent_monto_total': total,
                }
                
                pago=0.0
            
                if float(request.data.get('cantidad_tarjeta'))>0:
                    pago_data_1={
                        'fk_pago_tdc':request.data.get('tarjeta_id'),
                        'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                        'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                        'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                    }
                    
                    pago=pago+float(request.data.get('cantidad_tarjeta'))
                
                if float(request.data.get('cantidad_puntos'))  > 0:
                    cliente=ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id).first()
                    puntos=cliente.clie_natu_puntos
                    if puntos<float(request.data.get('cantidad_puntos')):
                        transaction.savepoint_rollback(sid)
                        return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                    pago_data_2={
                        'fk_pago_punt':request.data.get('puntos_id'),
                        'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')),
                        'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                        'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                    }
                    ClienteNatural.objects.filter(clie_natu_id=usuario.fk_usua_clie_natu.clie_natu_id).update(clie_natu_puntos=puntos-float(request.data.get('cantidad_puntos')))
                    puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                    pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
                
                
                   
                if pago==total:
                    carrito=Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                    return self._save_afiliacion_venta(data_afiliacion,data_venta,pago_data_1,pago_data_2)
                
                elif pago>total:
                    transaction.savepoint_rollback(sid) 
                    return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
                
                elif pago<total:
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'NO TIENES AFILIACION, NI LA ESTAS PAGANDO'}, status=status.HTTP_400_BAD_REQUEST)
            
    def _create_juri(self, usuario, now_caracas, request,sid):
        if AfiliadoClienteProveedor.objects.filter(fk_afil_clie_prov_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id, afil_clie_prov_fecha_vencimiento__gte=now_caracas.date()).exists():
            carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
            itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
            total = 0
            
            for iten in itenes:
                total += iten.carri_item_precio*iten.carri_item_cantidad
            pago_data_1={}
            pago_data_2={}
            total=round(total,2)
            data_venta = {
                'vent_fecha_venta': now_caracas,
                'venta_direccion': request.data.get('venta_direccion'),
                'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                'fk_vent_carri': carrito.carr_id,
                'vent_monto_total': total,
            }
            
            pago=0.0
            
            if float(request.data.get('cantidad_tarjeta'))>0:
                
                pago_data_1={
                    'fk_pago_tdc':request.data.get('tarjeta_id'),
                    'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                
                pago=pago+float(request.data.get('cantidad_tarjeta'))
            
            if float(request.data.get('cantidad_puntos'))  > 0:
                cliente=ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id).first()
                puntos=cliente.clie_juri_puntos
                
                if puntos<float(request.data.get('cantidad_puntos')):
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                
                
                pago_data_2={
                    'fk_pago_punt':request.data.get('puntos_id'),
                    'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id).update(clie_juri_puntos=puntos-float(request.data.get('cantidad_puntos')))
                puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
            
            
            if pago==total:
                carrito=Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                return self._save_venta(data_venta,pago_data_1,pago_data_2)
            
            elif pago>total:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif pago<total:
                transaction.savepoint_rollback(sid)
                return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            pago_data_1={}
            pago_data_2={}
            
            carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
            itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
            control = False
            
            for iten in itenes:
                if iten.fk_carri_item_afil is not None:
                    primaria = iten.fk_carri_item_afil
                    control = True
            
            if control:
                data_afiliacion = {
                    'fk_afil_clie_prov_clie_juri': usuario.fk_usua_clie_juri.clie_juri_id,
                    'afil_clie_prov_fecha_afiliacion': now_caracas.date(),
                    'afil_clie_prov_fecha_vencimiento': now_caracas.date() + timedelta(days=30),
                    'fk_afil_clie_prov_afil': primaria.afil_id,
                }
                
                total = 0
                for iten in itenes:
                    total += iten.carri_item_precio*iten.carri_item_cantidad
                
                total=round(total,2)
                
                data_venta = {
                    'vent_fecha_venta': now_caracas,
                    'venta_direccion': request.data.get('venta_direccion'),
                    'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                    'fk_vent_carri': carrito.carr_id,
                    'vent_monto_total': total,
                }
                
                pago=0.0
            
                if float(request.data.get('cantidad_tarjeta'))>0:
                    pago_data_1={
                        'fk_pago_tdc':request.data.get('tarjeta_id'),
                        'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                        'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                        'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                    }
                    
                    pago=pago+float(request.data.get('cantidad_tarjeta'))
                
                if float(request.data.get('cantidad_puntos'))  > 0:
                    cliente=ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id).first()
                    puntos=cliente.clie_juri_puntos
                    
                    if puntos<float(request.data.get('cantidad_puntos')):
                        transaction.savepoint_rollback(sid)
                        return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    pago_data_2={
                        'fk_pago_punt':request.data.get('puntos_id'),
                        'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')),
                        'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                        'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                    }
                    ClienteJuridico.objects.filter(clie_juri_id=usuario.fk_usua_clie_juri.clie_juri_id).update(clie_juri_puntos=puntos-float(request.data.get('cantidad_puntos')))
                    
                    puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                    pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
                    
                if pago==total:
                    carrito=Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                    return self._save_afiliacion_venta(data_afiliacion,data_venta,pago_data_1,pago_data_2)
                
                elif pago>total:
                    transaction.savepoint_rollback(sid) 
                    return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
                
                elif pago<total:
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'NO TIENES AFILIACION, NI LA ESTAS PAGANDO'}, status=status.HTTP_400_BAD_REQUEST)
            
    def _create_empleado(self, usuario, now_caracas, request,sid):
        
        if request.data.get('usuario_natu') !="":
            return self.empl_natu(request.data.get('usuario_natu'),usuario,now_caracas,request,sid)
        elif request.data.get('usuario_juri') !="":
            print("juri")
            return self.emple_juri(request.data.get('usuario_juri'),usuario,now_caracas,request,sid)
        else:
            transaction.savepoint_rollback(sid) 
            return Response({'error': 'NO SE HA ENVIADO UN USUARIO'}, status=status.HTTP_400_BAD_REQUEST)
    
    def empl_juri_afiliacion(self, cliente,usuario,now_caracas,request,sid):     
        
        carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
        itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
        control = False
            
        for iten in itenes:
            if iten.fk_carri_item_afil is not None:
                primaria = iten.fk_carri_item_afil
                control = True

        if control:
            
            pago_data_1={}
            pago_data_2={}
            pago_data_3={}
            pago_data_4={}
            
            cliente_juri=ClienteJuridico.objects.filter(clie_juri_id=cliente).first()
            cliente_id=cliente_juri.clie_juri_id
            
            data_afiliacion = {
                    'fk_afil_clie_prov_clie_juri': cliente_id,
                    'afil_clie_prov_fecha_afiliacion': now_caracas.date(),
                    'afil_clie_prov_fecha_vencimiento': now_caracas.date() + timedelta(days=30),
                    'fk_afil_clie_prov_afil': primaria.afil_id,
            }
                
            total = 0
            total_puntos=0
            
            for iten in itenes:
                total += iten.carri_item_precio*iten.carri_item_cantidad
                total_puntos=total_puntos+iten.carri_item_cantidad
                 
            total=round(total,2)
            
            data_venta = {
                    'vent_fecha_venta': now_caracas,
                    'venta_direccion': request.data.get('venta_direccion'),
                    'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                    'fk_vent_carri': carrito.carr_id,
                    'vent_monto_total': total,
            }
            pago=0.0
            
            if float(request.data.get('cantidad_tarjeta'))>0:
                pago_data_1={
                    'pago_tipo_pago':'TDC',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
            
                pago=pago+float(request.data.get('cantidad_tarjeta'))
                
            if float(request.data.get('cantidad_puntos'))  > 0:
                cliente=ClienteJuridico.objects.filter(clie_juri_id=cliente_id).first()
                puntos=cliente.clie_juri_puntos
                
                if puntos<float(request.data.get('cantidad_puntos')): 
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                
                pago_data_2={
                    'pago_tipo_pago':'PUNTO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                ClienteJuridico.objects.filter(clie_juri_id=cliente_id).update(clie_juri_puntos=puntos-float(request.data.get('cantidad_puntos')))
                puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
                
            puntos_viejo=ClienteJuridico.objects.filter(clie_juri_id=cliente_id).first()
            puntos_viejo=puntos_viejo.clie_juri_puntos
            puntos_nuevo=puntos_viejo+total_puntos
            ClienteJuridico.objects.filter(clie_juri_id=cliente_id).update(clie_juri_puntos=puntos_nuevo)
            
            if float(request.data.get('cantidad_efectivo'))  > 0:
                pago_data_3={
                    'pago_tipo_pago':'EFECTIVO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_efectivo')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_efectivo'))
                
            if float(request.data.get('cantidad_cheque'))>0:
                pago_data_4={
                    'pago_tipo_pago':'CHEQUE',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_cheque')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_cheque'))
            
            if pago==total:
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(fk_carr_clie_juri=cliente_id)
                return self._save_afiliacion_venta_empleado(data_afiliacion,data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4)
                
            elif pago>total:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif pago<total:
                transaction.savepoint_rollback(sid)
                return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            transaction.savepoint_rollback(sid) 
            return Response({'error': 'NO TIENES AFILIACION, NI LA ESTAS PAGANDO'}, status=status.HTTP_400_BAD_REQUEST)
     
    def emple_juri(self,cliente,usuario,now_caracas,request,sid):
        cliente_juri=ClienteJuridico.objects.filter(clie_juri_id=cliente).first()
        cliente_id=cliente_juri.clie_juri_id
        
        if AfiliadoClienteProveedor.objects.filter(fk_afil_clie_prov_clie_juri=cliente_id, afil_clie_prov_fecha_vencimiento__gte=now_caracas.date()).exists():
            pago_data_1={}
            pago_data_2={}
            pago_data_3={}
            pago_data_4={}
            
            carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
            itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
            total = 0
            total_puntos=0
            
            for iten in itenes:
                total += iten.carri_item_precio*iten.carri_item_cantidad
                total_puntos=total_puntos+iten.carri_item_cantidad
                
            total=round(total,2)
            pago=0.0
            data_venta = {
                'vent_fecha_venta': now_caracas,
                'venta_direccion': request.data.get('venta_direccion'),
                'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                'fk_vent_carri': carrito.carr_id,
                'vent_monto_total': total,
                'venta_puntos':total_puntos,
            }
            
            if float(request.data.get('cantidad_tarjeta'))>0:
                pago_data_1={
                    'pago_tipo_pago':'TDC',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
            
                pago=pago+float(request.data.get('cantidad_tarjeta'))
                
            if float(request.data.get('cantidad_puntos'))  > 0:
                cliente=ClienteJuridico.objects.filter(clie_juri_id=cliente_id).first()
                puntos=cliente.clie_juri_puntos
                
                if puntos<float(request.data.get('cantidad_puntos')): 
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                
                pago_data_2={
                    'pago_tipo_pago':'PUNTO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                ClienteJuridico.objects.filter(clie_juri_id=cliente_id).update(clie_juri_puntos=puntos-float(request.data.get('cantidad_puntos')))
                puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
            
            puntos_viejo=ClienteJuridico.objects.filter(clie_juri_id=cliente_id).first()
            puntos_viejo=puntos_viejo.clie_juri_puntos
            puntos_nuevo=puntos_viejo+total_puntos
            ClienteJuridico.objects.filter(clie_juri_id=cliente_id).update(clie_juri_puntos=puntos_nuevo)
            
            if float(request.data.get('cantidad_efectivo'))  > 0:
                pago_data_3={
                    'pago_tipo_pago':'EFECTIVO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_efectivo')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_efectivo'))
                
            if float(request.data.get('cantidad_cheque'))>0:
                pago_data_4={
                    'pago_tipo_pago':'CHEQUE',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_cheque')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_cheque'))
            
            if pago==total:
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(fk_carr_clie_juri=cliente_id)
                return self._save_venta_empleado(data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4)
            
            elif pago>total:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif pago<total:
                transaction.savepoint_rollback(sid)
                return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
    
    
        else:
            return self.empl_juri_afiliacion(cliente,usuario,now_caracas,request,sid)
    
    
    
    def empl_natu(self,cliente,usuario,now_caracas,request,sid):
        cliente_natu=ClienteNatural.objects.filter(clie_natu_id=cliente).first()
        cliente_id=cliente_natu.clie_natu_id
        
        if AfiliadoClienteProveedor.objects.filter(fk_afil_clie_prov_clie_natu=cliente_id, afil_clie_prov_fecha_vencimiento__gte=now_caracas.date()).exists():
            pago_data_1={}
            pago_data_2={}
            pago_data_3={}
            pago_data_4={}
            
            carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
            itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
            total = 0
            total_puntos=0
            
            for iten in itenes:
                total += iten.carri_item_precio*iten.carri_item_cantidad
                total_puntos=total_puntos+iten.carri_item_cantidad
                
            total=round(total,2)
            
            data_venta = {
                'vent_fecha_venta': now_caracas,
                'venta_direccion': request.data.get('venta_direccion'),
                'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                'fk_vent_carri': carrito.carr_id,
                'vent_monto_total': total,
                'venta_puntos':total_puntos,
            }
            
            pago=0.0
            
            if float(request.data.get('cantidad_tarjeta'))>0:
                pago_data_1={
                    'pago_tipo_pago':'TDC',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
            
                pago=pago+float(request.data.get('cantidad_tarjeta'))
                
            if float(request.data.get('cantidad_puntos'))  > 0:
                cliente=ClienteNatural.objects.filter(clie_natu_id=cliente_id).first()
                puntos=cliente.clie_natu_puntos
                
                if puntos<float(request.data.get('cantidad_puntos')): 
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                
                pago_data_2={
                    'pago_tipo_pago':'PUNTO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                ClienteNatural.objects.filter(clie_natu_id=cliente_id).update(clie_natu_puntos=puntos-float(request.data.get('cantidad_puntos')))
                puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
            
            puntos_viejos=ClienteNatural.objects.filter(clie_natu_id=cliente_id).first()
            puntos_viejos=puntos_viejos.clie_natu_puntos
            
            puntos_nuevos=puntos_viejos+total_puntos
            ClienteNatural.objects.filter(clie_natu_id=cliente_id).update(clie_natu_puntos=puntos_nuevos)
            
            if float(request.data.get('cantidad_efectivo'))  > 0:
                pago_data_3={
                    'pago_tipo_pago':'EFECTIVO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_efectivo')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_efectivo'))
                
            if float(request.data.get('cantidad_cheque'))>0:
                pago_data_4={
                    'pago_tipo_pago':'CHEQUE',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_cheque')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_cheque'))
            
            if pago==total:
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(fk_carr_clie_natu=cliente_id)
                return self._save_venta_empleado(data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4)
            elif pago>total:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif pago<total:
                transaction.savepoint_rollback(sid)
                return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return self.empl_natu_afiliacion(cliente,usuario,now_caracas,request,sid)
      
             
    def empl_natu_afiliacion(self,cliente,usuario,now_caracas,request,sid):
        carrito = Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).first()
        itenes = CarritoItem.objects.filter(fk_carri_item_carri=carrito.carr_id).all()
        control = False
            
        for iten in itenes:
            if iten.fk_carri_item_afil is not None:
                primaria = iten.fk_carri_item_afil
                control = True

        if control:
            
            pago_data_1={}
            pago_data_2={}
            pago_data_3={}
            pago_data_4={}
            
            cliente_natu=ClienteNatural.objects.filter(clie_natu_id=cliente).first()
            cliente_id=cliente_natu.clie_natu_id
            
            data_afiliacion = {
                    'fk_afil_clie_prov_clie_natu': cliente_id,
                    'afil_clie_prov_fecha_afiliacion': now_caracas.date(),
                    'afil_clie_prov_fecha_vencimiento': now_caracas.date() + timedelta(days=30),
                    'fk_afil_clie_prov_afil': primaria.afil_id,
            }
                
            total = 0
            total_puntos=0
            
            for iten in itenes:
                total += iten.carri_item_precio*iten.carri_item_cantidad
                total_puntos=total_puntos+iten.carri_item_cantidad
                 
            total=round(total,2)
            
            data_venta = {
                    'vent_fecha_venta': now_caracas,
                    'venta_direccion': request.data.get('venta_direccion'),
                    'fk_vent_direccion': request.data.get('fk_vent_direccion'),
                    'fk_vent_carri': carrito.carr_id,
                    'vent_monto_total': total,
            }
            pago=0.0
            
            if float(request.data.get('cantidad_tarjeta'))>0:
                pago_data_1={
                    'pago_tipo_pago':'TDC',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_tarjeta')),
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
            
                pago=pago+float(request.data.get('cantidad_tarjeta'))
                
            if float(request.data.get('cantidad_puntos'))  > 0:
                cliente=ClienteNatural.objects.filter(clie_natu_id=cliente_id).first()
                puntos=cliente.clie_natu_puntos
                
                if puntos<float(request.data.get('cantidad_puntos')): 
                    transaction.savepoint_rollback(sid)
                    return Response({'error': 'NO TIENES SUFICIENTES PUNTOS'}, status=status.HTTP_400_BAD_REQUEST)
                
                pago_data_2={
                    'pago_tipo_pago':'PUNTO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_puntos')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                ClienteNatural.objects.filter(clie_natu_id=cliente_id).update(clie_natu_puntos=puntos-float(request.data.get('cantidad_puntos')))
                puntos_valor=HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first()
                pago=pago+float((request.data.get('cantidad_puntos')))*(puntos_valor.hist_punt_valor)
            
            puntos_viejos=ClienteNatural.objects.filter(clie_natu_id=cliente_id).first()
            puntos_viejos=puntos_viejos.clie_natu_puntos
            
            puntos_nuevos=puntos_viejos+total_puntos
            ClienteNatural.objects.filter(clie_natu_id=cliente_id).update(clie_natu_puntos=puntos_nuevos)
            
            
            if float(request.data.get('cantidad_efectivo'))  > 0:
                pago_data_3={
                    'pago_tipo_pago':'EFECTIVO',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_efectivo')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_efectivo'))
                
            if float(request.data.get('cantidad_cheque'))>0:
                pago_data_4={
                    'pago_tipo_pago':'CHEQUE',
                    'pago_cantidad_pagada':float(request.data.get('cantidad_cheque')), 
                    'fk_pago_hist_dolar':HistoricoDolar.objects.filter(hist_dolar_fecha_fin__isnull=True).first().hist_dolar_id,
                    'fk_pago_hist_punt':HistoricoPunto.objects.filter(hist_punt_fecha_fin__isnull=True).first().hist_punt_id, 
                }
                pago=pago+float(request.data.get('cantidad_cheque'))
            
            if pago==total:
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(carri_comprado=True)
                Carrito.objects.filter(carr_uuid=request.data.get('uuid_carrito')).update(fk_carr_clie_natu=cliente_id)
                return self._save_afiliacion_venta_empleado(data_afiliacion,data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4)
                
            elif pago>total:
                transaction.savepoint_rollback(sid) 
                return Response({'error': 'EL MONTO PAGADO ES MAYOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif pago<total:
                transaction.savepoint_rollback(sid)
                return Response({'error': 'EL MONTO PAGADO ES MENOR AL TOTAL'}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            transaction.savepoint_rollback(sid) 
            return Response({'error': 'NO TIENES AFILIACION, NI LA ESTAS PAGANDO'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def _save_afiliacion_venta_empleado(self,data_afiliacion,data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4):
        with transaction.atomic():
            afiliacion_serializado = AfiliadoClienteProveedorSerializer(data=data_afiliacion)
            afiliacion_serializado.is_valid(raise_exception=True)
            afiliacion_serializado.save()  
            return self._save_venta_empleado(data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4)
        
    
    def _save_venta_empleado(self,data_venta,pago_data_1,pago_data_2,pago_data_3,pago_data_4):
        serializado = VentaSerializer(data=data_venta)
        serializado.is_valid(raise_exception=True)
        serializado.save()
        
        if 'pago_cantidad_pagada' in pago_data_1:
            pago_data_1['fk_pago_vent']=serializado.instance.vent_id
            serializado_pago_1=PagoSerializer(data=pago_data_1)
            serializado_pago_1.is_valid(raise_exception=True)
            serializado_pago_1.save()
        
        if 'pago_cantidad_pagada' in pago_data_2:
            pago_data_2['fk_pago_vent']=serializado.instance.vent_id
            serializado_pago_2=PagoSerializer(data=pago_data_2)
            serializado_pago_2.is_valid(raise_exception=True)
            serializado_pago_2.save()
            
        if 'pago_cantidad_pagada' in pago_data_3:
            pago_data_3['fk_pago_vent']=serializado.instance.vent_id
            serializado_pago_3=PagoSerializer(data=pago_data_3)
            serializado_pago_3.is_valid(raise_exception=True)
            serializado_pago_3.save()
        
        if 'pago_cantidad_pagada' in pago_data_4:
            pago_data_4['fk_pago_vent']=serializado.instance.vent_id
            serializado_pago_4=PagoSerializer(data=pago_data_4)
            serializado_pago_4.is_valid(raise_exception=True)
            serializado_pago_4.save()
        
        status1_data={
            'venta_stat_status':True,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden Recibida').first().stat_pedi_id,
            'venta_stat_fecha_fin':serializado.instance.vent_fecha_venta,
        }
        
        status2_data={
            'venta_stat_status':False,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden Aprobada').first().stat_pedi_id,
        }
        
        status3_data={
            'venta_stat_status':False,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden En Camino').first().stat_pedi_id,
        }
        
        status4_data={
            'venta_stat_status':False,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden Entregada').first().stat_pedi_id,
        }
        
        serializado_status1=VentaStatusVentaSerializer(data=status1_data)
        serializado_status1.is_valid(raise_exception=True)
        serializado_status1.save()
        
        serializado_status2=VentaStatusVentaSerializer(data=status2_data)
        serializado_status2.is_valid(raise_exception=True)
        serializado_status2.save()
        
        serializado_status3=VentaStatusVentaSerializer(data=status3_data)
        serializado_status3.is_valid(raise_exception=True)
        serializado_status3.save()
        
        serializado_status4=VentaStatusVentaSerializer(data=status4_data)
        serializado_status4.is_valid(raise_exception=True)
        serializado_status4.save()
        
        carrito_id=serializado.instance.fk_vent_carri.carr_id
        self.restar_inventario(carrito_id)
        
        return Response(serializado.data, status=status.HTTP_201_CREATED)   
            
    
    
    def _save_venta(self, data_venta,pago_data_1,pago_data_2):
        serializado = VentaSerializer(data=data_venta)
        serializado.is_valid(raise_exception=True)
        serializado.save()
        
        
        if 'pago_cantidad_pagada' in pago_data_1:
            pago_data_1['fk_pago_vent']=serializado.instance.vent_id
            serializado_pago_1=PagoSerializer(data=pago_data_1)
            serializado_pago_1.is_valid(raise_exception=True)
            serializado_pago_1.save()
            
        if 'pago_cantidad_pagada' in pago_data_2:
            pago_data_2['fk_pago_vent']=serializado.instance.vent_id
            serializado_pago_2=PagoSerializer(data=pago_data_2)
            serializado_pago_2.is_valid(raise_exception=True)
            serializado_pago_2.save()
        
        status1_data={
            'venta_stat_status':True,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden Recibida').first().stat_pedi_id,
            'venta_stat_fecha_fin':serializado.instance.vent_fecha_venta,
        }
        
        status2_data={
            'venta_stat_status':False,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden Aprobada').first().stat_pedi_id,
        }
        
        status3_data={
            'venta_stat_status':False,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden En Camino').first().stat_pedi_id,
        }
        
        status4_data={
            'venta_stat_status':False,
            'fk_venta_stat_vent':serializado.instance.vent_id,
            'venta_stat_fecha_inicio':serializado.instance.vent_fecha_venta,
            'fk_venta_stat_stat_pedi':StatusPedido.objects.filter(stat_pedi_nombre__icontains='Orden Entregada').first().stat_pedi_id,
        }
        
        serializado_status1=VentaStatusVentaSerializer(data=status1_data)
        serializado_status1.is_valid(raise_exception=True)
        serializado_status1.save()
        
        serializado_status2=VentaStatusVentaSerializer(data=status2_data)
        serializado_status2.is_valid(raise_exception=True)
        serializado_status2.save()
        
        serializado_status3=VentaStatusVentaSerializer(data=status3_data)
        serializado_status3.is_valid(raise_exception=True)
        serializado_status3.save()
        
        serializado_status4=VentaStatusVentaSerializer(data=status4_data)
        serializado_status4.is_valid(raise_exception=True)
        serializado_status4.save()
        
        carrito_id=serializado.instance.fk_vent_carri.carr_id
        self.restar_inventario(carrito_id)
        
        return Response(serializado.data, status=status.HTTP_201_CREATED)

    def _save_afiliacion_venta(self, data_afiliacion, data_venta,pago_data_1=None,pago_data_2=None):
        with transaction.atomic():
            afiliacion_serializado = AfiliadoClienteProveedorSerializer(data=data_afiliacion)
            afiliacion_serializado.is_valid(raise_exception=True)
            afiliacion_serializado.save()  
            return self._save_venta(data_venta,pago_data_1,pago_data_2)

        
    def restar_inventario(self,carrito_id):
        cursor = connection.cursor()
        try:
            itenes=CarritoItem.objects.filter(fk_carri_item_carri=carrito_id).all()
            for iten in itenes:
                
                if iten.fk_carri_item_inve_tiend is not None:
                    cursor.callproc('restar_inventario_carrito', [iten.fk_carri_item_inve_tiend.inve_tiend_id, iten.carri_item_cantidad])
                    cursor.callproc('enviar_notificacion_empleado',[iten.fk_carri_item_inve_tiend.inve_tiend_id])
                elif iten.fk_carri_item_entr_evento is not None:
                    cursor.callproc('restar_entradas', [iten.fk_carri_item_entr_evento.entr_envt_id, iten.carri_item_cantidad])
                    
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class AfiliadoBooleanViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        usuario = self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
                return AfiliadoBooleanSerializer
            else:
                raise PermissionDenied("ACCESO DENEGADO")
        else:
            raise PermissionDenied("ACCESO DENEGADO")

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                return AfiliadoClienteProveedor.objects.filter(
                    fk_afil_clie_prov_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id,
                    afil_clie_prov_fecha_vencimiento__gte=timezone.now().date()
                )
            elif usuario.fk_usua_clie_juri:
                return AfiliadoClienteProveedor.objects.filter(
                    fk_afil_clie_prov_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id,
                    afil_clie_prov_fecha_vencimiento__gte=timezone.now().date()
                )
            else:
                return AfiliadoClienteProveedor.objects.none()
        else:
            return AfiliadoClienteProveedor.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            return Response({'afiliado':True}, status=status.HTTP_200_OK)
        else:
            return Response({'afiliado': False}, status=status.HTTP_200_OK)
        
        
class PuntoViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    
    def get_serializer_context(self):
        return {'usuario': self.request.user}
    
    def get_serializer_class(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu or usuario.fk_usua_clie_juri:
               return PuntoSerializer
            else:
                raise PermissionDenied("ACCESO DENEGADO")
        else:
            raise PermissionDenied("ACCESO DENEGADO")
        
    def get_queryset(self):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_clie_natu:
                return Puntos.objects.filter(fk_punt_clie_natu=usuario.fk_usua_clie_natu.clie_natu_id)
            elif usuario.fk_usua_clie_juri:
                return Puntos.objects.filter(fk_punt_clie_juri=usuario.fk_usua_clie_juri.clie_juri_id)
            else:
                return Puntos.objects.none()
        else:
            return Puntos.objects.none()
        
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def create(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    
from django.conf import settings       
class ReporteVentaViewSet(ModelViewSet):
    serializer_class=ReporteVentaSerializer
    permission_classes=[IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self, request, *args, **kwargs):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def get_queryset(self):
        return Venta.objects.none()
    
    
    def _pdf(self,itenes,fecha_inicio,fecha_fin,clasificacion,tipo):
        back_ground_path = 'images/ReporteN1.png'
        background_image = ImageReader(back_ground_path)
        pdf_bytes = BytesIO()
        width, height = background_image.getSize()
        pdf = canvas.Canvas(pdf_bytes, pagesize=(width, height))
        pdf.drawImage(background_image, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='c')
        categoria=ClasificacionRon.objects.filter(clasi_ron_id=clasificacion).first()
        categoria=categoria.clasi_ron_nombre
        tipo=TipoRon.objects.filter(tipo_ron_id=tipo).first()
        tipo=tipo.tipo_ron_nombre
        pdf.setFont("Helvetica", 16)
        pdf.drawString(125, 1330, tipo)
        pdf.drawString(195, 1358, categoria)
        pdf.drawString(1115, 1535, fecha_inicio)
        pdf.drawString(1105, 1510, fecha_fin)
        
        table_data = [[""]]
    
        for item in itenes:
            nombre_producto=item[0]
            table_data.append([nombre_producto])
            
        
        table = Table(table_data, colWidths=[750])
        table.setStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ])

        table_height = table.wrapOn(pdf, width, height)[1]
        start_y = height - 370 - table_height  
        table.drawOn(pdf, 70, start_y)
        pdf.showPage()
        pdf.save()
        pdf_bytes.seek(0)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Reporte-Venta.pdf"'

        return response
    
    
    
    def _reporte_venta(self,request):
        fecha_inicio=request.data.get('fecha_inicio')
        fecha_fin=request.data.get('fecha_fin')
        categoria=request.data.get('categoria')
        tipo_ron=request.data.get('tipo_ron')
        
        settings.USE_TZ = False
        fecha_actual=timezone.now().date()

        fecha_fin_str=str(fecha_fin)
        fecha_inicio_str=str(fecha_inicio)
        fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')
        
        
        if fecha_fin_str==fecha_inicio_str:
            ventas=Venta.objects.filter(vent_fecha_venta__date=fecha_inicio).all()
        else:
            if fecha_fin_str == fecha_actual_str:
                fecha_mayor=fecha_actual+timedelta(days=1)
                ventas = Venta.objects.filter(
                    vent_fecha_venta__range=[fecha_inicio, fecha_mayor],
                ).all()
            else:
                fecha_mayor=fecha_actual+timedelta(days=1)
                ventas = Venta.objects.filter(
                    vent_fecha_venta__range=[fecha_inicio, fecha_mayor]
                ).all()
            
        nombres_botellas_unicos = set()
        
        for venta in ventas:
            carrito=venta.fk_vent_carri
            todos_los_items=CarritoItem.objects.filter(fk_carri_item_carri=carrito,
                                                       fk_carri_item_inve_tiend__fk_inve_tiend_bote__fk_bote_ron__fk_ron_clasi_tipo__fk_clasi_tipo_clasi_ron__clasi_ron_id=categoria,
                                                       fk_carri_item_inve_tiend__fk_inve_tiend_bote__fk_bote_ron__fk_ron_clasi_tipo__fk_clasi_tipo_tipo_ron__tipo_ron_id=tipo_ron)\
                                                        .values_list('fk_carri_item_inve_tiend__fk_inve_tiend_bote__bote_nombre')
                                                        
            nombres_botellas_unicos.update(todos_los_items)                           
        
        itenes=list(nombres_botellas_unicos)
            
        settings.USE_TZ = True
        return self._pdf(itenes,fecha_inicio,fecha_fin,categoria,tipo_ron)
        
        
    
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.groups.filter(name='Gerente De ventas').exists() or usuario.is_superuser or usuario.is_staff:
                return self._reporte_venta(request)
            else:
                raise PermissionDenied("ACCESO DENEGADO")
        else:
            raise PermissionDenied("ACCESO DENEGADO")
        
class TopDiezParroquiasViewSet(ModelViewSet):

    serializer_class = ReporteDashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Lugar.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _top_diez_parroquias(self,fecha_inicio,fecha_fin):
        
        cursor=connection.cursor()
        try:
            cursor.callproc('top_10_parroquias_online',[fecha_inicio,fecha_fin])
            parroquias=cursor.fetchall()
            return Response(parroquias, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
    
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._top_diez_parroquias(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)

class TotalComprasViewSet(ModelViewSet):
    serializer_class=ReporteDashboardSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Venta.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _total_compras(self,fecha_inicio,fecha_fin):
            
            cursor=connection.cursor()
            try:
                cursor.callproc('total_compras',[fecha_inicio,fecha_fin])
                total=cursor.fetchall()
                return Response(total, status=status.HTTP_200_OK)
            except Exception as e:
                raise ValueError(f"Se ha producido un error: {e}")
            finally:
                cursor.close()
    
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._total_compras(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        
class ProductoMasVendidoViewSer(ModelViewSet):
    serializer_class=ReporteDashboardSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Venta.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _producto_mas_vendido(self,fecha_inicio,fecha_fin):
            
            cursor=connection.cursor()
            try:
                cursor.callproc('producto_mas_vendido',[fecha_inicio,fecha_fin])
                producto=cursor.fetchall()
                return Response(producto, status=status.HTTP_200_OK)
            except Exception as e:
                raise ValueError(f"Se ha producido un error: {e}")
            finally:
                cursor.close()
    
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._producto_mas_vendido(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)

class TotalOrdenStatusViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReporteDashboardSerializer
    
    def get_queryset(self):
        return StatusPedido.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _total_orden_status(self,fecha_inicio,fecha_fin): 
        cursor=connection.cursor()
        try:
            cursor.callproc('ordenes_status',[fecha_inicio,fecha_fin])
            statusos=cursor.fetchall()
            return Response(statusos, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
            
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._total_orden_status(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)

class TotalPuntosCajenadosViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReporteDashboardSerializer
    
    def get_queryset(self):
        return Puntos.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _total_puntos_cajenados(self,fecha_inicio,fecha_fin):
        cursor=connection.cursor()
        try:
            cursor.callproc('puntos_usados',[fecha_inicio,fecha_fin])
            puntos=cursor.fetchall()
            return Response(puntos, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
            
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._total_puntos_cajenados(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        
class TotalPuntosOtorgadosViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReporteDashboardSerializer
    
    def get_queryset(self):
        return Puntos.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _total_puntos_otorgados(self,fecha_inicio,fecha_fin):
        cursor=connection.cursor()
        try:
            cursor.callproc('puntos_otorgados',[fecha_inicio,fecha_fin])
            puntos=cursor.fetchall()
            return Response(puntos, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
            
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._total_puntos_otorgados(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)

class Top10ProductosFisicoViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReporteDashboardSerializer
    
    def get_queryset(self):
        return Venta.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _top_10_productos_fisico(self,fecha_inicio,fecha_fin):
        cursor=connection.cursor()
        try:
            cursor.callproc('productos_mas_vendidos_fisico',[fecha_inicio,fecha_fin])
            productos=cursor.fetchall()
            return Response(productos, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
            
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._top_10_productos_fisico(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
    
    
class ReporteOrdenesRetradasViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReporteDashboardSerializer
    
    def get_queryset(self):
        return Venta.objects.none()
    
    def update(self):
        return Response({"detail": "Updates are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self):
        return Response({"detail": "Deletes are not allowed for this resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def _reporte_ordenes_retrasadas(self,fecha_inicio,fecha_fin):
        cursor=connection.cursor()
        try:
            cursor.callproc('ordenes_retraso',[fecha_inicio,fecha_fin])
            ordenes=cursor.fetchall()
            return Response(ordenes, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValueError(f"Se ha producido un error: {e}")
        finally:
            cursor.close()
    
    def create(self, request, *args, **kwargs):
        usuario=self.request.user
        if usuario.is_authenticated:
            if usuario.fk_usua_empl:
                fecha_inicio=request.data.get('fecha_inicio')
                fecha_fin=request.data.get('fecha_fin')
                return self._reporte_ordenes_retrasadas(fecha_inicio,fecha_fin)
            else: 
                return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'NO TIENES PERMISOS'}, status=status.HTTP_400_BAD_REQUEST)
    