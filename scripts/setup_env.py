import os
import sys
import subprocess
import platform

def create_venv():
    """Create a virtual environment in parent directory"""
    parent_dir = os.path.dirname(os.getcwd())  # Go up one level from scripts folder
    venv_path = os.path.join(parent_dir, "venv")
    
    print(f"Creating virtual environment at '{venv_path}'...")
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print(f"✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating virtual environment: {e}")
        return False

def get_activation_command():
    """Get the appropriate activation command based on OS"""
    system = platform.system().lower()
    
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:  # Linux/Mac
        return "source venv/bin/activate"

def install_requirements():
    """Install requirements in the activated virtual environment"""
    parent_dir = os.path.dirname(os.getcwd())  # Go up one level from scripts folder
    system = platform.system().lower()
    
    if system == "windows":
        pip_path = os.path.join(parent_dir, "venv", "Scripts", "pip")
    else:  # Linux/Mac
        pip_path = os.path.join(parent_dir, "venv", "bin", "pip")
    
    requirements_path = os.path.join(parent_dir, "requirements.txt")
    
    print("Installing requirements...")
    try:
        subprocess.run([pip_path, "install", "-r", requirements_path], check=True)
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def main():
    """Main function to set up the environment"""
    print("Setting up Python virtual environment...")
    print("-" * 40)
    
    parent_dir = os.path.dirname(os.getcwd())  # Go up one level from scripts folder
    requirements_path = os.path.join(parent_dir, "requirements.txt")
    venv_path = os.path.join(parent_dir, "venv")
    
    # Check if requirements.txt exists in parent directory
    if not os.path.exists(requirements_path):
        print(f"✗ requirements.txt not found in parent directory: {parent_dir}")
        sys.exit(1)
    
    # Check if venv already exists in parent directory
    if os.path.exists(venv_path):
        print("Virtual environment 'venv' already exists in parent directory")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            import shutil
            shutil.rmtree(venv_path)
            print("Removed existing virtual environment")
        else:
            print("Using existing virtual environment")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_path):
        if not create_venv():
            sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    print("-" * 40)
    print("✓ Setup completed successfully!")
    print(f"\nVirtual environment created at: {venv_path}")
    print(f"Requirements installed from: {requirements_path}")
    print("\nTo activate the virtual environment, run:")
    print(f"  {get_activation_command()}")
    print("\nTo deactivate, run:")
    print("  deactivate")

if __name__ == "__main__":
    main()