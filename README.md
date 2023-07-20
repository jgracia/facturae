Facturador Electrónico

create database facturae_st;
create user userdb with encrypted password 'i2+4LH24c{s]';
grant all privileges on database facturae_st to userdb;


CARGAR DATOS INICIALES
./manage.py loaddata 01initial_sri_00.json
./manage.py loaddata 02initial_sri_01_retencion_iva.json
./manage.py loaddata 03initial_sri_02_retencion_renta.json
./manage.py loaddata 04initial_administracion.json
./manage.py loaddata 05initial_almacen.json
./manage.py loaddata 06initial_app.json
./manage.py loaddata 07initial_unidades.json
./manage.py loaddata 08initial_contabilidad.json