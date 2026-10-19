from django.db import models


class Carrera(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre de la Carrera")
    duracion_teorica = models.PositiveIntegerField(default=5, verbose_name="Duración Teórica (Años)")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Egresado(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    numero_egresado = models.IntegerField(primary_key=True, verbose_name="N° de Egresado")
    nombres = models.CharField(max_length=150, verbose_name="Nombres")
    apellidos = models.CharField(max_length=150, verbose_name="Apellidos")
    cin = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad (CIN)")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    lugar_nacimiento = models.CharField(max_length=100, verbose_name="Lugar de Nacimiento")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='egresados', verbose_name="Carrera")
    anio_ingreso = models.PositiveIntegerField(verbose_name="Año de Ingreso")
    anio_egreso = models.PositiveIntegerField(verbose_name="Año de Egreso")
    link_repositorio = models.URLField(blank=True, null=True, max_length=500, verbose_name="Link al Repositorio")

    class Meta:
        verbose_name = "Egresado"
        verbose_name_plural = "Egresados"
        ordering = ['numero_egresado']

    def __str__(self):
        return f"#{self.numero_egresado} - {self.nombres} {self.apellidos} ({self.carrera})"

    @property
    def duracion_carrera(self):
        if self.anio_egreso and self.anio_ingreso:
            return self.anio_egreso - self.anio_ingreso
        return None

    @property
    def edad_egreso(self):
        if self.fecha_nacimiento and self.anio_egreso:
            return self.anio_egreso - self.fecha_nacimiento.year
        return None


class CohorteIngresantes(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='cohortes', verbose_name="Carrera")
    anio_cohorte = models.PositiveIntegerField(verbose_name="Año de Cohorte (Ingreso)")
    cantidad_ingresantes = models.PositiveIntegerField(default=0, verbose_name="Cantidad Total de Ingresantes")
    cantidad_masculino = models.PositiveIntegerField(default=0, verbose_name="Ingresantes Masculinos")
    cantidad_femenino = models.PositiveIntegerField(default=0, verbose_name="Ingresantes Femeninos")

    class Meta:
        verbose_name = "Cohorte de Ingresantes"
        verbose_name_plural = "Cohortes de Ingresantes"
        unique_together = ('carrera', 'anio_cohorte')
        ordering = ['-anio_cohorte', 'carrera__nombre']

    def __str__(self):
        return f"{self.carrera.nombre} ({self.anio_cohorte}): {self.cantidad_ingresantes} ingresantes (M: {self.cantidad_masculino}, F: {self.cantidad_femenino})"

    def save(self, *args, **kwargs):
        # Si se ingresaron cantidades por sexo pero no el total o es menor a la suma
        suma_sexos = (self.cantidad_masculino or 0) + (self.cantidad_femenino or 0)
        if suma_sexos > 0 and (not self.cantidad_ingresantes or self.cantidad_ingresantes < suma_sexos):
            self.cantidad_ingresantes = suma_sexos
        super().save(*args, **kwargs)

