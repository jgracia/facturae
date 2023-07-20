from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'producto'
urlpatterns = [
    # rutas productos
    path('listado_productos', login_required(views.IndexView.as_view()), name='listado_productos'),
    path('ajax_producto_resumen/', login_required(views.ajax_producto_resumen), name='ajax_producto_resumen'),
    #path('ajax_listado_productos/', login_required(views.ajax_listado_productos), name='ajax_listado_productos'),
    path('crear_producto/', login_required(views.CrearProducto.as_view()), name='crear_producto'),
    ###path('actualizar_costos/', login_required(views.actualizar_costos), name='actualizar_costos'),
    path('actualizar_costos_control/', login_required(views.actualizar_costos_control),
         name='actualizar_costos_control'),
    path('editar_producto/<int:pk>', login_required(views.EditarProducto.as_view()), name='editar_producto'),
    path('detalle_producto/<int:pk>',
         login_required(views.DetalleProducto.as_view()), name='detalle_producto'),
    path('eliminar_producto/<int:pk>',
         login_required(views.EliminarProducto.as_view()), name='eliminar_producto'),
    path('detalle_producto_modal/<int:pk>',
         login_required(views.DetalleProductoModal.as_view()), name='detalle_producto_modal'),
    path('export/xls/', login_required(views.export_products_xls), name='export_products_xls'),
    path('ajax/buscar_producto/', login_required(views.ajaxBuscarProductoDB), name='buscar_producto'),

    # rutas categorias de productos
    path('categorias/', login_required(views.ListadoCategorias.as_view()), name='listado_categorias'),
    path('crear_categoria/', login_required(views.CrearCategoria.as_view()), name='crear_categoria'),
    path('modificar_categoria/<int:pk>',
         login_required(views.ModificarCategoria.as_view()), name='modificar_categoria'),
    path('detalle_categoria/<int:pk>',
         login_required(views.DetalleCategoria.as_view()), name='detalle_categoria'),
    path('eliminar_categoria/<int:pk>',
         login_required(views.EliminarCategoria.as_view()), name='eliminar_categoria'),
    # categoría modal
    path('category/create/', login_required(views.category_create), name='category_create'),
    path('crear_categoria_modal/', login_required(views.CrearCategoriaModal.as_view()),
         name='crear_categoria_modal'),

    path('crear_categoria_bsmodal/', login_required(views.CrearCategoriaBSModal.as_view()),
         name='crear_categoria_bsmodal'),
    path('modificar_categoria_bsmodal/<int:pk>', login_required(views.ModificarCategoriaBSModal.as_view()),
         name='modificar_categoria_bsmodal'),
    path('detalle_categoria_bsmodal/<int:pk>', login_required(views.DetalleCategoriaBSModal.as_view()),
         name='detalle_categoria_bsmodal'),
    path('eliminar_categoria_bsmodal/<int:pk>', login_required(views.EliminarCategoriaBSModal.as_view()),
         name='eliminar_categoria_bsmodal'),
]
