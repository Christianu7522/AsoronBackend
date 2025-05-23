import datetime
from io import BytesIO
import secrets
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import *
from django.utils.html import format_html
from django.forms import ModelForm
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from import_export import resources
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch   
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas



@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display=('ofer_id','ofer_nombre','ofer_fecha_inicio','ofer_fecha_fin')
    ordering=('ofer_id','ofer_fecha_inicio','ofer_fecha_fin')
    search_fields=('ofer_nombre',)
    list_per_page=10

class OfertaBotellaInline(admin.TabularInline):
    model = OfertaBotella
    extra=1


@admin.register(TipoTienda)
class TipoTiendaAdmin(admin.ModelAdmin):
    list_display=('tipo_tiend_id','tipo_tiend_nombre')
    search_fields=('tipo_tiend_nombre',)
    ordering=('tipo_tiend_nombre',)
    list_per_page = 10
@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display=('tiend_id','tiend_nombre','fk_tiend_tipo_tiend','fk_tiend_lugar')
    search_fields=('tiend_nombre',)
    ordering=('tiend_id','tiend_nombre','fk_tiend_tipo_tiend','fk_tiend_lugar')
    list_per_page=10


class HistoricoRonAdmin(admin.TabularInline):
    model=HistoricoRon
    
@admin.register(InventarioTienda)
class InventarioTiendaAdmin(admin.ModelAdmin):
    inlines=[HistoricoRonAdmin]
    list_display=('inve_tiend_id','inve_tiend_cantidad','fk_inve_tiend_bote','fk_inve_tiend_tiend')
    search_fields=('inve_tiend_cantidad','fk_inve_tiend_bote','fk_inve_tiend_tiend')
    ordering=('inve_tiend_cantidad','fk_inve_tiend_bote','fk_inve_tiend_tiend')
    list_per_page=10
    
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display=('depa_id','depa_nombre')
    search_fields=('depa_nombre',)
    ordering=('depa_nombre',)
    list_per_page = 10
    
@admin.register(TipoComercio)
class TipoComercioAdmin(admin.ModelAdmin):
    list_display=('tipo_comer_id','tipo_comer_nombre')
    search_fields=('tipo_comer_nombre',)
    ordering=('tipo_comer_nombre',)
    list_per_page = 10
@admin.register(TelefonoCodigo)
class TelefonoCodigoAdmin(admin.ModelAdmin):
    list_display=('telf_cod_id','telf_cod_codigo')
    search_fields=('telf_cod_codigo',)
    ordering=('telf_cod_codigo',)
    list_per_page = 10
   
class TelefonoForm(ModelForm):  
    class Meta:
        model = Telefono
        fields = 'fk_telf_telf_codi','telf_numero'
    

            
class TelefonoAdmin(admin.TabularInline):
    model=Telefono
    form=TelefonoForm
    addform=TelefonoForm
    
class RonImagenInline(admin.TabularInline):
    model = Imagen
    readonly_fields = ['Imagen']
    exclude=['fk_img_event']

    def Imagen(self, instance):
        if instance.img_url:
            return format_html(f'<img src="{instance.img_url.url}" '
                               f'style="max-height:100px; max-width:100px; object-fit: cover; '
                               f'filte:brightness(1.1);mix-blend-mode:multiply;"/>')
        return ''
     


@admin.register(MetodoDestilacion)
class MetodoDestilacionAdmin(admin.ModelAdmin):
    list_display=('meto_dest_id','meto_dest_nombre')
    search_fields=('meto_dest_nombre',)
    ordering=('meto_dest_nombre',)
    list_per_page = 10

class BarrilAnejamientoInlines(admin.TabularInline):
    model = BarrilAnejamiento
    
 
@admin.register(Anejamiento) 
class AnejamientoAdmin(admin.ModelAdmin):
    inlines=[BarrilAnejamientoInlines]
    list_display=('anej_id','anej_cantidad_anos','anej_calidad_agua')
    search_fields=('anej_cantidad_anos',)
    ordering=('anej_cantidad_anos',)
    list_per_page = 10
    
    
@admin.register(MetodoFermentacion)
class MetodoFermentacionAdmin(admin.ModelAdmin):
    list_display=('meto_ferm_id','meto_ferm_nombre')
    search_fields=('meto_ferm_nombre',)
    ordering=('meto_ferm_nombre',)
    list_per_page = 10
@admin.register(Barril)
class BarrilAdmin(admin.ModelAdmin):
    
    list_display=('barr_id','barr_calidad','barr_tipo','barr_tamano')
    search_fields=('barr_tamano',)
    ordering=('barr_tamano',)
    list_per_page = 10
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display=('color_id','color_nombre')
    search_fields=('color_nombre',)
    ordering=('color_nombre',)
    list_per_page = 10
@admin.register(GradoAlcohol)
class GradoAlcoholAdmin(admin.ModelAdmin):
    list_display=('grad_alco_id','grad_alco_porcentaje_alcohol')
    search_fields=('grad_alco_porcentaje_alcohol',)
    ordering=('grad_alco_porcentaje_alcohol',)
    list_per_page = 10
    
@admin.register(Sensacion)
class SensacionAdmin(admin.ModelAdmin):
    list_display=('sens_id','sens_nombre')
    search_fields=('sens_nombre',)
    ordering=('sens_nombre',)
    list_per_page = 10

@admin.register(ComoServir)
class ComoservirAdmin(admin.ModelAdmin):
    list_display=('como_serv_id','como_serv_nombre')
    search_fields=('como_serv_nombre',)
    ordering=('como_serv_nombre',)
    list_per_page = 10
    
class ComoServirRonInline(admin.TabularInline):
    model=ComoServirRon
    extra=1
class MateriaPrimaRonInline(admin.TabularInline):
    model=MateriaPrimaRon
    extra=1
class SensacionRonInline(admin.TabularInline):
    model = SensacionRon
    extra=1
    
@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display=('caja_id','caja_cantidad','caja_nombre')
    search_fields=('caja_nombre',)
    ordering=('caja_nombre','caja_cantidad')
    list_per_page = 10
    

@admin.register(Tapa)
class TapaAdmin(admin.ModelAdmin):
    list_display=('tapa_id','tapa_nombre')
    search_fields=('tapa_nombre',)
    ordering=('tapa_nombre',)
    list_per_page = 10
    
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display=('mate_id','mate_nombre')
    search_fields=('mate_nombre',)
    ordering=('mate_nombre',)
    list_per_page = 10
    
@admin.register(TapaMaterial)
class TapaMaterialAdmin(admin.ModelAdmin):
    list_display=('fk_tapa_mate_tapa','fk_tapa_mate_mate')
    search_fields=('fk_tapa_mate_tapa',)
    ordering=('fk_tapa_mate_tapa',)
    list_per_page = 10
    
@admin.register(TipoBotella) 
class TipoBotellaAdmin(admin.ModelAdmin):
    list_display=('tipo_bote_id','tipo_bote_capacidad')
    search_fields=('tipo_bote_capacidad',)
    ordering=('tipo_bote_capacidad',)
    list_per_page = 10
    
@admin.register(MaterialTipoBotella)
class MaterialTipoBotellaAdmin(admin.ModelAdmin):
    list_display=('fk_mate_tipo_bote_mate','fk_mate_tipo_bote_tipo_bote')
    search_fields=('fk_mate_tipo_bote_mate',)
    ordering=('fk_mate_tipo_bote_mate',)
    list_per_page = 10
    
@admin.register(Botella)
class BotellaAdmin(admin.ModelAdmin):
    inlines=[RonImagenInline,OfertaBotellaInline]
    list_display=('bote_id','bote_nombre')
    search_fields=('bote_nombre',)
    ordering=('bote_nombre',)
    list_per_page = 10

class CataEventoPremioRonInline(admin.TabularInline):
    model = CataEventoPremioRon
    extra=1
    

class RonRource(resources.ModelResource):
    class Meta:
        model=Ron


@admin.register(Ron)
class RonAdmin(ImportExportModelAdmin,ExportActionMixin,admin.ModelAdmin,):
    actions = ['exportar_a_pdf']
    resource_class =RonRource
    inlines = [ SensacionRonInline, MateriaPrimaRonInline,ComoServirRonInline,CataEventoPremioRonInline]
    
    
    def exportar_a_pdf(self, request, queryset):
        # Configura la respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ron_reporte.pdf"'

        # Configura la tabla con los datos de los objetos seleccionados
        data = [['ID', 'Nombre', 'Descripción', 'Clasificación y Tipo', 'Añejamiento', 'Grado Alcohol', 'Color', 'Proveedor', 'Origen']]
        for ron in queryset:
            data.append([
                str(ron.ron_id),
                str(ron.ron_nombre),
                str(ron.ron_descripcion),
                str(ron.fk_ron_clasi_tipo),
                str(ron.fk_ron_anej),
                str(ron.fk_ron_grado_alco),
                str(ron.fk_ron_color),
                str(ron.fk_ron_prove),
                str(ron.fk_ron_lugar),
            ])

        # Calcula el ancho de las columnas
        column_widths = [1 * inch, 2 * inch, 5 * inch, 2 * inch, 2 * inch, 2 * inch, 2 * inch, 2.5 * inch, 2.5 * inch]

        # Calcula el ancho total de la tabla
        table_width = sum(column_widths)

        # Configura el objeto PDF con el tamaño de la página igual al ancho de la tabla
        p = SimpleDocTemplate(response, pagesize=(table_width + 50, 1000))

        # Configura el estilo del encabezado
        style = getSampleStyleSheet()
        header_text = "Reporte de Ron"
        header = Paragraph(header_text, style['Heading1'])

        # Agrega el encabezado al documento
        elements = [header]

        # Crea la tabla y aplica estilos
        table = Table(data, colWidths=column_widths)

        # Configura el estilo de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPACEBEFORE', (0, 0), (-1, -1), 12),  # Agrega espacio antes de la tabla
        ])
        table.setStyle(table_style)

        # Agrega la tabla al documento
        elements.append(table)

        # Construye el documento
        p.build(elements)

        return response

    exportar_a_pdf.short_description = "Exportar seleccionado(s) a PDF"

    def header_footer(self, canvas, doc):
        # Esta función se llama en cada página, permite agregar encabezados y pies de página
        pass
    
    
    
    
    exportar_a_pdf.short_description = "Exportar seleccionado(s) a PDF"
    list_display=('ron_id','ron_nombre')
    search_fields=('ron_nombre',)
    ordering=('ron_nombre',)
    list_per_page = 10
    
    
@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display=('mate_prima_id','mate_prima_nombre')
    search_fields=('mate_prima_nombre',)
    ordering=('mate_prima_nombre',)
    list_per_page = 10
    
    
@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display=('lugar_id','lugar_tipo','lugar_nombre')
    search_fields=('lugar_nombre',)
    ordering=('lugar_nombre',)
    list_per_page = 10
    


@admin.register(TipoRon)
class TipoRonAdmin(admin.ModelAdmin):
    list_display=('tipo_ron_id','tipo_ron_nombre')
    search_fields=('tipo_ron_nombre',)
    ordering=('tipo_ron_nombre',)
    list_per_page = 10


@admin.register(ClasificacionRon)
class ClasificacionRonAdmin(admin.ModelAdmin):
    list_display=('clasi_ron_id','clasi_ron_nombre')
    search_fields=('clasi_ron_nombre',)
    ordering=('clasi_ron_nombre',)
    list_per_page = 10


@admin.register(ClasificacionTipo)
class ClasificacionTipoAdmin(admin.ModelAdmin):
    list_display=('clasi_tipo_id','fk_clasi_tipo_clasi_ron','fk_clasi_tipo_tipo_ron')
    ordering=('fk_clasi_tipo_clasi_ron','fk_clasi_tipo_tipo_ron')
    list_per_page = 10


class EventoImagenInline(admin.TabularInline):
    model = Imagen
    readonly_fields = ['Imagen']
    exclude=['fk_img_bote']

    def Imagen(self, instance):
        if instance.img_url:
            return format_html(f'<img src="{instance.img_url.url}" '
                               f'style="max-height:100px; max-width:100px; object-fit: cover; '
                               f'filte:brightness(1.1);mix-blend-mode:multiply;"/>')
        return ''
     
@admin.register(EntradaEvento)
class EntradaEventoAdmin(admin.ModelAdmin):
    list_display=('entr_envt_id','entr_envt_nombre','entr_envt_fecha_inicio','entr_envt_fecha_fin','fk_entr_envt_evento')
    ordering=('entr_envt_id','entr_envt_fecha_inicio','entr_envt_fecha_fin','fk_entr_envt_evento')
    search_fields=('entr_envt_nombre',)
    list_per_page=10
    
    
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    inlines=[EventoImagenInline]
    list_display=('event_id','event_nombre','event_fecha_ini','event_fecha_fin')
    ordering=('event_id','event_fecha_ini','event_fecha_fin')
    search_fields=('event_nombre',)
    list_per_page=10
    
@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    list_display=('prem_id','prem_nombre',)
    ordering=('prem_id','prem_nombre')
    search_fields=('prem_nombre',)
    list_per_page=10
    
@admin.register(NotaCata)
class NotaCataAdmin(admin.ModelAdmin):
    list_display=('nota_cata_id','nota_cata_nombre',)
    ordering=('nota_cata_id','nota_cata_nombre')
    list_per_page=10




class CorreoElectronicoAdmin(admin.TabularInline):
    model = CorreoElectronico

class AfiliadoProveAdmin(admin.TabularInline):
    model=AfiliadoClienteProveedor
    exclude=['fk_afil_clie_prov_clie_natu','fk_afil_clie_prov_clie_juri']
    extra=1
    
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    inlines=[CorreoElectronicoAdmin,TelefonoAdmin,AfiliadoProveAdmin]
    list_display=('prov_id','prov_rif','prov_denominacion_comercial','prov_razon_social')
    search_fields=('prov_denominacion_comercial',)
    ordering=('prov_rif',)
    list_per_page = 10
    
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        codigo_autogenerado = secrets.token_hex(4)[:8].upper()
        if not change:
            while True:
                if AfiliadoCodigo.objects.filter(afil_codigo_codigo=codigo_autogenerado).exists():
                        codigo_autogenerado = secrets.token_hex(4)[:8].upper()
                else:
                    break
                
            AfiliadoCodigo.objects.create(afil_codigo_codigo=codigo_autogenerado,fk_afil_prov=obj)
            
            suscripcion=Afiliado.objects.get(afil_nombre='Suscripcion Asoron')
            
            fecha_fin=datetime.datetime.now()+datetime.timedelta(days=365)
            
            AfiliadoClienteProveedor.objects.create(fk_afil_clie_prov_prov=obj,fk_afil_clie_prov_afil=suscripcion,afil_clie_prov_fecha_vencimiento=fecha_fin,afil_clie_prov_fecha_afiliacion=datetime.datetime.now())
                
           
        
   
class EmpleadoTiendaInline(admin.TabularInline):
    model=EmpleadoTienda
    extra=1
      
class AsistenciaEmpleadoInline(admin.TabularInline):
    model=Asistencia 
class HorarioEmpleadoInline(admin.TabularInline):
    model=HorarioEmpleado
    
class BeneficioEmpleadoInline(admin.TabularInline):
    model=BeneficioEmpleado
    
class CargoEmpleadoInline(admin.TabularInline):
    model=CargoEmpleado

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    actions = ['exportar_a_pdf']
    list_display=('noti_id','noti_asunto','noti_descripcion')
    search_fields=('noti_id',)
    ordering=('noti_id',)
    list_per_page = 10
   
    
    def exportar_a_pdf(self, request, queryset):
        
        notificacion=queryset.first()
        prov=notificacion.noti_id_prov
        tienda=notificacion.noti_id_tienda
        producto=notificacion.noti_id_pro
        
        proveedor=Proveedor.objects.get(prov_id=prov)
        tienda=Tienda.objects.get(tiend_id=tienda)
        producto=InventarioTienda.objects.get(inve_tiend_id=producto)
        
        nombre_proveedor=proveedor.prov_razon_social
        rif_proveedor=proveedor.prov_rif
        
        nombre_tienda=tienda.tiend_nombre
        direccion_tienda=tienda.tiend_dirrecion
        fecha_actual=datetime.datetime.now()
        formatted_fecha = fecha_actual.strftime('%Y-%m-%d %H:%M')
        
        nombre_producto=producto.fk_inve_tiend_bote.bote_nombre
        
        cantidad_comprar='500'
        
        back_ground_path = 'images/OrdenCompra.png'
        background_image = ImageReader(back_ground_path)
        pdf_bytes = BytesIO()
        width, height = background_image.getSize()
        pdf = canvas.Canvas(pdf_bytes, pagesize=(width, height))
        pdf.drawImage(background_image, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='c')
        
        pdf.setFont('Helvetica', 15)
        pdf.setFillColor(colors.black)
        pdf.drawString(280, 1351, '{}'.format(nombre_tienda ))
        pdf.drawString(905, 1351, '{}'.format(rif_proveedor))
        pdf.drawString(920, 1326, '{}'.format(nombre_proveedor))
        pdf.drawString(170, 1322, '{}'.format(direccion_tienda))
        pdf.setFont('Helvetica', 20)
        pdf.drawString(1080, 1526, '{}'.format(formatted_fecha))
        pdf.drawString(80, 1200, '{}'.format(nombre_producto))
        pdf.drawString(1100, 1200, '{}'.format(cantidad_comprar))
        
        pdf.showPage()
        pdf.save()

        pdf_bytes.seek(0)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="venta.pdf"'
        return response
    
    
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(fk_noti_empl=request.user.fk_usua_empl)
        return qs
    
    exportar_a_pdf.short_description = "Crear Orden De compra"
    
    
    
    

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    inlines=[TelefonoAdmin,HorarioEmpleadoInline,AsistenciaEmpleadoInline,BeneficioEmpleadoInline,CargoEmpleadoInline,EmpleadoTiendaInline]
    list_display=('empl_id','empl_cedula_identidad','empl_nombre','empl_apellido','empl_direccion','fk_empl_depa')
    search_fields=('empl_id','empl_cedula_identidad')
    ordering=('empl_id','empl_cedula_identidad')
    list_per_page = 10
    def get_queryset(self, request):
        # Filtra la consulta para que solo devuelva el perfil del empleado del usuario actual
        qs = super().get_queryset(request)
        if not request.user.is_superuser and not request.user.groups.filter(name='Recursos humanos').exists():
            qs = qs.filter(usuario__id=request.user.id)
        return qs
    
    
@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display=('vaca_id','vaca_fecha_inicio','vaca_fecha_fin')
    search_fields=('vaca_id',)
    ordering=('vaca_id',)
    list_per_page = 10
    
    
@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display=('hora_id','hora_dia','hora_hora_entrada','hora_hora_salida')
    search_fields=('hora_dia',)
    ordering=('hora_dia',)
    list_per_page = 10
    
@admin.register(Beneficio)   
class BeneficioAdmin(admin.ModelAdmin):
    list_display=('bene_id','bene_nombre')
    search_fields=('bene_nombre',)
    ordering=('bene_nombre',)
    list_per_page = 10
    
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display=('cargo_id','cargo_nombre')
    search_fields=('cargo_nombre',)
    ordering=('cargo_nombre',)
    list_per_page = 10
    






@admin.register(PersonaContacto)
class PersonaContactoAdmin(admin.ModelAdmin):
    inlines=[TelefonoAdmin]
    list_display=('pers_cont_id','pers_cont_nombre','pers_cont_apellido')
    search_fields=('pers_cont_nombre',)
    ordering=('pers_cont_nombre',)
    list_per_page = 10

class TdcJuriAdmin(admin.TabularInline):
    model=TarjetaCredito
    exclude=['fk_tdc_clie_natu']
    extra=1

class efecJuriAdmin(admin.TabularInline):
    model=Efectivo
    exclude=['fk_efe_clie_natu']
    extra=1

class chequeJuriAdmin(admin.TabularInline):
    model=Cheque
    exclude=['fk_cheq_clie_natu']
    extra=1
    
class puntosJuriAdmin(admin.TabularInline):
    model=Puntos
    exclude=['fk_punt_clie_natu']
    extra=1
    
class AfiliadoJuriAdmin(admin.TabularInline):
    model=AfiliadoClienteProveedor
    exclude=['fk_afil_clie_prov_clie_natu','fk_afil_clie_prov_prov']
    extra=1

@admin.register(ClienteJuridico)
class ClienteJuridicoAdmin(admin.ModelAdmin):
    inlines=[TelefonoAdmin,TdcJuriAdmin,efecJuriAdmin,chequeJuriAdmin,puntosJuriAdmin,AfiliadoJuriAdmin]
    list_display = ('clie_juri_razon_social','clie_juri_denominacion_comercial','clie_juri_rif','fk_clie_juri_tipo_come')
    search_fields = ('clie_juri_rif',)
    ordering = ('clie_juri_rif',)
    list_per_page = 10
    
    

class TdcNatuAdmin(admin.TabularInline):
    model=TarjetaCredito
    exclude=['fk_tdc_clie_juri']
    extra=1

class efecNatuAdmin(admin.TabularInline):
    model=Efectivo
    exclude=['fk_efe_clie_juri']
    extra=1

class chequeNatuAdmin(admin.TabularInline):
    model=Cheque
    exclude=['fk_cheq_clie_juri']
    extra=1
    
class puntosNatuAdmin(admin.TabularInline):
    model=Puntos
    exclude=['fk_punt_clie_juri']
    extra=1    

class AfiliadoNatuAdmin(admin.TabularInline):
    model=AfiliadoClienteProveedor
    exclude=['fk_afil_clie_prov_clie_juri','fk_afil_clie_prov_prov']
    extra=1
@admin.register(ClienteNatural)
class ClienteNaturalAdmin(admin.ModelAdmin):
    inlines=[TelefonoAdmin,TdcNatuAdmin,efecNatuAdmin,chequeNatuAdmin,puntosNatuAdmin,AfiliadoNatuAdmin]
    list_display=('clie_natu_nombre','clie_natu_apellido','clie_natu_cedula_identidad')
    search_fields=('clie_natu_cedula_identidad',)
    ordering=('clie_natu_cedula_identidad',)
    list_per_page = 10

class VentaStatusInline(admin.TabularInline):
    model=VentaStatus
    exclude=['fk_venta_stat_vent']
    extra=1
    

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    inlines=[VentaStatusInline]
    list_display=('compr_id','compr_fecha_compra','fk_compr_tiend','fk_compr_prove')
    search_fields=('compr_id',)
    ordering=('compr_id','fk_compr_tiend','fk_compr_prove')
    list_per_page = 10
    
@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display=('deta_compr_id','deta_compr_cantidad','deta_compr_precio','fk_deta_compr_bote','fk_deta_compr_compr')
    search_fields=('deta_compr_id',)
    ordering=('deta_compr_id','fk_deta_compr_bote','fk_deta_compr_compr')
    list_per_page = 10
    
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display=('carr_id','fk_carr_clie_natu','fk_carr_clie_juri')
    search_fields=('carr_id',)
    ordering=('carr_id','fk_carr_clie_natu','fk_carr_clie_juri')
    list_per_page = 10
    
@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display=('carri_item_id','carri_item_cantidad','fk_carri_item_inve_tiend','fk_carri_item_ofer_ron','fk_carri_item_entr_evento','fk_carri_item_afil','fk_carri_item_carri')
    search_fields=('carri_item_id',)
    ordering=('carri_item_id','carri_item_cantidad','fk_carri_item_inve_tiend','fk_carri_item_ofer_ron','fk_carri_item_entr_evento','fk_carri_item_afil','fk_carri_item_carri')
    list_per_page = 10
    
@admin.register(Afiliado)
class AfiliadoAdmin(admin.ModelAdmin):
    list_display=('afil_id','afil_nombre')
    search_fields=('afil_id',)
    ordering=('afil_id',)
    list_per_page = 10

@admin.register(HistoricoPunto)
class HistoricoPuntoAdmin(admin.ModelAdmin):
    list_display=('hist_punt_id','hist_punt_valor','hist_punt_fecha_inicio','hist_punt_fecha_fin')
    search_fields=('hist_punt_id',)
    ordering=('hist_punt_id','hist_punt_valor','hist_punt_fecha_inicio','hist_punt_fecha_fin')
    list_per_page = 10
    
@admin.register(HistoricoDolar)
class HistoricoDolarAdmin(admin.ModelAdmin):
    list_display=('hist_dolar_id','hist_dolar_valor','hist_dolar_fecha_inicio','hist_dolar_fecha_fin')
    search_fields=('hist_dolar_id',)
    ordering=('hist_dolar_id','hist_dolar_valor','hist_dolar_fecha_inicio','hist_dolar_fecha_fin')
    list_per_page = 10

class StatusVentaAdmin(admin.TabularInline):
    model=VentaStatus
    exclude=['fk_venta_stat_compr']
    extra=1
    
class PagoAdmin(admin.TabularInline):
    model=Pago
    extra=1
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines=[StatusVentaAdmin,PagoAdmin]
    list_display=('vent_id','vent_fecha_venta','vent_monto_total')
    search_fields=('vent_id',)
    ordering=('vent_id','vent_fecha_venta','vent_monto_total')
    list_per_page = 10
    
@admin.register(AfiliadoCodigo)
class AfiliadoCodigoAdmin(admin.ModelAdmin):
    readonly_fields=('afil_codigo_codigo','fk_afil_clie_juri','fk_afil_clie_natu','fk_afil_prov')
    list_display=('afil_codigo_id','afil_codigo_codigo')
    search_fields=('afil_codigo_id',)
    ordering=('afil_codigo_id',)
    list_per_page = 10