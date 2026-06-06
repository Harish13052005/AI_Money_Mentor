#!/usr/bin/env python3
"""
Multi-Provider LLM Setup Script
Helps you configure API keys and test provider connectivity.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(msg: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_warning(msg: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_info(msg: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def test_groq(api_key: str) -> bool:
    """Test Groq API connection."""
    try:
        from groq import Groq
        
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
        )
        return True
    except ImportError:
        print_warning("groq library not installed. Install with: pip install groq")
        return False
    except Exception as e:
        print_error(f"Groq connection failed: {str(e)}")
        return False


def test_together(api_key: str) -> bool:
    """Test Together AI API connection."""
    try:
        import together
        
        together.api_key = api_key
        response = together.Complete.create(
            prompt="test",
            model="mistralai/Mistral-7B-Instruct-v0.1",
            max_tokens=1,
        )
        return True
    except ImportError:
        print_warning("together library not installed. Install with: pip install together")
        return False
    except Exception as e:
        print_error(f"Together AI connection failed: {str(e)}")
        return False


def test_huggingface(api_key: str) -> bool:
    """Test HuggingFace API connection."""
    try:
        import requests
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            "https://api-inference.huggingface.co/api/whoami",
            headers=headers,
            timeout=5
        )
        return response.status_code == 200
    except ImportError:
        print_warning("requests library not installed. Install with: pip install requests")
        return False
    except Exception as e:
        print_error(f"HuggingFace connection failed: {str(e)}")
        return False


def test_openai(api_key: str) -> bool:
    """Test OpenAI API connection."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
        )
        return True
    except ImportError:
        print_warning("openai library not installed. Install with: pip install openai")
        return False
    except Exception as e:
        print_error(f"OpenAI connection failed: {str(e)}")
        return False


def load_env_file() -> dict:
    """Load current .env file."""
    env_path = Path(".env")
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
    
    return env_vars


def save_env_file(env_vars: dict) -> None:
    """Save environment variables to .env file."""
    env_path = Path(".env")
    
    with open(env_path, "w") as f:
        f.write("# AI Money Mentor - Multi-Provider LLM Configuration\n")
        f.write("# Auto-generated configuration file\n\n")
        
        f.write("# Primary provider selection\n")
        f.write(f"AI_PROVIDER={env_vars.get('AI_PROVIDER', 'groq')}\n\n")
        
        f.write("# API Keys\n")
        f.write(f"GROQ_API_KEY={env_vars.get('GROQ_API_KEY', 'your-groq-api-key')}\n")
        f.write(f"TOGETHER_API_KEY={env_vars.get('TOGETHER_API_KEY', 'your-together-api-key')}\n")
        f.write(f"HUGGINGFACE_API_KEY={env_vars.get('HUGGINGFACE_API_KEY', 'your-huggingface-api-key')}\n")
        f.write(f"OPENAI_API_KEY={env_vars.get('OPENAI_API_KEY', 'your-openai-api-key')}\n")


def main():
    """Main setup wizard."""
    print_header("🚀 AI Money Mentor - Multi-Provider LLM Setup")
    
    print_info("This wizard will help you configure LLM providers.")
    print_info("You can use FREE options (Groq, Together AI, HuggingFace)")
    print_info("or keep your existing OpenAI key as fallback.\n")
    
    # Load existing configuration
    env_vars = load_env_file()
    
    if env_vars:
        print_info(f"Found existing configuration with {len(env_vars)} variables")
    
    # Provider selection
    print_header("Provider Setup")
    
    providers = {
        "groq": {
            "name": "Groq",
            "recommended": True,
            "url": "https://console.groq.com",
            "info": "Fastest free LLM (30 req/min)"
        },
        "together": {
            "name": "Together AI",
            "recommended": False,
            "url": "https://www.together.ai",
            "info": "Free tier with $5 credits"
        },
        "huggingface": {
            "name": "HuggingFace",
            "recommended": False,
            "url": "https://huggingface.co",
            "info": "Free inference API"
        },
        "openai": {
            "name": "OpenAI",
            "recommended": False,
            "url": "https://platform.openai.com",
            "info": "Fallback option (paid)"
        }
    }
    
    for provider_id, provider_info in providers.items():
        print(f"\n{Colors.BOLD}{provider_info['name']}{Colors.END}")
        print(f"  → {provider_info['info']}")
        if provider_info['recommended']:
            print(f"  {Colors.GREEN}(RECOMMENDED){Colors.END}")
        
        existing_key = env_vars.get(f"{provider_id.upper()}_API_KEY", "")
        if existing_key and existing_key != f"your-{provider_id}-api-key":
            print(f"  {Colors.GREEN}✓ API Key found{Colors.END}")
        
        print(f"  Sign up: {provider_info['url']}")
    
    # Interactive setup
    print("\n")
    setup = input(f"{Colors.BOLD}Would you like to configure API keys? (y/n): {Colors.END}").lower()
    
    if setup == 'y':
        for provider_id in providers.keys():
            print(f"\n{Colors.BOLD}Enter your {providers[provider_id]['name']} API Key:{Colors.END}")
            print(f"  (or press Enter to skip)")
            
            api_key = input(f"  API Key: ").strip()
            
            if api_key:
                env_vars[f"{provider_id.upper()}_API_KEY"] = api_key
                
                # Test connection
                print(f"  Testing connection...")
                test_func = globals().get(f"test_{provider_id}")
                
                if test_func and test_func(api_key):
                    print_success(f"{providers[provider_id]['name']} connection successful!")
                else:
                    print_warning(f"{providers[provider_id]['name']} connection failed")
    
    # Save configuration
    print("\n")
    save_config = input(f"{Colors.BOLD}Save configuration to .env? (y/n): {Colors.END}").lower()
    
    if save_config == 'y':
        save_env_file(env_vars)
        print_success("Configuration saved to .env")
    
    # Summary
    print_header("Setup Summary")
    
    available_providers = []
    for provider_id in providers.keys():
        if env_vars.get(f"{provider_id.upper()}_API_KEY", "").startswith(("gsk_", "key_", "hf_", "sk_")):
            available_providers.append(provider_id)
    
    if available_providers:
        print_success(f"Available providers: {', '.join(available_providers)}")
        primary = env_vars.get("AI_PROVIDER", "groq")
        print_info(f"Primary provider: {primary}")
    else:
        print_error("No providers configured!")
        print_info("Please configure at least one provider to use the system")
    
    print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
    print("  1. pip install -r requirements.txt")
    print("  2. python main.py (backend)")
    print("  3. streamlit run app.py (frontend)")
    print("  4. GET http://192.168.0.39:8000/health (check providers)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)
