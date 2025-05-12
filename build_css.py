import subprocess
import os

def build_tailwind():
    """Build Tailwind CSS."""
    print("Building Tailwind CSS...")
    
    # Ensure output directory exists
    os.makedirs('app/static/css', exist_ok=True)
    
    # Build Tailwind CSS
    try:
        subprocess.run([
            'npx', 
            'tailwindcss', 
            '-i', 'app/static/css/input.css', 
            '-o', 'app/static/css/style.css',
            '--minify'
        ], check=True)
        print("Tailwind CSS built successfully!")
    except subprocess.CalledProcessError:
        print("Error: Failed to build Tailwind CSS.")
        print("Make sure you have Node.js and npm installed.")
        print("Try running: npm install -D tailwindcss")

if __name__ == "__main__":
    build_tailwind()