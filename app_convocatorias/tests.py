from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import Convocatoria


class ConvocatoriaCuposIntegracionTestCase(TestCase):

    def setUp(self):
        # Crear grupo de administradores
        self.grupo = Group.objects.create(name='Administradores')

        # Crear usuario administrador
        self.usuario_admin = User.objects.create_user(
            username='admin',
            password='admin123'
        )

        # Asignar usuario al grupo
        self.usuario_admin.groups.add(self.grupo)

        # Iniciar sesión
        self.client.login(
            username='admin',
            password='admin123'
        )

        # Datos válidos para registrar una convocatoria
        self.datos_convocatoria = {
            'titulo': 'Curso Python Avanzado',
            'area': 'Tecnología',
            'descripcion': 'Capacitación en desarrollo backend',
            'fecha_inicio': '2026-11-15',
            'fecha_final': '2026-11-30',
            'ciudad': 'Pereira',
            'cupos_totales': '0',
        }

    def test_cupos_totales_negativos_integracion(self):
        """
        Escenario A:
        Validar que no se permita registrar una convocatoria
        con cupos totales negativos.
        """

        # Consultar formulario
        respuesta = self.client.get('/convocatorias/crear/')

        self.assertEqual(respuesta.status_code, 200)

        self.assertTemplateUsed(
            respuesta,
            'app_convocatorias/app_convocatorias_form.html'
        )

        # Enviar cupos totales negativos
        datos = self.datos_convocatoria.copy()
        datos['cupos_totales'] = '-5'

        respuesta_post = self.client.post(
            '/convocatorias/crear/',
            datos
        )

        # Verificar que el formulario presenta un error
        self.assertEqual(respuesta_post.status_code, 200)

        self.assertContains(
            respuesta_post,
            'Los cupos totales deben ser mayores o iguales a cero.'
        )

        # Verificar que NO se creó la convocatoria
        self.assertEqual(Convocatoria.objects.count(), 0)

    def test_cupos_totales_cero_integracion(self):
        """
        Escenario B:
        Validar que se permita registrar una convocatoria
        con cero cupos totales y cero cupos asignados.
        """

        # Consultar formulario
        respuesta = self.client.get('/convocatorias/crear/')

        self.assertEqual(respuesta.status_code, 200)

        self.assertTemplateUsed(
            respuesta,
            'app_convocatorias/app_convocatorias_form.html'
        )

        # Enviar convocatoria con cero cupos
        respuesta_post = self.client.post(
            '/convocatorias/crear/',
            self.datos_convocatoria
        )

        # Verificar que se creó el registro
        self.assertEqual(Convocatoria.objects.count(), 1)

        # Consultar convocatoria registrada
        convocatoria = Convocatoria.objects.first()

        # Validar información registrada
        self.assertEqual(
            convocatoria.titulo,
            'Curso Python Avanzado'
        )

        self.assertEqual(convocatoria.cupos_totales, 0)

        self.assertEqual(convocatoria.cupos_asignados, 0)

        self.assertEqual(convocatoria.estado, 'Borrador')

        # Verificar redirección
        self.assertEqual(respuesta_post.status_code, 302)

        self.assertRedirects(
            respuesta_post,
            '/convocatorias/'
        )

        # Consultar listado de convocatorias
        respuesta_convocatorias = self.client.get('/convocatorias/')

        self.assertContains(
            respuesta_convocatorias,
            'Curso Python Avanzado'
        )