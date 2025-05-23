from rest_framework_nested import routers
from .views import *
from django.urls import path

router=routers.DefaultRouter()

router.register('botella-detail',BotellaDetailViewSet,basename='botella-detail')
router.register('inventario-tienda',InventarioTiendaViewSet,basename='inventario-tienda')
router.register('evento',EventoViewSet,basename='evento')
router.register('evento-detail',EventoDetailViewSet,basename='evento-detail')
router.register('diario-ronero',OfertaViewSet,basename='diario-ronero')


router.register('empleado',EmpleadoViewSet,basename='Empleado')


router.register('clienteNatural',ClienteNaturalViewSet,basename='clienteNatural')
cliente_natural_router=routers.NestedSimpleRouter(router,'clienteNatural',lookup='clienteNatural')
cliente_natural_router.register('telefononatu',TelefonoClienteNaturalViewSet,basename='telefono_natu')


router.register('clienteJuridico',ClienteJuridicoViewSet,basename='ClienteJuridico')
cliente_juridico_router=routers.NestedSimpleRouter(router,'clienteJuridico',lookup='clienteJuridico')
cliente_juridico_router.register('telefonojuri',TelefonoClienteJuridicoViewSet,basename='telefono_juridico')

router.register('codigoTelefono',TelefonoCodigoViewSet,basename='Telefono')
router.register('lugar',LugarViewSet,basename='lugar')
router.register('tipo-comercio',TipoComercioViewSet,basename='TipoComercio')
router.register('provedores',ProvedorFiltroViewSet,basename='ProvedorFiltro')
router.register('tipo-ron',TipoRonFiltroViewSet,basename='tipo-ron')
router.register('cliente-natural-empleado',ClienteNaturalEmpleadoViewSet,basename='cliente-natural-empleado')
router.register('cliente-juridico-empleado',ClienteJuridicoEmpleadoViewSet,basename='cliente-juridico-empleado')
router.register('carnet',CarnetViewSet,basename='carnet')
router.register('carrito',CarritoViewSet,basename='carrito')
router.register('carrito-detail',CarritoItemViewSet,basename='carrito-detail')
router.register('oferta-carrito',OfertaCarritoViewSet,basename='oferta-carrito')
router.register('afiliado',AfiliadoViewSet,basename='afiliado')
router.register('tdc',TDCviewSet,basename='tdc')
router.register('cheque',ChequeViewSet,basename='cheque')
router.register('efectivo',EfectivoViewSet,basename='efectivo')
router.register('punto',PuntoViewSet,basename='punto')
router.register('valor-punto',HistoricoPuntoViewSet,basename='valor-punto')
router.register('valor-dolar',HistoricoDolarViewSet,basename='valor-dolar')
router.register('venta',VentaViewSet,basename='venta')
router.register('afiliado-boolean',AfiliadoBooleanViewSet,basename='afiliado-boolean')
router.register('reporte_venta',ReporteVentaViewSet,basename='reporte_venta')
router.register('reporte_top_10_parroquias',TopDiezParroquiasViewSet,basename='reporte_top_10_parroquias')
router.register('total_compras',TotalComprasViewSet,basename='total_compras')
router.register('producto_mas_vendido',ProductoMasVendidoViewSer,basename='producto_mas_vendido')
router.register('ordenes_status',TotalOrdenStatusViewSet,basename='ordenes_status')
router.register('puntos_canjeados',TotalPuntosCajenadosViewSet,basename='puntos_canjeados')
router.register('puntos_otorgados',TotalPuntosOtorgadosViewSet,basename='puntos_otorgados')
router.register('top_10_pro_vendidos_fisica',Top10ProductosFisicoViewSet,basename='top_10_pro_vendidos_fisica')
router.register('ordenes_retrasadas',ReporteOrdenesRetradasViewSet,basename='ordenes_retrasadas')

urlpatterns = router.urls+cliente_natural_router.urls+cliente_juridico_router.urls


