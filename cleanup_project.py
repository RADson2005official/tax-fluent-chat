"""
Complete Project Cleanup and Optimization Script
=================================================
Removes unnecessary files and optimizes project structure.
"""
import os
import shutil
from pathlib import Path

# Files to remove (debug, test scripts in wrong locations)
FILES_TO_REMOVE = [
    'backend/debug_import.py',
    'backend/debug_models.py',
    'backend/check_imports.py',
    'backend/import_error.txt',
    'backend/test_autogen.py',
    'backend/test_comprehensive_uat.py',
    'backend/test_conversational_filing.py',
    'backend/test_core_functionality.py',
    'backend/test_crud_completion.py',
    'backend/test_db_connection.py',
    'backend/test_hashing.py',
    'verify_backend.py',
    'verify_sdui.py',
    'verify_ws.py',
    'test_register.py',
    'test-all-providers.html',
    'sdui_response.json',
    'bun.lockb',  # Not using Bun
]

# Directories to remove
DIRS_TO_REMOVE = [
    'rust-engine',  # Incomplete/unused
    'backend/pgvector',
    'backend/pgvector_extracted',
    'backend/pgvector.zip',
]

# Optional documentation files (can keep but organize)
DOCS_TO_KEEP = [
    'README.md',
    'AGENTS.md',
    'PHASE1_SETUP.md',
    'PHASE3_PROGRESS.md',
    'implementation_plan.md',
    'walkthrough.md',
    'task.md',
]

def remove_file(filepath: str):
    """Remove a file if it exists."""
    path = Path(filepath)
    if path.exists():
        try:
            path.unlink()
            print(f"🗑️  Removed: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove {filepath}: {e}")
            return False
    return False

def remove_directory(dirpath: str):
    """Remove a directory if it exists."""
    path = Path(dirpath)
    if path.exists():
        try:
            shutil.rmtree(path)
            print(f"🗑️  Removed directory: {dirpath}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove directory {dirpath}: {e}")
            return False
    return False

def create_gitkeep(directory: str):
    """Create .gitkeep in empty directories."""
    path = Path(directory)
    if path.exists() and path.is_dir():
        gitkeep = path / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.touch()
            print(f"📝 Created .gitkeep in {directory}")

def main():
    """Main cleanup function."""
    print("="*70)
    print("🧹 Starting Project Cleanup...")
    print("="*70 + "\n")
    
    # Remove unnecessary files
    print("\n📄 Removing unnecessary files...")
    removed_files = 0
    for filepath in FILES_TO_REMOVE:
        if remove_file(filepath):
            removed_files += 1
    
    # Remove unnecessary directories
    print("\n📁 Removing unnecessary directories...")
    removed_dirs = 0
    for dirpath in DIRS_TO_REMOVE:
        if remove_directory(dirpath):
            removed_dirs += 1
    
    # Ensure proper directory structure
    print("\n📂 Ensuring proper directory structure...")
    required_dirs = [
        'backend/app/core',
        'backend/app/agents',
        'backend/app/schemas',
        'backend/tests/unit',
        'backend/tests/integration',
        'backend/uploads',
        'docs',
    ]
    
    for directory in required_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Ensured: {directory}")
    
    # Create .gitkeep in upload directories
    create_gitkeep('backend/uploads')
    
    print("\n" + "="*70)
    print(f"✅ Cleanup Complete!")
    print(f"   - Removed {removed_files} files")
    print(f"   - Removed {removed_dirs} directories")
    print("="*70 + "\n")
    
    print("📋 Next Steps:")
    print("   1. Run: restructure.bat")
    print("   2. Run: python backend/update_imports.py")
    print("   3. Run: npm install (clean install)")
    print("   4. Run: cd backend && pip install -r requirements.txt")
    print("   5. Run: docker-compose up -d")
    print("")

if __name__ == '__main__':
    main()
