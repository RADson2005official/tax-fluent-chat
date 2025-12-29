"""
Backend Structure Update Script
================================
Updates all imports after restructuring to use core module.
"""
import os
import re
from pathlib import Path

# Define replacements
REPLACEMENTS = {
    'from app.config import': 'from app.core.config import',
    'from app.database import': 'from app.core.database import',
    'from app.security import': 'from app.core.security import',
    'from app import database': 'from app.core import database',
    'from app import security': 'from app.core import security',
    'from app import config': 'from app.core import config',
}

def update_imports_in_file(filepath: Path):
    """Update imports in a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {filepath.relative_to(Path.cwd())}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def main():
    """Main function to update all Python files."""
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / 'app'
    
    if not app_dir.exists():
        print("❌ app directory not found!")
        return
    
    # Find all Python files
    python_files = list(app_dir.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files to check...")
    print("="*60)
    
    updated_count = 0
    for py_file in python_files:
        if '__pycache__' in str(py_file):
            continue
        if update_imports_in_file(py_file):
            updated_count += 1
    
    print("="*60)
    print(f"✅ Updated {updated_count} files")
    
    # Also update main.py if it exists
    main_py = backend_dir / 'main.py'
    if main_py.exists():
        if update_imports_in_file(main_py):
            print("✅ Updated main.py")

if __name__ == '__main__':
    main()
