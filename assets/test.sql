--1.- Numero de personas que viajaron por cada estado
select e.nombre as Estado, count(c.cve_clientes) as Numero_Personas
from estados as e, clientes as c
where e.cve_estados = c.cve_estados
group by e.nombre;

--2.- Numero de personas que viajaron por cada estado, por cada año
select e.nombre as Estado, year(c.fecha_nacimiento) as Año, count(c.cve_clientes) as Numero_Personas
from estados as e, clientes as c
where e.cve_estados = c.cve_estados
group by e.nombre, year(c.fecha_nacimiento);

--3.- Numero de personas que viajaron de cada combinación municipios, estados
select e.nombre as Estado, m.nombre as municipio, count(c.cve_clientes) as Numero_Personas
from estados as e, municipios as m, clientes as c
where e.cve_estados = m.cve_estados and m.cve_municipios = c.cve_municipios
group by e.nombre, m.nombre
order by e.nombre;

--4.- Numero de vuelos por cada año
select year(dv.fecha_hora_salida) as Año, count(*) as Numero_Vuelos
from detalle_vuelos as dv
group by year(dv.fecha_hora_salida)
order by año;

--5.- Numero de vuelos por cada mes / año
select year(dv.fecha_hora_salida) as Año, month(dv.fecha_hora_salida) as Mes, count(*) as Numero_Vuelos
from detalle_vuelos as dv
group by year(dv.fecha_hora_salida), month(dv.fecha_hora_salida)
order by Mes;

--6.- Numero de personas que viajaron de acuerdo a su categoría: Niños hasta 12 años, adolescentes de 13 a 17 años, 
--jóvenes de 18 a 30 años, adultos de 30 a 59 años y adultos mayores de 60 en adelante.
select
    case
        when datediff(year, c.fecha_nacimiento, getdate()) <= 12 then 'Niños'
        when datediff(year, c.fecha_nacimiento, getdate()) between 13 and 17 then 'Adolescentes'
        when datediff(year, c.fecha_nacimiento, getdate()) between 18 and 30 then 'Jovenes'
        when datediff(year, c.fecha_nacimiento, getdate()) between 31 and 59 then 'Adultos'
        else 'Adultos Mayores' 
    end as Categoria,
    count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, clientes as c
where o.cve_clientes = c.cve_clientes
group by
    case
        when datediff(year, c.fecha_nacimiento, getdate()) <= 12 then 'Niños'
        when datediff(year, c.fecha_nacimiento, getdate()) between 13 and 17 then 'Adolescentes'
        when datediff(year, c.fecha_nacimiento, getdate()) between 18 and 30 then 'Jovenes'
        when datediff(year, c.fecha_nacimiento, getdate()) between 31 and 59 then 'Adultos'
        else 'Adultos Mayores' 
    end;

--7.- Numero de vuelos por cada aeropuerto de salida en cada año, del aeropuerto se desea saber la clave 
--internacional del aeropuerto y la clave internacional del país al que pertenece el aeropuerto
select a.clave_internacional as Clave_Aeropuerto, p.clave_internacional as Clave_Pais, year(dv.fecha_hora_salida) as Año, count(dv.cve_vuelos) as Numero_Vuelos
from vuelos as v, aeropuertos as a, ciudades as c, paises as p, detalle_vuelos as dv
where v.cve_aeropuertos__origen = a.cve_aeropuertos and a.cve_ciudades = c.cve_ciudades and c.cve_paises = p.cve_paises and v.cve_vuelos = dv.cve_vuelos
group by a.clave_internacional, p.clave_internacional, year(dv.fecha_hora_salida);

--8.- Numero de vuelos por aerolínea (detalle_vuelos) 
select aer.nombre as Aerolinea, count(dv.cve_vuelos) as Numero_Vuelos
from detalle_vuelos as dv, vuelos as v, aerolineas as aer
where dv.cve_vuelos = v.cve_vuelos and v.cve_aerolineas = aer.cve_aerolineas
group by aer.nombre;

--9.- Numero de vuelos realizados por aerolínea, por cada año. 
select aer.nombre as Aerolinea, year(dv.fecha_hora_salida) as Año, count(dv.cve_vuelos) as Numero_Vuelos
from detalle_vuelos as dv, vuelos as v, aerolineas as aer
where dv.cve_vuelos = v.cve_vuelos and v.cve_aerolineas = aer.cve_aerolineas
group by aer.nombre, year(dv.fecha_hora_salida);

--10.- Numero de personas que viajan por cada estado, muestre los 10 estados de los que más personas viajan. 
select top 10 e.nombre as Estado, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, clientes as c, estados as e
where o.cve_clientes = c.cve_clientes and c.cve_estados = e.cve_estados
group by e.nombre
order by Numero_Personas desc;

--11.- Numero de personas que viajan por cada año 
select year(dv.fecha_hora_salida) as Año, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, detalle_vuelos as dv
where o.cve_detalle_vuelos = dv.cve_detalle_vuelos
group by year(dv.fecha_hora_salida);

--12.- Nombre, ciudad y país de los 10 aeropuertos de los que más personas parten hacia algún destino. 
select top 10 a.nombre as Aeropuerto, c.nombre as Ciudad, p.nombre as Pais, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, detalle_vuelos as dv, vuelos as v, aeropuertos as a, ciudades as c, paises as p
where o.cve_detalle_vuelos = dv.cve_detalle_vuelos and dv.cve_vuelos = v.cve_vuelos and v.cve_aeropuertos__origen = a.cve_aeropuertos and a.cve_ciudades = c.cve_ciudades and c.cve_paises = p.cve_paises
group by a.nombre, c.nombre, p.nombre
order by numero_personas desc;

--13.- Numero de personas que viajan por cada mes.
select year(dv.fecha_hora_salida) as Año, month(dv.fecha_hora_salida) as Mes, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, detalle_vuelos as dv
where o.cve_detalle_vuelos = dv.cve_detalle_vuelos
group by year(dv.fecha_hora_salida), month(dv.fecha_hora_salida)
order by month(dv.fecha_hora_salida);

--14.- Nombre de los 10 municipios de los que más personas viajan, agregue el nombre del estado. 
select top 10 m.nombre as Municipio, e.nombre as Estado, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, clientes as c, municipios as m, estados as e
where o.cve_clientes = c.cve_clientes and c.cve_municipios = m.cve_municipios and m.cve_estados = e.cve_estados
group by m.nombre, e.nombre
order by numero_personas desc;

--15.- Nombre de los 10 municipios de los que menos personas viajan, agregue el nombre del estado. 
select top 10 m.nombre as Municipio, e.nombre as Estado, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, clientes as c, municipios as m, estados as e
where o.cve_clientes = c.cve_clientes and c.cve_municipios = m.cve_municipios and m.cve_estados = e.cve_estados
group by m.nombre, e.nombre
order by numero_personas asc;

--16.- Nombre del o los aeropuertos de los que menos personas parten. Muestro la ciudad y el país al que pertenece.
select a.nombre as Aeropuerto, c.nombre as Ciudad, p.nombre as Pais, count(o.cve_clientes) as Numero_Personas
from ocupaciones as o, detalle_vuelos as dv, vuelos as v, aeropuertos as a, ciudades as c, paises as p
where o.cve_detalle_vuelos = dv.cve_detalle_vuelos and dv.cve_vuelos = v.cve_vuelos and v.cve_aeropuertos__origen = a.cve_aeropuertos and a.cve_ciudades = c.cve_ciudades and c.cve_paises = p.cve_paises
group by a.nombre, c.nombre, p.nombre
order by numero_personas asc;