from groq import Groq
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

class LLMClient:
    """Cliente para interactuar con Groq API (compatible con OpenAI)"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY no encontrada en .env")
        
        self.client = Groq(api_key=api_key)
    
    def generate(
        self,
        prompt: str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_message: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Genera una respuesta usando el modelo especificado.
        
        Args:
            prompt: El prompt principal
            model: Modelo a usar
            temperature: Creatividad (0-1)
            max_tokens: Máximo de tokens a generar
            system_message: Mensaje de sistema opcional
            stream: Si True, retorna un generator para streaming
        
        Returns:
            Respuesta generada por el modelo
        """
        messages: List[Dict[str, str]] = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            if not stream:
                # Modo normal (sin streaming)
                console.print(f'[dim]🤖 Calling {model} via Groq...[/dim]')
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content.strip()
            
            else:
                # Modo streaming
                console.print(f'[dim]🤖 Streaming from {model} via Groq...[/dim]')
                console.print()
                
                stream_response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                full_response = ""
                
                for chunk in stream_response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        # Imprimir en tiempo real
                        console.print(content, end='', style='cyan')
                
                console.print()  # Salto de línea final
                console.print()
                
                return full_response.strip()
        
        except Exception as e:
            console.print(f'[red]❌ Error calling LLM: {e}[/red]')
            raise
    
    def count_tokens_estimate(self, text: str) -> int:
        """
        Estimación simple de tokens (aproximadamente 4 chars = 1 token)
        """
        return len(text) // 4
