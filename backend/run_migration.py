#!/usr/bin/env python3
"""Script pour exécuter les migrations SQL manuellement"""
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import engine
from sqlalchemy import text

def run_migration(sql_file: str):
    """Exécute un fichier SQL de migration"""
    sql_path = Path(__file__).parent / "alembic" / "versions" / sql_file

    if not sql_path.exists():
        print(f"❌ Fichier de migration non trouvé: {sql_path}")
        return False

    print(f"📄 Lecture du fichier de migration: {sql_file}")
    sql_content = sql_path.read_text()

    # Remove comments and clean up SQL
    lines = []
    for line in sql_content.split('\n'):
        # Skip comment lines
        stripped = line.strip()
        if stripped.startswith('--'):
            continue
        # Remove inline comments
        if '--' in line:
            line = line.split('--')[0]
        lines.append(line)

    cleaned_sql = '\n'.join(lines)

    # Split by statements
    statements = []
    for s in cleaned_sql.split(';'):
        s = s.strip()
        if s:  # Only add non-empty statements
            statements.append(s)

    print(f"🔄 Exécution de {len(statements)} statements SQL...")

    with engine.begin() as conn:
        for i, statement in enumerate(statements, 1):
            try:
                print(f"   [{i}/{len(statements)}] Exécution...")
                conn.execute(text(statement))
                print(f"   ✅ Statement {i} exécuté avec succès")
            except Exception as e:
                print(f"   ❌ Erreur lors de l'exécution du statement {i}")
                print(f"   Error: {e}")
                print(f"   Statement: {statement[:100]}...")
                raise

    print(f"✅ Migration {sql_file} terminée avec succès!")
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Exécution des migrations de base de données")
    print("=" * 70)

    try:
        # Run the migration
        run_migration("001_add_series_cast_crew_videos.sql")
        print("\n✅ Toutes les migrations ont été appliquées avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        sys.exit(1)
