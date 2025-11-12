from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from Texcore.models import Profile


class Command(BaseCommand):
    help = 'Crear usuario con rol específico para el sistema TextilApp'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario')
        parser.add_argument('email', type=str, help='Email del usuario')
        parser.add_argument('password', type=str, help='Contraseña')
        parser.add_argument(
            '--role',
            type=str,
            choices=['operario', 'admin'],
            default='operario',
            help='Rol del usuario (operario o admin)'
        )
        parser.add_argument(
            '--first_name',
            type=str,
            default='',
            help='Nombre del usuario'
        )
        parser.add_argument(
            '--last_name',
            type=str,
            default='',
            help='Apellido del usuario'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Crear como superusuario de Django'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        role = options['role']
        first_name = options['first_name']
        last_name = options['last_name']
        is_superuser = options['superuser']

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            raise CommandError(f'El usuario "{username}" ya existe.')

        # Crear el usuario
        try:
            if is_superuser:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                
                # Crear o actualizar perfil
                profile, created = Profile.objects.get_or_create(user=user)
                profile.role = role
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Superusuario "{username}" creado exitosamente con rol "{role}".'
                    )
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Crear o actualizar perfil
                profile, created = Profile.objects.get_or_create(user=user)
                profile.role = role
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuario "{username}" creado exitosamente con rol "{role}".'
                    )
                )

            # Mostrar información del usuario creado
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Nombre: {user.first_name} {user.last_name}')
            self.stdout.write(f'  Rol: {profile.get_role_display()}')
            if is_superuser:
                self.stdout.write(f'  Superusuario: Sí')

        except Exception as e:
            raise CommandError(f'Error al crear el usuario: {str(e)}')