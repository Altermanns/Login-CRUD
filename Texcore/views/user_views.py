"""
User management views - CRUD operations for users (Admin only).
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib import messages
from ..models import Profile
from ..decorators import admin_required


@admin_required
def listar_usuarios(request):
    """List all users with their roles - Admin only."""
    usuarios = User.objects.select_related('profile').all().order_by('username')
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'usuarios/lista.html', context)


@admin_required  
def crear_usuario(request):
    """Create new user with role assignment - Admin only."""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        
        # Validations
        if not all([username, first_name, last_name, email, password, role]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/crear.html')
        
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'usuarios/crear.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'usuarios/crear.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'usuarios/crear.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Assign role
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            
            messages.success(
                request, 
                f'Usuario {username} creado exitosamente con rol {profile.get_role_display()}.'
            )
            return redirect('listar_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return render(request, 'usuarios/crear.html')
    
    return render(request, 'usuarios/crear.html')


@admin_required
def editar_usuario(request, user_id):
    """Edit existing user and role - Admin only."""
    usuario = get_object_or_404(User, pk=user_id)
    
    # Don't allow admin to edit themselves to avoid lockouts
    if usuario == request.user:
        messages.warning(request, 'No puedes editar tu propio usuario.')
        return redirect('listar_usuarios')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validations
        if not all([first_name, last_name, email, role]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})
        
        # Check unique email (excluding current user)
        if User.objects.filter(email=email).exclude(pk=usuario.pk).exists():
            messages.error(request, 'El email ya está registrado por otro usuario.')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})
        
        try:
            # Update user
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.email = email
            usuario.is_active = is_active
            usuario.save()
            
            # Update role
            profile, created = Profile.objects.get_or_create(user=usuario)
            profile.role = role
            profile.save()
            
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
            return redirect('listar_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    return render(request, 'usuarios/editar.html', {'usuario': usuario})


@admin_required
@require_POST
def eliminar_usuario(request, user_id):
    """Delete user (soft delete by deactivating) - Admin only."""
    usuario = get_object_or_404(User, pk=user_id)
    
    # Don't allow deleting own user
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('listar_usuarios')
    
    # Soft delete - just deactivate
    usuario.is_active = False
    usuario.save()
    
    messages.success(request, f'Usuario {usuario.username} desactivado exitosamente.')
    return redirect('listar_usuarios')
