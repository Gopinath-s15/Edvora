"""
Setup script for Edvora - AI Document Reasoning System
Automates the setup process for development and deployment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    success = run_command("python -m venv venv", "Creating virtual environment")
    return success is not None

def get_activation_command():
    """Get the correct activation command for the platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    if platform.system() == "Windows":
        pip_command = "venv\\Scripts\\pip"
    else:
        pip_command = "venv/bin/pip"
    
    # Upgrade pip first
    run_command(f"{pip_command} install --upgrade pip", "Upgrading pip")
    
    # Install dependencies
    success = run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")
    return success is not None

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("📁 .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy template
    with open(env_example, 'r') as src, open(env_file, 'w') as dst:
        content = src.read()
        dst.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file and add your OpenAI API key")
    return True

def validate_setup():
    """Validate the setup by running basic checks"""
    print("\n🔍 Validating setup...")
    
    # Check if main files exist
    required_files = ["main.py", "retriever.py", "llm_logic.py", "utils.py", "requirements.txt"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing required file: {file}")
            return False
        print(f"✅ Found {file}")
    
    # Check .env file
    if not Path(".env").exists():
        print("⚠️  .env file not found - you'll need to create it manually")
    else:
        print("✅ .env file exists")
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    activation_cmd = get_activation_command()
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n📋 Next Steps:")
    print(f"1. Activate virtual environment: {activation_cmd}")
    print("2. Edit .env file and add your OpenAI API key:")
    print("   OPENAI_API_KEY=your_openai_api_key_here")
    print("3. Start the application:")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("4. Open your browser and go to:")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/health")
    print("\n🧪 Testing:")
    print("   python tests/test_examples.py")
    print("\n📚 Documentation:")
    print("   See README.md for detailed usage instructions")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 Edvora Setup Script")
    print("Setting up AI-Powered Document Reasoning System")
    print("="*60)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Step 4: Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Step 5: Validate setup
    if not validate_setup():
        print("❌ Setup validation failed")
        sys.exit(1)
    
    # Step 6: Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
