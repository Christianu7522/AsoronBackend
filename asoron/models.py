import uuid
from django.db import models
from .validators import validate_file_size as vak
from django.core.validators import MaxValueValidator, MinValueValidator,MinLengthValidator

# Create your models here.
class Ron(models.Model):
    ron_id=models.AutoField(primary_key=True,verbose_name='identificador')
    ron_nombre=models.CharField(max_length=50,verbose_name='Nombre')
    ron_descripcion=models.CharField(max_length=1000,verbose_name='Descripcion')
    fk_ron_clasi_tipo=models.ForeignKey('ClasificacionTipo',on_delete=models.CASCADE,verbose_name='Clasificacion y Tipo')
    fk_ron_anej=models.ForeignKey('Anejamiento',on_delete=models.CASCADE,related_name='ron_anejamiento',verbose_name='Añejamiento')
    fk_ron_grado_alco=models.ForeignKey('GradoAlcohol',on_delete=models.CASCADE,related_name='ron_grado_alcohol',verbose_name='Grado Alcohol')
    fk_ron_color=models.ForeignKey('Color',on_delete=models.CASCADE,related_name='ron_color',verbose_name='Color')
    fk_ron_prove=models.ForeignKey('Proveedor',on_delete=models.CASCADE,related_name='ron_proveedor',verbose_name='Proveedor')
    fk_ron_lugar=models.ForeignKey('Lugar',on_delete=models.CASCADE,related_name='ron_lugar',verbose_name='Origen',limit_choices_to={'lugar_tipo':'parroquia'})
    
    def __str__(self):
        return self.ron_nombre
    
    class Meta:
        verbose_name_plural = "Ron"
        
class Imagen(models.Model):
    img_id=models.AutoField(primary_key=True)
    img_url=models.ImageField(upload_to='asoron/',validators=[vak],verbose_name='Imagen URL')
    fk_img_event=models.ForeignKey('Evento',on_delete=models.CASCADE,null=True,blank=True,related_name='event_images')
    fk_img_bote=models.ForeignKey('Botella',on_delete=models.CASCADE,null=True,blank=True,related_name='bote_images')
    
    class Meta:
        verbose_name_plural = "Imagen"
class TipoRon(models.Model):
    tipo_ron_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tipo_ron_nombre=models.CharField(max_length=50,verbose_name='Nombre')
    
    def __str__(self):
        return self.tipo_ron_nombre
    
    class Meta:
        verbose_name_plural = "Tipo Ron"
    
class ClasificacionRon(models.Model):
    clasi_ron_id=models.AutoField(primary_key=True,verbose_name='identificador')
    clasi_ron_nombre=models.CharField(max_length=50,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.clasi_ron_nombre
    
    class Meta:
        verbose_name_plural = "Clasificacion Ron"
class ClasificacionTipo(models.Model):
    
    clasi_tipo_id=models.AutoField(primary_key=True,verbose_name='identificador')
    fk_clasi_tipo_clasi_ron=models.ForeignKey(ClasificacionRon, on_delete=models.CASCADE,related_name='clasi_tipo_ron',verbose_name='Clasificacion Ron')
    fk_clasi_tipo_tipo_ron=models.ForeignKey(TipoRon, on_delete=models.CASCADE,related_name='clasi_tipo_tipo_ron',verbose_name='Tipo Ron')
    
    def get_related_names(self):
        data = ClasificacionTipo.objects.filter(pk=self.pk).values('fk_clasi_tipo_clasi_ron__clasi_ron_nombre', 'fk_clasi_tipo_tipo_ron__tipo_ron_nombre').first()
        return data['fk_clasi_tipo_clasi_ron__clasi_ron_nombre'], data['fk_clasi_tipo_tipo_ron__tipo_ron_nombre']

    def __str__(self) -> str:
        clasi_name, tipo_name = self.get_related_names()
        return f"{clasi_name} {tipo_name}"
    
    
class MateriaPrima(models.Model):
    mate_prima_id=models.AutoField(primary_key=True,verbose_name='identificador')
    mate_prima_nombre=models.CharField(max_length=50,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.mate_prima_nombre
    
    class Meta:
        verbose_name_plural = "Materia Prima"
class MateriaPrimaRon(models.Model):
    mate_prima_ron_id=models.AutoField(primary_key=True)
    fk_mate_prima_ron_mate_prima=models.ForeignKey('MateriaPrima',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Materia Prima del Ron')
    fk_mate_prima_ron_ron=models.ForeignKey('Ron',on_delete=models.CASCADE,null=False,blank=False,related_name='mate_prima_ron_ron')
    
        
    def __str__(self) -> str:
        return self.fk_mate_prima_ron_mate_prima.mate_prima_nombre+" "+self.fk_mate_prima_ron_ron.ron_nombre

    class Meta:
        verbose_name_plural = "Materia Prima del Ron"
        unique_together = ('fk_mate_prima_ron_mate_prima', 'fk_mate_prima_ron_ron')


class Sensacion(models.Model):
    sens_id=models.AutoField(primary_key=True,verbose_name='identificador')
    sens_nombre=models.CharField(max_length=50,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.sens_nombre

    class Meta:
        verbose_name_plural = "Sensacion"
class SensacionRon(models.Model):
    sens_ron_id=models.AutoField(primary_key=True)
    fk_sens_ron_sens=models.ForeignKey('Sensacion',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Sensacion del ron')
    fk_sens_ron_ron=models.ForeignKey('Ron',on_delete=models.CASCADE,null=False,blank=False,related_name='sens_ron_ron')
        
    def __str__(self) -> str:
        return self.fk_sens_ron_sens.sens_nombre

    class Meta:
        verbose_name_plural = "Sensacion del Ron"
        unique_together = ('fk_sens_ron_sens', 'fk_sens_ron_ron')
        
class ComoServir(models.Model):
    como_serv_id=models.AutoField(primary_key=True,verbose_name='identificador')
    como_serv_nombre=models.CharField(max_length=50,verbose_name='Coctel')
    
    def __str__(self) -> str:
        return self.como_serv_nombre
    class Meta:
        verbose_name_plural = "Como Servir"
    
class ComoServirRon(models.Model):
    
    como_serv_ron_id=models.AutoField(primary_key=True)
    como_serv_ron_descripcion=models.CharField(max_length=200,verbose_name='Descripcion')
    fk_como_serv_ron_como_serv=models.ForeignKey('ComoServir',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Coctel')
    fk_como_serv_ron_ron=models.ForeignKey('Ron',on_delete=models.CASCADE,null=False,blank=False,related_name='como_serv_ron_ron')
    
    def __str__(self) -> str:
        return self.fk_como_serv_ron_como_serv.como_serv_nombre+" "+self.como_serv_ron_descripcion
    
    class Meta:
        verbose_name_plural = "Como Servir Ron"
        unique_together = ('fk_como_serv_ron_como_serv', 'fk_como_serv_ron_ron')
        
        
class GradoAlcohol(models.Model):
    grad_alco_id=models.AutoField(primary_key=True,verbose_name='identificador')
    grad_alco_porcentaje_alcohol=models.PositiveIntegerField(null=False,blank=False,verbose_name='Grado de alcohol')
    
    def __str__(self) -> str:
        return str(self.grad_alco_porcentaje_alcohol)+"°"
    
    class Meta:
        verbose_name_plural = "Grado Alcohol"
class Color(models.Model):
    color_id=models.AutoField(primary_key=True,verbose_name='identificador')
    color_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    color_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion')
    
    def __str__(self) -> str:
        return self.color_nombre +" "+self.color_descripcion
    
    class Meta:
        verbose_name_plural = "Color"
class Anejamiento(models.Model):
    BUENA='Buena'
    REGULAR='Regular'
    MALA='Mala'
        
    CALIDAD_AGUA=[
        (BUENA,'Buena'),
        (REGULAR,'Regular'),
        (MALA,'Mala')
    ]
        
    anej_id=models.AutoField(primary_key=True,verbose_name='identificador')
    anej_cantidad_anos=models.PositiveIntegerField(null=False,blank=False,verbose_name='Cantidad de años')
    anej_calidad_agua=models.CharField(max_length=10,null=False,blank=False,choices=CALIDAD_AGUA,verbose_name='Calidad del agua')
    fk_anej_meto_ferm=models.ForeignKey('MetodoFermentacion',on_delete=models.CASCADE,null=False,blank=False,related_name='anej_meto_ferm',verbose_name='Metodo de fermentacion')
    fk_anej_meto_dest=models.ForeignKey('MetodoDestilacion',on_delete=models.CASCADE,null=False,blank=False,related_name='anej_meto_dest',verbose_name='Metodo de destilacion')
    
    def __str__(self):
        return str(self.anej_cantidad_anos)+" años" +" "+self.anej_calidad_agua
    
    class Meta:
        verbose_name_plural = "Añejamiento"
class MetodoDestilacion(models.Model):
    meto_dest_id=models.AutoField(primary_key=True,verbose_name='identificador')
    meto_dest_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.meto_dest_nombre
    
    class Meta:
        verbose_name_plural = "Metodo Destilacion"
class MetodoFermentacion(models.Model):
    meto_ferm_id=models.AutoField(primary_key=True,verbose_name='identificador')
    meto_ferm_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    
    def __str__(self):
        return self.meto_ferm_nombre

    class Meta:
        verbose_name_plural = "Metodo Fermentacion"

class Barril(models.Model):
    
    BUENO='Bueno'
    REGULAR='Regular'
    MALO='Malo'
        
    CALIDAD_BARRIL=[
        (BUENO,'Bueno'),
        (REGULAR,'Regular'),
        (MALO,'Malo')
    ]
    
    ROBLE='Roble'
    
    
    TIPO_MADERA=[
        (ROBLE,'Roble')
    ]
    
    

    
    barr_id=models.AutoField(primary_key=True,verbose_name='identificador')
    barr_calidad=models.CharField(max_length=50,null=False,blank=False,choices=CALIDAD_BARRIL,verbose_name='Calidad del barril')
    barr_tipo=models.CharField(max_length=50,null=False,blank=False,verbose_name='Tipo de barril')
    barr_tamano=models.PositiveIntegerField(null=False,blank=False,verbose_name='Tamaño del barril')
    barr_tipo_madera=models.CharField(max_length=50,null=False,blank=False,choices=TIPO_MADERA,verbose_name='Tipo de madera')
    
    def __str__(self) -> str:
        return self.barr_tipo+" "+self.barr_tipo_madera+" "+str(self.barr_tamano)+" litros"

    class Meta:
        verbose_name_plural = "Barril"

class BarrilAnejamiento(models.Model):
    barr_anej_id=models.AutoField(primary_key=True)
    barr_anej_anos_barril=models.PositiveIntegerField(null=False,blank=False,verbose_name='Años del barril')
    fk_barr_anej_anej=models.ForeignKey('Anejamiento',on_delete=models.CASCADE,null=False,blank=False,related_name='barr_anej_anej')
    fk_barr_anej_barr=models.ForeignKey('Barril',on_delete=models.CASCADE,null=False,blank=False,related_name='barr_anej_barr',verbose_name='Barril')
    

    def __str__(self):
        return str(self.barr_anej_anos_barril)+" años"

    class Meta:
        unique_together =('fk_barr_anej_anej','fk_barr_anej_barr')
        verbose_name_plural = "Barril y Añejamiento"


class Botella(models.Model):
    bote_id=models.AutoField(primary_key=True)
    bote_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre de la botella')
    bote_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion de la botella')
    fk_bote_ron=models.ForeignKey('Ron',on_delete=models.CASCADE,null=False,blank=False,related_name='bote_ron',verbose_name='Ron')
    fk_bote_caja=models.ForeignKey('Caja',on_delete=models.CASCADE,null=False,blank=False,related_name='bote_caja',verbose_name='Caja')
    fk_bote_tapa_mate=models.ForeignKey('TapaMaterial',on_delete=models.CASCADE,null=False,blank=False,related_name='bote_tapa_mate',verbose_name='Tapa y Material')
    fk_bote_mate_tipo_bote=models.ForeignKey('MaterialTipoBotella',on_delete=models.CASCADE,null=False,blank=False,related_name='bote_mate_tipo_bote',verbose_name='Material y Tipo Botella')
    
    
    def __str__(self) -> str:
        return self.bote_nombre
    
    class Meta:
        verbose_name_plural = "Botella"
        
        
class Caja(models.Model):
    PALETA='Paleta'
    BULTO='Bulto'
    CAJA='Caja'
    
    TIPO_CAJA=[
        (PALETA,'Paleta'),
        (BULTO,'Bulto'),
        (CAJA,'Caja')
    ]
    
    caja_id=models.AutoField(primary_key=True,verbose_name='identificador')
    caja_cantidad=models.PositiveIntegerField(null=False,blank=False,verbose_name='Cantidad')
    caja_tipo=models.CharField(max_length=50,null=False,blank=False,choices=TIPO_CAJA,verbose_name='Tipo')
    caja_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    fk_caja_caja=models.ForeignKey('Caja',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Embalaje')
    
    def __str__(self) -> str:
        return self.caja_nombre+" "+str(self.caja_cantidad)+" "+self.caja_tipo
    
    class Meta:
        verbose_name_plural = "Caja"


class Tapa(models.Model):
    tapa_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tapa_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.tapa_nombre
    
    class Meta:
        verbose_name_plural = "Tapa"

class Material(models.Model):
    mate_id=models.AutoField(primary_key=True,verbose_name='identificador')
    mate_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.mate_nombre
    
    class Meta:
        verbose_name_plural = "Material"


class TipoBotella(models.Model):
    tipo_bote_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tipo_bote_altura=models.PositiveIntegerField(null=False,blank=False,verbose_name='Altura')
    tipo_bote_ancho=models.PositiveIntegerField(null=False,blank=False,verbose_name='Ancho')
    tipo_bote_capacidad=models.PositiveIntegerField(null=False,blank=False,verbose_name='Capacidad')
    
    def __str__(self) -> str:
        return str(self.tipo_bote_altura)+"cm "+str(self.tipo_bote_ancho)+"cm "+str(self.tipo_bote_capacidad)+"ml"
    
    class Meta:
        verbose_name_plural = "Tipo Botella"


class MaterialTipoBotella(models.Model):
    mate_tipo_bote_id=models.AutoField(primary_key=True,verbose_name='identificador')
    mate_tipo_bote_peso=models.PositiveIntegerField(null=False,blank=False,verbose_name='Peso')
    fk_mate_tipo_bote_mate=models.ForeignKey('Material',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Material')
    fk_mate_tipo_bote_tipo_bote=models.ForeignKey('TipoBotella',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tipo de Botella')
    
    def get_related_names(self):
        data = MaterialTipoBotella.objects.filter(pk=self.pk).values('fk_mate_tipo_bote_mate__mate_nombre', 'fk_mate_tipo_bote_tipo_bote__tipo_bote_altura','fk_mate_tipo_bote_tipo_bote__tipo_bote_ancho','fk_mate_tipo_bote_tipo_bote__tipo_bote_capacidad').first()
        return data['fk_mate_tipo_bote_mate__mate_nombre'], data['fk_mate_tipo_bote_tipo_bote__tipo_bote_altura'],data['fk_mate_tipo_bote_tipo_bote__tipo_bote_ancho'],data['fk_mate_tipo_bote_tipo_bote__tipo_bote_capacidad']

    def __str__(self) -> str:
        mate_nombre, bote_altura,bote_ancho,bote_capacidad = self.get_related_names()
        return f"{mate_nombre} {bote_altura}cm  {bote_ancho}cm  {bote_capacidad}ml"
    class Meta:
        verbose_name_plural = "Material y Tipo Botella"
        unique_together = ('fk_mate_tipo_bote_mate', 'fk_mate_tipo_bote_tipo_bote')

class TapaMaterial(models.Model):
    tapa_mate_id=models.AutoField(primary_key=True,verbose_name='identificador')
    fk_tapa_mate_tapa=models.ForeignKey('Tapa',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tapa')
    fk_tapa_mate_mate=models.ForeignKey('Material',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Material')
    
    def get_releted_names(self):
        data=TapaMaterial.objects.filter(pk=self.pk).values('fk_tapa_mate_tapa__tapa_nombre','fk_tapa_mate_mate__mate_nombre').first()
        return data['fk_tapa_mate_tapa__tapa_nombre'],data['fk_tapa_mate_mate__mate_nombre']
    
    def __str__(self) -> str:
        tapa_nombre,mate_nombre=self.get_releted_names()
        return tapa_nombre+" "+mate_nombre
    class Meta:
        verbose_name_plural = "Tapa y Material"
        unique_together = ('fk_tapa_mate_tapa', 'fk_tapa_mate_mate')



class Premio(models.Model):
    prem_id=models.AutoField(primary_key=True,verbose_name='identificador')
    prem_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    prem_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion')
    prem_direccion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fisica')
    fk_prem_lugar=models.ForeignKey('Lugar',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    
    def __str__(self) -> str:
        return self.prem_nombre
    
    class Meta:
        verbose_name_plural = "Premio"


class Evento(models.Model):
    event_id=models.AutoField(primary_key=True,verbose_name='identificador')
    event_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    event_descripcion=models.CharField(max_length=1000,null=False,blank=False,verbose_name='Descripcion')
    event_direccion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fisica')
    event_fecha_ini=models.DateField(null=False,blank=False,verbose_name='Fecha Inicio')
    event_fecha_fin=models.DateField(null=False,blank=False,verbose_name='Fecha Fin')
    fk_event_lugar=models.ForeignKey('Lugar',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    fk_event_tien=models.ForeignKey('Tienda',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tienda')
    
    
    def __str__(self) -> str:
        return self.event_nombre
    
    class Meta:
        verbose_name_plural = "Evento"

class EntradaEvento(models.Model):
    entr_envt_id=models.AutoField(primary_key=True)
    entr_envt_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    entr_envt_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion',default=' ')
    entr_envt_precio=models.FloatField(null=False,blank=False,verbose_name='Precio',validators=[MinValueValidator(1.00)])
    entr_evnt_cantidad=models.PositiveIntegerField(null=False,blank=False,verbose_name='Cantidad',validators=[MinValueValidator(1)])
    entr_envt_fecha_inicio=models.DateTimeField(null=False,blank=False,verbose_name='Fecha')
    entr_envt_fecha_fin=models.DateTimeField(null=False,blank=False,verbose_name='Fecha de fin')
    fk_entr_envt_evento=models.ForeignKey('Evento',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Evento',related_name='entr_envt_evento')
    
    
    def __str__(self) -> str:
        return self.entr_envt_nombre
    
    class Meta:
        verbose_name_plural = "Entrada Evento"
        
        
    
class NotaCata(models.Model):
    nota_cata_id=models.AutoField(primary_key=True,verbose_name='identificador')
    nota_cata_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    nota_cata_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion')
    fk_nota_cata_cata_even_premio_ron=models.OneToOneField('CataEventoPremioRon',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Cata Evento Premio Ron',related_name='nota_cata_cata_even_premio_ron')

    def __str__(self) -> str:
        return self.nota_cata_nombre
    
    class Meta:
        verbose_name_plural = "Nota de Cata"
    
class CataEventoPremioRon(models.Model):
    cata_even_premio_ron_id=models.AutoField(primary_key=True,verbose_name='identificador')
    cata_even_premio_ron_fecha_premiacion=models.DateTimeField(null=False,blank=False,verbose_name='Fecha de premiacion')
    fk_cata_even_premio_ron_ron=models.ForeignKey('Ron',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Ron')
    fk_cata_even_premio_ron_premio=models.ForeignKey('Premio',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Premio')
    fk_cata_even_premio_ron_evento=models.ForeignKey('Evento',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Evento')
    
    def __str__(self) -> str:
        return self.cata_even_premio_ron_fecha_premiacion.strftime("%d/%m/%Y, %H:%M:%S")
    
    class Meta:
        unique_together = ('fk_cata_even_premio_ron_ron', 'fk_cata_even_premio_ron_premio','fk_cata_even_premio_ron_evento')
        verbose_name_plural = "Cata Evento Premio Ron"



class TipoTienda(models.Model):
    tipo_tiend_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tipo_tiend_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.tipo_tiend_nombre
    
    class Meta:
        verbose_name_plural = "Tipo Tienda"
        
class Tienda(models.Model):
    tiend_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tiend_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    tiend_dirrecion=models.CharField(max_length=200,null=True,blank=True,verbose_name='Direccion Fisica')
    fk_tiend_tipo_tiend=models.ForeignKey('TipoTienda',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tipo de Tienda')
    fk_tiend_lugar=models.ForeignKey('Lugar',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    
    def __str__(self) -> str:
        return self.tiend_nombre +" "+self.fk_tiend_tipo_tiend.tipo_tiend_nombre
    
    class Meta:
        verbose_name_plural = "Tienda"
        
class InventarioTienda(models.Model):
    inve_tiend_id=models.AutoField(primary_key=True,verbose_name='identificador')
    inve_tiend_cantidad=models.PositiveIntegerField(null=False,blank=False,verbose_name='Cantidad')
    fk_inve_tiend_bote=models.ForeignKey('Botella',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Botella')
    fk_inve_tiend_tiend=models.ForeignKey('Tienda',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tienda')
    
    class Meta:
        verbose_name_plural = "Inventario Tienda"
        unique_together = ('fk_inve_tiend_bote', 'fk_inve_tiend_tiend')
        
    def __str__(self) -> str:
        return self.fk_inve_tiend_bote.bote_nombre+" "+self.fk_inve_tiend_tiend.tiend_nombre
    
class HistoricoRon(models.Model):
    hist_ron_id=models.AutoField(primary_key=True,verbose_name='identificador')
    hist_ron_fecha_inicio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    hist_ron_fecha_fin=models.DateField(null=True,blank=True,verbose_name='Fecha de fin')
    hist_ron_precio=models.FloatField(null=False,blank=False,verbose_name='Precio',validators=[MinValueValidator(1.00)])
    fk_hist_ron_inve_tiend=models.ForeignKey('InventarioTienda',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Inventario Tienda')
    
    def __str__(self) -> str:
        return str(self.hist_ron_fecha_inicio)+" "+str(self.hist_ron_fecha_fin)+" "+str(self.hist_ron_precio)
    
    class Meta:
        verbose_name_plural = "Historico Ron"
        

class Oferta(models.Model):
    ofer_id=models.AutoField(primary_key=True,verbose_name='identificador')
    ofer_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    ofer_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion')
    ofer_fecha_inicio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    ofer_fecha_fin=models.DateField(null=False,blank=False,verbose_name='Fecha de fin')
    
    def __str__(self) -> str:
        return self.ofer_nombre
    
    class Meta:
        verbose_name_plural = "Oferta"
        
class OfertaBotella(models.Model):
    ofer_bote_id=models.AutoField(primary_key=True)
    ofer_bote_porcentaje=models.PositiveIntegerField(null=False,blank=False,verbose_name='Porcentaje')
    fk_ofer_bote_bote=models.ForeignKey('Botella',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Botella')
    fk_ofer_bote_ofer=models.ForeignKey('Oferta',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Oferta')
    
    class Meta:
        verbose_name_plural = "Oferta Botella"
        unique_together = ('fk_ofer_bote_bote', 'fk_ofer_bote_ofer')
        
    def __str__(self) -> str:
        return self.fk_ofer_bote_bote.bote_nombre+" "+self.fk_ofer_bote_ofer.ofer_nombre
    

class ClienteNatural(models.Model):
    clie_natu_id=models.AutoField(primary_key=True,verbose_name='identificador')
    clie_natu_rif=models.CharField(max_length=10,null=False,blank=False,verbose_name='RIF',unique=True)
    clie_natu_cedula_identidad=models.CharField(max_length=10,null=False,blank=False,verbose_name='Cedula de identidad',unique=True) 
    clie_natu_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    clie_natu_apellido=models.CharField(max_length=50,null=False,blank=False,verbose_name='Apellido')
    clie_natu_segundo_nombre=models.CharField(max_length=50,null=True,blank=True,verbose_name='Segundo Nombre')
    clie_natu_segundo_apellido=models.CharField(max_length=50,null=True,blank=True,verbose_name='Segundo Apellido')
    clie_natu_direccion_habitacion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion de habitacion')
    clie_natu_puntos=models.FloatField(default=0,verbose_name='Puntos')
    fk_clie_natu_lugar=models.ForeignKey('Lugar',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    
    def __str__(self) -> str:
        return self.clie_natu_nombre+" "+self.clie_natu_apellido 

    class Meta:
        verbose_name_plural = "Cliente Natural"
       

        
        
class ClienteJuridico(models.Model):
    clie_juri_id=models.AutoField(primary_key=True,verbose_name='identificador')
    clie_juri_rif=models.CharField(max_length=10,null=False,blank=False,verbose_name='RIF',unique=True)
    clie_juri_denominacion_comercial=models.CharField(max_length=50,null=False,blank=False,verbose_name='Denominacion Comercial')
    clie_juri_razon_social=models.CharField(max_length=50,null=False,blank=False,verbose_name='Razon Social')
    clie_juri_pagina_web=models.CharField(max_length=50,null=True,blank=True,verbose_name='Pagina Web')
    clie_juri_capital_disponible=models.PositiveIntegerField(default=0,verbose_name='Capital Disponible')
    clie_juri_direccion_fisica=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fisica')
    clie_juri_direccion_fiscal=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fiscal')    
    clie_juri_puntos=models.FloatField(default=0,verbose_name='Puntos')
    fk_clie_juri_tipo_come=models.ForeignKey('TipoComercio',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Tipo de Comercio')
    fk_clie_juri_lugar_fisica=models.ForeignKey('Lugar',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Direccion Fisica Geografica',limit_choices_to={'lugar_tipo':'parroquia'})
    fk_clie_juri_lugar_fiscal=models.ForeignKey('Lugar',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Direccion Fiscal Geografica',related_name='clie_juri_lugar_fiscal',limit_choices_to={'lugar_tipo':'parroquia'})
    def __str__(self) -> str:
        return self.clie_juri_denominacion_comercial+" "+self.clie_juri_razon_social
    
    class Meta:
        verbose_name_plural = "Cliente Juridico"
        
class TipoComercio(models.Model):
    tipo_comer_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tipo_comer_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    
    def __str__(self) -> str:
        return self.tipo_comer_nombre
    
    class Meta:
        verbose_name_plural = "Tipo de Comercio"

class Departamento(models.Model):
    depa_id=models.AutoField(primary_key=True,verbose_name='identificador')
    depa_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    depa_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion')
    
    def __str__(self) -> str:
        return self.depa_nombre

    class Meta:
        verbose_name_plural = "Departamento"
        
        
class Empleado(models.Model):
    empl_id=models.AutoField(primary_key=True,verbose_name='identificador')
    empl_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    empl_nombre_segundo=models.CharField(max_length=50,null=True,blank=True,verbose_name='Segundo Nombre')
    empl_apellido=models.CharField(max_length=50,null=False,blank=False,verbose_name='Apellido')
    empl_apellido_segundo=models.CharField(max_length=50,null=True,blank=True,verbose_name='Segundo Apellido')
    empl_cedula_identidad=models.CharField(max_length=10,null=False,blank=False,verbose_name='Cedula de identidad',unique=True)
    empl_direccion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fisica')
    fk_empl_depa=models.ForeignKey('Departamento',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Departamento')
    fk_empl_lugar=models.ForeignKey('Lugar',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    fk_empl_vaca=models.ForeignKey('Vacacion',on_delete=models.PROTECT,null=True,blank=True,verbose_name='Vacaciones')
    
    def __str__(self) -> str:
        return self.empl_nombre+" "+self.empl_apellido +" "+ self.empl_cedula_identidad
    
    class Meta:
        verbose_name_plural = "Empleado"

class EmpleadoTienda(models.Model):
    empl_tiend_id=models.AutoField(primary_key=True)
    empl_tiend_fecha_incio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    empl_tiend_fecha_fin=models.DateField(null=True,blank=True,verbose_name='Fecha de fin')
    fk_empl_tiend_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Empleado',related_name='empl_tiend_empl')
    fk_empl_tiend_tiend=models.ForeignKey('Tienda',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tienda',related_name='empl_tiend_tiend')
    
    class Meta:
        verbose_name_plural = "Empleado Tienda"
        
    def __str__(self) -> str:
        return self.fk_empl_tiend_empl.empl_nombre+" "+self.fk_empl_tiend_tiend.tiend_nombre
    
    

class Vacacion(models.Model):
    vaca_id=models.AutoField(primary_key=True,verbose_name='identificador')
    vaca_fecha_inicio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    vaca_fecha_fin=models.DateField(null=False,blank=False,verbose_name='Fecha de fin') 
    
    def __str__(self) -> str:
        return str(self.vaca_fecha_inicio)+" "+str(self.vaca_fecha_fin)
    
    class Meta:
        verbose_name_plural = "Vacacion"
    
class Horario(models.Model):
    LUNES='Lunes'
    MARTES='Martes'
    MIERCOLES='Miercoles'
    JUEVES='Jueves'
    VIERNES='Viernes'
    SABADO='Sabado'
    DOMINGO='Domingo'
    
    DIA=[
        (LUNES,'Lunes'),
        (MARTES,'Martes'),
        (MIERCOLES,'Miercoles'),
        (JUEVES,'Jueves'),
        (VIERNES,'Viernes'),
        (SABADO,'Sabado'),
        (DOMINGO,'Domingo')
    ]


    
    hora_id=models.AutoField(primary_key=True,verbose_name='identificador')
    hora_hora_entrada=models.TimeField(null=False,blank=False,verbose_name='Hora de entrada')
    hora_hora_salida=models.TimeField(null=False,blank=False,verbose_name='Hora de salida')
    hora_dia=models.CharField(max_length=50,null=False,blank=False,verbose_name='Dia',choices=DIA) 
    
    def __str__(self) -> str:
        return self.hora_dia+"  de  "+str(self.hora_hora_entrada)+" a  "+str(self.hora_hora_salida)
    
    
    class Meta:
        verbose_name_plural = "Horario"      

class HorarioEmpleado(models.Model):
    hora_empl_id=models.AutoField(primary_key=True)
    hora_empl_fecha_incio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    hora_empl_fecha_fin=models.DateField(null=True,blank=True,verbose_name='Fecha de fin')
    fk_hora_empl_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Empleado')
    fk_hora_empl_hora=models.ForeignKey('Horario',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Horario')
    
    
class BeneficioEmpleado(models.Model):
    bene_empl_id=models.AutoField(primary_key=True)
    bene_empl_fecha_incio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    bene_empl_fecha_fin=models.DateField(null=True,blank=True,verbose_name='Fecha de fin')
    fk_bene_empl_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Empleado')
    fk_bene_empl_bene=models.ForeignKey('Beneficio',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Beneficio')
    
class CargoEmpleado(models.Model):
    cargo_empl_id=models.AutoField(primary_key=True)
    cargo_empl_fecha_incio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    cargo_empl_fecha_fin=models.DateField(null=True,blank=True,verbose_name='Fecha de fin')
    cargo_empl_salario=models.PositiveIntegerField(null=False,blank=False,verbose_name='Salario',default=0)
    fk_cargo_empl_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Empleado')
    fk_cargo_empl_sala=models.ForeignKey('Cargo',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Cargo')
    


class Beneficio(models.Model):
    bene_id=models.AutoField(primary_key=True,verbose_name='identificador')
    bene_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    bene_descripcion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Descripcion')
    
    def __str__(self) -> str:
        return self.bene_nombre
    
    class Meta:
        verbose_name_plural = "Beneficio"
        
class Cargo(models.Model):
    cargo_id=models.AutoField(primary_key=True,verbose_name='identificador')
    cargo_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Cargo')
    
    def __str__(self) -> str:
        return self.cargo_nombre
    
    class Meta:
        verbose_name_plural = "Cargo"
        
class Asistencia(models.Model):
    asis_id=models.AutoField(primary_key=True,verbose_name='identificador')
    asis_hora_entrada=models.TimeField(null=False,blank=False,verbose_name='Hora de entrada')
    asis_hora_salida=models.TimeField(null=False,blank=False,verbose_name='Hora de salida')
    asis_fecha=models.DateField(null=False,blank=False,verbose_name='Fecha')
    fk_asis_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Empleado')
    def __str__(self) -> str:
        return str(self.asis_hora_entrada)+" "+str(self.asis_hora_salida)
    
    class Meta:
        verbose_name_plural = "Asistencia"
        
class Notificacion(models.Model):
    noti_id=models.AutoField(primary_key=True,verbose_name='identificador')
    noti_asunto=models.CharField(max_length=50,null=False,blank=False,verbose_name='Asunto')
    noti_descripcion=models.CharField(max_length=1500,null=False,blank=False,verbose_name='Descripcion')
    noti_id_tienda=models.PositiveIntegerField(null=False,blank=False,verbose_name='Tienda')
    noti_id_prov=models.PositiveIntegerField(null=False,blank=False,verbose_name='Proveedor')
    noti_id_pro=models.PositiveIntegerField(null=False,blank=False,verbose_name='Producto',default=0)
    fk_noti_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Empleado')
    
    class Meta:
        verbose_name_plural = "Notificacion"


    
class Proveedor(models.Model):    
    prov_id=models.AutoField(primary_key=True,verbose_name='identificador')
    prov_rif=models.CharField(max_length=10,null=False,blank=False,verbose_name='RIF')
    prov_denominacion_comercial=models.CharField(max_length=50,null=False,blank=False,verbose_name='Denominacion Comercial')
    prov_razon_social=models.CharField(max_length=50,null=False,blank=False,verbose_name='Razon Social')
    prov_pagina_web=models.CharField(max_length=50,null=True,blank=True,verbose_name='Pagina Web')
    prov_direccion_fiscal=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fiscal')
    prov_direccion_fisica=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fisica')
    fk_prov_lugar=models.ForeignKey('Lugar',on_delete=models.PROTECT,null=False,blank=False,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    
    def __str__(self) -> str:
        return self.prov_denominacion_comercial+" "+self.prov_razon_social

    class Meta:
        verbose_name_plural = "Proveedor"
        
        
class CorreoElectronico(models.Model):
    mail_id=models.AutoField(primary_key=True)
    mail_dirrecion_correo=models.CharField(max_length=50,null=False,blank=False,unique=True,verbose_name='Direccion de correo electronico')
    fk_mail_prov=models.ForeignKey('Proveedor',on_delete=models.CASCADE,null=False,blank=False,default=None,verbose_name='Proveedor')
    class Meta:
        verbose_name_plural = "Correo Electronico"
        
        
class PersonaContacto(models.Model):
    pers_cont_id=models.AutoField(primary_key=True)
    pers_cont_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    pers_cont_apellido=models.CharField(max_length=50,null=False,blank=False,verbose_name='Apellido')
    fk_pers_cont_prov=models.ForeignKey('Proveedor',on_delete=models.CASCADE,null=True,blank=True)
    fk_pers_cont_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True)
    
    def __str__(self) -> str:
        return self.pers_cont_nombre+" "+self.pers_cont_apellido
    
    class Meta:
        verbose_name_plural = "Persona de Contacto"
        
        

        
        
class Telefono(models.Model):
    telf_id=models.AutoField(primary_key=True)
    telf_numero=models.CharField(max_length=7,null=False,blank=False,verbose_name='Numero de telefono')
    fk_telf_telf_codi=models.ForeignKey('TelefonoCodigo',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Codigo de area')
    fk_telf_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,related_name='clie_natu_telf')
    fk_telf_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,related_name='clie_juri_telf')
    fk_telf_prov=models.ForeignKey('Proveedor',on_delete=models.CASCADE,null=True,blank=True,related_name='prov_telf')
    fk_telf_empl=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=True,blank=True,related_name='empl_telf')
    fk_telf_pers_cont=models.ForeignKey('PersonaContacto',on_delete=models.CASCADE,null=True,blank=True,related_name='pers_cont_telf')
    
    def __str__(self) -> str:
        return self.telf_numero + " " + self.fk_telf_telf_codi.telf_cod_codigo
    class Meta:
        verbose_name_plural = "Telefono"
        
class TelefonoCodigo(models.Model):
    telf_cod_id=models.AutoField(primary_key=True,verbose_name='identificador')
    telf_cod_codigo=models.CharField(max_length=4,null=False,blank=False,verbose_name='Codigo de area')
    
    def __str__(self) -> str:
        return self.telf_cod_codigo
    
    class Meta:
        verbose_name_plural = "Codigo de Telefono"
    
    
    
    
    
    
    
    
    
class Lugar(models.Model):
    PAIS='pais'
    ESTADO='estado'
    PARROQUIA='parroquia'
    MUNICIPIO='municipio'
 
    
    TIPO_LUGAR=[
        (PAIS,'pais'),
        (MUNICIPIO,'municipio'),
        (ESTADO,'estado'),
        (PARROQUIA,'parroquia'),
    ]
    
    lugar_id=models.AutoField(primary_key=True,verbose_name='identificador')
    lugar_tipo=models.CharField(max_length=50,null=False,blank=False,choices=TIPO_LUGAR,verbose_name='Tipo de lugar')
    lugar_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre del lugar')
    fk_lugar_lugar=models.ForeignKey('Lugar',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Lugar Origen')
    
    class Meta:
        verbose_name_plural = "Lugar"
    
    def __str__(self) -> str:
        return self.lugar_tipo.upper() + "  "+ self.lugar_nombre
    
    

class StatusPedido(models.Model):
    stat_pedi_id=models.AutoField(primary_key=True,verbose_name='identificador')
    stat_pedi_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')

    def __str__(self) -> str:
        return self.stat_pedi_nombre
    
    class Meta:
        verbose_name_plural = "Status Pedido"
        
class VentaStatus(models.Model):
    venta_stat_id=models.AutoField(primary_key=True,verbose_name='identificador')
    venta_stat_status=models.BooleanField(null=False,blank=False,verbose_name='Comprobante')
    venta_stat_fecha_inicio=models.DateTimeField(null=False,blank=False,verbose_name='Fecha antes de comprobacion')
    venta_stat_fecha_fin=models.DateTimeField(null=True,blank=True,verbose_name='Fecha despues de comprobacion')
    fk_venta_stat_stat_pedi=models.ForeignKey('StatusPedido',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Status Pedido')
    fk_venta_stat_compr=models.ForeignKey('Compra',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Compra')
    fk_venta_stat_vent=models.ForeignKey('Venta',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Venta')
    
    

    
    class Meta:
        verbose_name_plural = "Status Venta"
        
class Compra(models.Model):
    compr_id=models.AutoField(primary_key=True,verbose_name='identificador')
    compr_fecha_compra=models.DateTimeField(null=False,blank=False,verbose_name='Fecha de compra')
    fk_compr_tiend=models.ForeignKey('Tienda',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Tienda')
    fk_compr_prove=models.ForeignKey('Proveedor',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Proveedor')
    
    def __str__(self) -> str:
        return str(self.compr_fecha_compra) +self.fk_compr_tiend.tiend_nombre
    
    class Meta:
        verbose_name_plural = "Compra"
        
    
class DetalleCompra(models.Model):
    deta_compr_id=models.AutoField(primary_key=True,verbose_name='identificador')
    deta_compr_cantidad=models.PositiveIntegerField(null=False,blank=False,verbose_name='Cantidad')
    deta_compr_precio=models.FloatField(null=False,blank=False,verbose_name='Precio',validators=[MinValueValidator(1.00)])
    fk_deta_compr_compr=models.ForeignKey('Compra',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Compra')
    fk_deta_compr_bote=models.ForeignKey('Botella',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Botella')
    
    def __str__(self) -> str:
        return str(self.deta_compr_cantidad)+" "+str(self.deta_compr_precio)
    
    class Meta:
        verbose_name_plural = "Detalle Compra"
        unique_together = ('fk_deta_compr_compr', 'fk_deta_compr_bote')


class Afiliado(models.Model):
    afil_id=models.AutoField(primary_key=True,verbose_name='identificador')
    afil_nombre=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre')
    afil_precio=models.FloatField(null=False,blank=False,verbose_name='Precio',validators=[MinValueValidator(1.00)])
    
    def __str__(self) -> str:
        return self.afil_nombre
    
    class Meta:
        verbose_name_plural = "Afiliado"
        

class AfiliadoClienteProveedor(models.Model):
    afil_clie_prov_id=models.AutoField(primary_key=True,verbose_name='identificador')
    afil_clie_prov_fecha_afiliacion=models.DateField(null=False,blank=False,verbose_name='Fecha de afiliacion')
    afil_clie_prov_fecha_vencimiento=models.DateField(null=False,blank=False,verbose_name='Fecha de vencimiento')
    fk_afil_clie_prov_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    fk_afil_clie_prov_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    fk_afil_clie_prov_prov=models.ForeignKey('Proveedor',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Proveedor')
    fk_afil_clie_prov_afil=models.ForeignKey('Afiliado',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Afiliado')
    
    def __str__(self) -> str:
        return self.fk_afil_clie_prov_afil.afil_nombre
    
    class Meta:
        verbose_name_plural = "Afiliado Cliente Proveedor"
        
        

class Carrito(models.Model):
    carr_id=models.AutoField(primary_key=True,verbose_name='identificador')
    carr_uuid=models.UUIDField(default=uuid.uuid4,editable=False,verbose_name='UUID',unique=True)
    carri_comprado=models.BooleanField(default=False,verbose_name='Comprado')
    carri_empleado=models.BooleanField(default=False,verbose_name='Empleado')
    fk_carr_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    fk_carr_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    fk_carr_clie_emples=models.ForeignKey('Empleado',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Empleado')
    
    def __str__(self) -> str:
        return str(self.carr_id)
    
    class Meta:
        verbose_name_plural = "Carrito"
        
class CarritoItem(models.Model):
    carri_item_id=models.AutoField(primary_key=True,verbose_name='identificador')
    carri_item_cantidad=models.PositiveIntegerField(null=False,blank=False,verbose_name='Cantidad')
    carri_item_precio=models.FloatField(null=False,blank=False,verbose_name='Precio')
    fk_carri_item_carri=models.ForeignKey('Carrito',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Carrito')
    fk_carri_item_inve_tiend=models.ForeignKey('InventarioTienda',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Inventario Tienda')
    fk_carri_item_ofer_ron=models.ForeignKey('OfertaBotella',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Oferta Botella')
    fk_carri_item_entr_evento=models.ForeignKey('EntradaEvento',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Entrada Evento')
    fk_carri_item_afil=models.ForeignKey('Afiliado',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Afiliado')
    
    
    class Meta:
        verbose_name_plural = "Carrito Item"
        unique_together = [
            ('fk_carri_item_carri', 'fk_carri_item_inve_tiend', 'fk_carri_item_ofer_ron'),
            ('fk_carri_item_carri', 'fk_carri_item_entr_evento'),
            ('fk_carri_item_carri', 'fk_carri_item_afil'),
            ('fk_carri_item_carri', 'fk_carri_item_inve_tiend'),
        ]
        
        
class Venta(models.Model):
    vent_id=models.AutoField(primary_key=True,verbose_name='identificador')
    vent_fecha_venta=models.DateTimeField(null=False,blank=False,verbose_name='Fecha de venta')
    vent_monto_total=models.FloatField(null=False,blank=False,verbose_name='Precio',validators=[MinValueValidator(1.00)])
    venta_puntos=models.PositiveIntegerField(default=0,verbose_name='Puntos')
    venta_direccion=models.CharField(max_length=200,null=False,blank=False,verbose_name='Direccion Fisica')
    fk_vent_direccion=models.ForeignKey('Lugar',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Direccion',limit_choices_to={'lugar_tipo':'parroquia'})
    fk_vent_carri=models.OneToOneField('Carrito',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Carrito')
    
    def __str__(self) -> str:
        return str(self.vent_fecha_venta)
    
    class Meta:
        verbose_name_plural = "Venta"

class HistoricoDolar(models.Model):
    hist_dolar_id=models.AutoField(primary_key=True,verbose_name='identificador')
    hist_dolar_valor=models.FloatField(null=False,blank=False,verbose_name='Valor',validators=[MinValueValidator(1.00)])
    hist_dolar_fecha_inicio=models.DateTimeField(null=False,blank=False,verbose_name='Fecha de inicio')
    hist_dolar_fecha_fin=models.DateTimeField(null=True,blank=True,verbose_name='Fecha de fin')
    
    def __str__(self) -> str:
        return str( self.hist_dolar_valor)
    class Meta:
        verbose_name_plural = "Historico Dolar"

class TarjetaCredito(models.Model):
    tdc_id=models.AutoField(primary_key=True,verbose_name='identificador')
    tdc_numero_tarjeta=models.CharField(max_length=16,null=False,blank=False,verbose_name='Numero de tarjeta',validators=[MinLengthValidator(16)])
    tdc_nombre_titular=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre del titular')
    tdc_fecha_vencimiento=models.DateField(null=False,blank=False,verbose_name='Fecha de vencimiento')
    tdc_cvv=models.CharField(max_length=3,null=False,blank=False,verbose_name='CVV',validators=[MinLengthValidator(3)])
    fk_tdc_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    fk_tdc_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    
    def __str__(self) -> str:
        return self.tdc_numero_tarjeta
    
    class Meta:
        verbose_name_plural = "Tarjeta de Credito"
        
class Cheque(models.Model):
    cheq_id=models.AutoField(primary_key=True,verbose_name='identificador')
    cheq_numero_cheque=models.CharField(max_length=50,null=False,blank=False,verbose_name='Numero de cheque')
    cheq_banco=models.CharField(max_length=50,null=False,blank=False,verbose_name='Banco')
    chq_nombre_titular=models.CharField(max_length=50,null=False,blank=False,verbose_name='Nombre del titular',default='N/A')
    fk_cheq_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    fk_cheq_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    
    def __str__(self) -> str:
        return self.cheq_numero_cheque
    
    class Meta:
        verbose_name_plural = "Cheque"
        
class Efectivo(models.Model):
    efe_id=models.AutoField(primary_key=True,verbose_name='identificador')
    efe_monto=models.FloatField(null=False,blank=False,verbose_name='Monto',validators=[MinValueValidator(1.00)])
    fk_efe_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    fk_efe_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    
    def __str__(self) -> str:
        return str(self.efe_monto)
    
    class Meta:
        verbose_name_plural = "Efectivo"
        
class Puntos(models.Model):
    punt_id=models.AutoField(primary_key=True,verbose_name='identificador')
    punt_tiene_puntos=models.BooleanField(null=False,blank=False,verbose_name='Tiene puntos')
    fk_punt_clie_juri=models.ForeignKey('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    fk_punt_clie_natu=models.ForeignKey('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    
    def __str__(self) -> str:
        return str( self.punt_tiene_puntos)
    class Meta:
        verbose_name_plural = "Puntos"
        
class Pago(models.Model):
    pago_id=models.AutoField(primary_key=True,verbose_name='identificador')
    pago_cantidad_pagada=models.FloatField(null=False,blank=False,verbose_name='Cantidad pagada',validators=[MinValueValidator(1.00)])
    pago_tipo_pago=models.CharField(max_length=50,null=True,blank=True,verbose_name='Tipo de pago')
    fk_pago_vent=models.ForeignKey('Venta',on_delete=models.CASCADE,null=False,blank=False,verbose_name='Venta')
    fk_pago_tdc=models.ForeignKey('TarjetaCredito',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Tarjeta de Credito')
    fk_pago_cheq=models.ForeignKey('Cheque',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cheque')
    fk_pago_efe=models.ForeignKey('Efectivo',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Efectivo')
    fk_pago_punt=models.ForeignKey('Puntos',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Puntos')
    fk_pago_hist_dolar=models.ForeignKey('HistoricoDolar',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Historico Dolar')
    fk_pago_hist_punt=models.ForeignKey('HistoricoPunto',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Historico Punto')
    
    
    def __str__(self) -> str:
        return str(self.pago_cantidad_pagada)
    
    class Meta:
        verbose_name_plural = "Pago"
        
class HistoricoPunto(models.Model):
    hist_punt_id=models.AutoField(primary_key=True,verbose_name='identificador')
    hist_punt_valor=models.FloatField(null=False,blank=False,verbose_name='Valor',validators=[MinValueValidator(0.00)])
    hist_punt_fecha_inicio=models.DateField(null=False,blank=False,verbose_name='Fecha de inicio')
    hist_punt_fecha_fin=models.DateField(null=True,blank=True,verbose_name='Fecha de fin')
    
    
    def __str__(self) -> str:
        return str(self.hist_punt_valor)
    
    class Meta:
        verbose_name_plural = "Historico Punto"
    
class AfiliadoCodigo(models.Model):
    afil_codigo_id=models.AutoField(primary_key=True,verbose_name='identificador')
    afil_codigo_codigo=models.CharField(max_length=8,null=False,blank=False,verbose_name='Codigo',unique=True,validators=[MinLengthValidator(8)])
    fk_afil_prov=models.OneToOneField('Proveedor',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Proveedor')
    fk_afil_clie_juri=models.OneToOneField('ClienteJuridico',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Juridico')
    fk_afil_clie_natu=models.OneToOneField('ClienteNatural',on_delete=models.CASCADE,null=True,blank=True,verbose_name='Cliente Natural')
    
    def __str__(self) -> str:
        return self.afil_codigo_codigo