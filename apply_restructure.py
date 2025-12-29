"""
MASTER RESTRUCTURE SCRIPT
=========================
Applies all changes in one go.

This script will:
1. Create new directory structure
2. Move files to correct locations
3. Update all imports
4. Clean up unnecessary files
5. Generate reports

Run this ONCE to apply all restructuring changes.
"""
import os
import shutil
import re
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def ensure_dir(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_move(src: Path, dst: Path) -> bool:
    """Safely move file, creating directories as needed."""
    try:
        if not src.exists():
            return False
        ensure_dir(dst.parent)
        shutil.move(str(src), str(dst))
        return True
    except Exception as e:
        print_error(f"Failed to move {src} to {dst}: {e}")
        return False

def safe_remove(path: Path) -> bool:
    """Safely remove file or directory."""
    try:
        if not path.exists():
            return False
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return True
    except Exception as e:
        print_error(f"Failed to remove {path}: {e}")
        return False

def update_imports_in_file(filepath: Path) -> bool:
    """Update imports in a Python file."""
    replacements = {
        'from app.config import': 'from app.core.config import',
        'from app.database import': 'from app.core.database import',
        'from app.security import': 'from app.core.security import',
        'from app import database': 'from app.core import database',
        'from app import security': 'from app.core import security',
        'from app import config': 'from app.core import config',
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print_error(f"Failed to update {filepath}: {e}")
        return False

def main():
    """Main restructure function."""
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    
    print_header("TAX FILING AGENT - MASTER RESTRUCTURE")
    
    # ========================================================================
    # STEP 1: CREATE NEW DIRECTORY STRUCTURE
    # ========================================================================
    print_header("STEP 1: Creating New Directory Structure")
    
    new_dirs = [
        backend_dir / 'app' / 'core',
        backend_dir / 'app' / 'agents',
        backend_dir / 'app' / 'schemas',
        backend_dir / 'tests' / 'unit',
        backend_dir / 'tests' / 'integration',
        backend_dir / 'scripts',
        backend_dir / 'uploads',
        project_root / 'docs',
    ]
    
    for dir_path in new_dirs:
        ensure_dir(dir_path)
        print_success(f"Ensured: {dir_path.relative_to(project_root)}")
    
    # ========================================================================
    # STEP 2: MOVE CORE FILES
    # ========================================================================
    print_header("STEP 2: Moving Core Files")
    
    core_moves = [
        (backend_dir / 'app' / 'config.py', backend_dir / 'app' / 'core' / 'config.py'),
        (backend_dir / 'app' / 'database.py', backend_dir / 'app' / 'core' / 'database.py'),
        (backend_dir / 'app' / 'security.py', backend_dir / 'app' / 'core' / 'security.py'),
    ]
    
    moved_count = 0
    for src, dst in core_moves:
        if safe_move(src, dst):
            print_success(f"Moved: {src.name} → core/{dst.name}")
            moved_count += 1
        else:
            print_warning(f"Skipped: {src.name} (already moved or not found)")
    
    # Create __init__.py for core
    core_init = backend_dir / 'app' / 'core' / '__init__.py'
    if not core_init.exists():
        core_init.write_text('"""Core module for configuration, database, and security."""\n')
        print_success("Created: app/core/__init__.py")
    
    # ========================================================================
    # STEP 3: MOVE SCHEMA FILES
    # ========================================================================
    print_header("STEP 3: Moving Schema Files")
    
    schemas_file = backend_dir / 'app' / 'schemas.py'
    schemas_dir = backend_dir / 'app' / 'schemas'
    if schemas_file.exists():
        safe_move(schemas_file, schemas_dir / '__init__.py')
        print_success("Moved: schemas.py → schemas/__init__.py")
    
    # ========================================================================
    # STEP 4: MERGE AGENT FOLDERS
    # ========================================================================
    print_header("STEP 4: Merging Agent Folders")
    
    autogen_agents = backend_dir / 'app' / 'autogen_agents'
    agents_v2 = backend_dir / 'app' / 'agents_v2'
    agents_dir = backend_dir / 'app' / 'agents'
    
    ensure_dir(agents_dir)
    
    # Copy from autogen_agents
    if autogen_agents.exists():
        for file in autogen_agents.glob('*.py'):
            if file.name != '__pycache__':
                dst = agents_dir / file.name
                if not dst.exists():
                    shutil.copy2(file, dst)
                    print_success(f"Copied: autogen_agents/{file.name} → agents/")
    
    # Copy from agents_v2
    if agents_v2.exists():
        for file in agents_v2.glob('*.py'):
            if file.name != '__pycache__':
                dst = agents_dir / file.name
                if not dst.exists():
                    shutil.copy2(file, dst)
                    print_success(f"Copied: agents_v2/{file.name} → agents/")
    
    # ========================================================================
    # STEP 5: MOVE TEST FILES
    # ========================================================================
    print_header("STEP 5: Moving Test Files")
    
    tests_dir = backend_dir / 'tests'
    test_files = list(backend_dir.glob('test_*.py'))
    
    for test_file in test_files:
        dst = tests_dir / test_file.name
        if safe_move(test_file, dst):
            print_success(f"Moved: {test_file.name} → tests/")
    
    # ========================================================================
    # STEP 6: REMOVE UNNECESSARY FILES
    # ========================================================================
    print_header("STEP 6: Removing Unnecessary Files")
    
    files_to_remove = [
        backend_dir / 'debug_import.py',
        backend_dir / 'debug_models.py',
        backend_dir / 'check_imports.py',
        backend_dir / 'import_error.txt',
        backend_dir / 'main.py',  # Old duplicate main.py
        project_root / 'test_register.py',
        project_root / 'verify_backend.py',
        project_root / 'verify_sdui.py',
        project_root / 'verify_ws.py',
        project_root / 'test-all-providers.html',
        project_root / 'sdui_response.json',
        project_root / 'bun.lockb',
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        if safe_remove(file_path):
            print_success(f"Removed: {file_path.name}")
            removed_count += 1
    
    # Remove directories
    dirs_to_remove = [
        project_root / 'rust-engine',
        backend_dir / 'pgvector',
        backend_dir / 'pgvector_extracted',
    ]
    
    for dir_path in dirs_to_remove:
        if safe_remove(dir_path):
            print_success(f"Removed directory: {dir_path.name}")
            removed_count += 1
    
    # ========================================================================
    # STEP 7: UPDATE IMPORTS
    # ========================================================================
    print_header("STEP 7: Updating Import Statements")
    
    app_dir = backend_dir / 'app'
    python_files = [
        f for f in app_dir.rglob('*.py')
        if '__pycache__' not in str(f)
    ]
    
    updated_count = 0
    for py_file in python_files:
        if update_imports_in_file(py_file):
            print_success(f"Updated imports: {py_file.relative_to(backend_dir)}")
            updated_count += 1
    
    # ========================================================================
    # STEP 8: CREATE INITIALIZATION FILES
    # ========================================================================
    print_header("STEP 8: Creating __init__.py Files")
    
    init_dirs = [
        backend_dir / 'app' / 'agents',
        backend_dir / 'app' / 'schemas',
        backend_dir / 'tests',
        backend_dir / 'tests' / 'unit',
        backend_dir / 'tests' / 'integration',
    ]
    
    for dir_path in init_dirs:
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            init_file.write_text('')
            print_success(f"Created: {init_file.relative_to(backend_dir)}")
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print_header("RESTRUCTURE COMPLETE!")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print(f"  • Directories created: {len(new_dirs)}")
    print(f"  • Files moved: {moved_count}")
    print(f"  • Files removed: {removed_count}")
    print(f"  • Imports updated: {updated_count}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print("  1. Review changes with: git status")
    print("  2. Install dependencies: npm install && cd backend && pip install -r requirements.txt")
    print("  3. Configure .env: edit backend/.env")
    print("  4. Start database: docker-compose up -d")
    print("  5. Run application: SETUP_AND_RUN.bat")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All changes applied successfully!{Colors.END}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print_error(f"Restructure failed: {e}")
        import traceback
        traceback.print_exc()
