import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
import django
django.setup()

from cooperativa.models import Usuario, UsuarioRol, Rol

print('=== USUARIOS Y SUS ROLES ===')
for usuario in Usuario.objects.all():
    print(f'Usuario: {usuario.usuario} - {usuario.nombres} {usuario.apellidos}')
    roles_usuario = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')
    if roles_usuario.exists():
        for ur in roles_usuario:
            print(f'  Rol: {ur.rol.nombre}')
            permisos = ur.rol.permisos
            if 'semillas' in permisos:
                print(f'    Permisos semillas: {permisos["semillas"]}')
            if 'pesticidas' in permisos:
                print(f'    Permisos pesticidas: {permisos["pesticidas"]}')
            if 'fertilizantes' in permisos:
                print(f'    Permisos fertilizantes: {permisos["fertilizantes"]}')
    else:
        print('  Sin roles asignados')
    print()