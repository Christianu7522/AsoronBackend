from django.contrib.admin.models import LogEntry
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import Usuario
from django.contrib.admin.models import LogEntry
from django import forms

class UsuarioCreationForm(UserCreationForm):
    password1 = forms.CharField(label='Nueva Contraseña', strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Nueva Contraseña', strip=False, widget=forms.PasswordInput)

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'fk_usua_clie_natu', 'fk_usua_clie_juri', 'fk_usua_empl')
        labels={
            'username':'Nombre de usuario',
            'email':'Correo',
            'fk_usua_clie_natu':'Cliente Natural',
            'fk_usua_clie_juri':'Cliente Juridico',
            'fk_usua_empl':'Empleado',
            'Active':'Activo',
        }

class UsuarioChangeForm(UserChangeForm):
       
        class Meta:
            model = Usuario
            fields = ('username', 'email', 'fk_usua_clie_natu', 'fk_usua_clie_juri', 'fk_usua_empl')
            labels={
                'username':'Nombre de usuario',
                'email':'Correo',
                'fk_usua_clie_natu':'Cliente Natural',
                'fk_usua_clie_juri':'Cliente Juridico',
                'fk_usua_empl':'Empleado',
            }

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    
    list_per_page = 10
    list_display = ('usuario', 'email', 'cliente_natural', 'cliente_juridico', 'empleado')
    
    def usuario(self, obj):
        return obj.username
    
    def cliente_natural(self, obj):
        return obj.fk_usua_clie_natu
    
    def cliente_juridico(self, obj):
        return obj.fk_usua_clie_juri
    
    def empleado(self, obj):
        return obj.fk_usua_empl
    
    list_filter = ()
    
    fieldsets = (
                    (None, {'fields': ('username', 'password')}),
                    ('Correo', {'fields': ('email',)}),
                    ('Tipo Cliente', {'fields': ('fk_usua_clie_natu', 'fk_usua_clie_juri', 'fk_usua_empl')}),
                    ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
                    ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
    (None, {
                        'classes': ('wide',),
                        'fields': ('username', 'email', 'fk_usua_clie_natu', 'fk_usua_clie_juri', 'fk_usua_empl', 'password1', 'password2'),
                    }),
    )
    usuario.admin_order_field = 'username'
    cliente_natural.admin_order_field = 'fk_usua_clie_natu'
    cliente_juridico.admin_order_field = 'fk_usua_clie_juri'
    empleado.admin_order_field = 'fk_usua_empl'
    
    search_fields = ('username', 'email', 'fk_usua_clie_natu', 'fk_usua_clie_juri', 'fk_usua_empl')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_fieldsets(self, request, obj=None):
       
        if obj and not request.user.is_superuser and not request.user.groups.filter(name='Recursos humanos').exists():
            return (
                (None, {'fields': ('username', 'password')}),
                ('Correo', {'fields': ('email',)}),
                ('Tipo Cliente', {'fields': ('fk_usua_clie_natu', 'fk_usua_clie_juri', 'fk_usua_empl')}),
               
            )
        return super().get_fieldsets(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and not request.user.groups.filter(name='Recursos humanos').exists():
            qs = qs.filter(username=request.user.username)
        return qs


class Logform(forms.ModelForm):
    class Meta:
        model = LogEntry
        fields = '__all__'
        labels={
            'user':'Usuario',
            'action_time':'Fecha de accion',
            'content_type':'Modelo Modificado',
            'object_id':'ID de la fila modificada',
            'object_repr':'Representacion del objeto',
            'action_flag':'Accion realizada',
            'change_message':'Mensaje de cambio',
        }
        
@admin.register(LogEntry)
class LogAdmin(admin.ModelAdmin):
    form=Logform
    list_display = ('usuario', 'fecha_de_accion', 'modelo_modificado', 'id_de_la_fila_modificada', 'representacion_del_objeto', 'accion_realizada')
    
    def usuario(self, obj):
        return obj.user
    
    def fecha_de_accion(self, obj):
        return obj.action_time
    
    def modelo_modificado(self, obj):
        return obj.content_type
    
    def id_de_la_fila_modificada(self, obj):
        return obj.object_id
    
    def representacion_del_objeto(self, obj):
        return obj.object_repr
    
    def accion_realizada(self, obj):
        return obj.action_flag
    
    usuario.admin_order_field = 'user'
    fecha_de_accion.admin_order_field = 'action_time'
    modelo_modificado.admin_order_field = 'content_type'


    search_fields = ('user', 'object_repr', 'change_message')

    list_per_page = 10