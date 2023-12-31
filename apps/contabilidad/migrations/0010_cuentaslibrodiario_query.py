# Generated by Django 2.2.8 on 2019-12-26 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0009_cuentaslibromayor_query'),
    ]

    operations = [
        migrations.RunSQL("drop view if exists contabilidad_cuentaslibrodiario;"),
        migrations.RunSQL("""
            create or replace view contabilidad_cuentaslibrodiario as
            select debe.id, debe.asiento_id, debe.cuenta_id, debe.monto, 'D' AS "tipo_movimiento", asiento.numero_asiento, asiento.fecha, asiento.glosa, asiento.comprobante, asiento.usuario_creador_id, asiento.empresa_id
            from contabilidad_asientodebedetalle debe
            inner join contabilidad_asientocontable asiento on debe.asiento_id = asiento.id
            union
            select haber.id, haber.asiento_id, haber.cuenta_id, haber.monto, 'H' AS "tipo_movimiento", asiento.numero_asiento, asiento.fecha, asiento.glosa, asiento.comprobante, asiento.usuario_creador_id, asiento.empresa_id
            from contabilidad_asientohaberdetalle haber
            inner join contabilidad_asientocontable asiento on haber.asiento_id = asiento.id
            order by cuenta_id, asiento_id;
        """),
    ]
