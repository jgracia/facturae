# Generated by Django 2.2.8 on 2019-12-25 22:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("DROP VIEW IF EXISTS cliente_clientesaldo;"),
        migrations.RunSQL("""
            create view cliente_clientesaldo as
            select cliente_id, 0 as saldo
            from cliente_cliente
        """),
    ]
