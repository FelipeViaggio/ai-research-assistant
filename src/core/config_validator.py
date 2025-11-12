'''
Validador de configuración del sistema
'''
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

console = Console()

class ConfigValidator:
    '''Valida la configuración antes de ejecutar el sistema'''
    
    @staticmethod
    def validate_all() -> bool:
        '''
        Valida toda la configuración necesaria.
        Retorna True si todo está OK, False si hay errores.
        '''
        console.print()
        console.print('[bold cyan]🔍 Validando configuración del sistema...[/bold cyan]')
        console.print()
        
        errors = []
        warnings = []
        
        # Validar .env existe
        if not os.path.exists('.env'):
            errors.append('Archivo .env no encontrado')
            errors.append('  → Copiá .env.example a .env y configurá tu API key')
        else:
            load_dotenv()
        
        # Validar API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            errors.append('GROQ_API_KEY no configurada en .env')
            errors.append('  → Agregá: GROQ_API_KEY=tu-key-aqui')
        elif api_key == 'your-api-key-here' or api_key == 'TU_API_KEY_AQUI':
            errors.append('GROQ_API_KEY tiene el valor por defecto')
            errors.append('  → Reemplazala con tu API key real de Groq')
        elif not api_key.startswith('gsk_'):
            warnings.append('GROQ_API_KEY no tiene el formato esperado (debería empezar con gsk_)')
        else:
            console.print('[green]✓[/green] GROQ_API_KEY configurada correctamente')
        
        # Validar modelos configurados
        cheap_model = os.getenv('MODEL_CHEAP')
        moderate_model = os.getenv('MODEL_MODERATE')
        expensive_model = os.getenv('MODEL_EXPENSIVE')
        
        if cheap_model:
            console.print(f'[green]✓[/green] Modelo barato: {cheap_model}')
        else:
            warnings.append('MODEL_CHEAP no configurado, usando default')
        
        if expensive_model:
            console.print(f'[green]✓[/green] Modelo caro: {expensive_model}')
        else:
            warnings.append('MODEL_EXPENSIVE no configurado, usando default')
        
        # Validar conectividad (básico)
        if api_key and api_key.startswith('gsk_'):
            console.print('[green]✓[/green] API key tiene formato válido')
        
        # Mostrar warnings
        if warnings:
            console.print()
            console.print('[yellow]⚠️  Advertencias:[/yellow]')
            for warning in warnings:
                console.print(f'  [yellow]•[/yellow] {warning}')
        
        # Mostrar errores
        if errors:
            console.print()
            console.print('[red]❌ Errores de configuración:[/red]')
            for error in errors:
                console.print(f'  [red]{error}[/red]')
            console.print()
            
            # Panel con instrucciones
            help_text = '''[bold]Para configurar el sistema:[/bold]

1. Copiá .env.example a .env:
   [cyan]cp .env.example .env[/cyan]

2. Conseguí tu API key de Groq:
   [cyan]https://console.groq.com/[/cyan]

3. Editá .env y agregá tu key:
   [cyan]GROQ_API_KEY=gsk_tu_key_aqui[/cyan]

4. Ejecutá de nuevo el programa
'''
            console.print(Panel(help_text, border_style='red', title='[bold red]Configuración Requerida[/bold red]'))
            
            return False
        
        console.print()
        console.print('[bold green]✓ Configuración válida[/bold green]')
        console.print()
        
        return True
    
    @staticmethod
    def test_api_connection() -> bool:
        '''
        Intenta una llamada de prueba a la API.
        Opcional: solo si querés verificar conectividad real.
        '''
        try:
            from groq import Groq
            import os
            
            client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            
            # Llamada mínima de prueba
            response = client.chat.completions.create(
                model='llama-3.1-8b-instant',
                messages=[{'role': 'user', 'content': 'test'}],
                max_tokens=5
            )
            
            console.print('[green]✓[/green] Conexión con Groq API exitosa')
            return True
        
        except Exception as e:
            console.print(f'[red]✗[/red] Error al conectar con Groq: {e}')
            return False
