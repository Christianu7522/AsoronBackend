from django.core.mail import send_mail

def enviar_correo(username,password,email):
    asunto = 'Bienvenido a ASORON'
    mensaje = f'Bienvenido a ASORON,\n\nEstas son tus credenciales:\n\nUsuario: {username}\nContraseña: {password}\nCorreo Electrónico: {email}\n\nSi deseas cambiar tu contraseña, entra a la página y presiona "He olvidado mi contraseña".'

    send_mail(
        asunto,
        mensaje,
        'programucabch7@gmail.com',
        [email],  
        fail_silently=False,  
    )
