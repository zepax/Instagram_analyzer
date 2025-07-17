#!/usr/bin/env python3
"""
Script para generar análisis HTML completo con imágenes embebidas.
Ignora análisis gramatical - solo se enfoca en exportar HTML.
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, 'src')

from instagram_analyzer.parsers.data_detector import DataDetector
from instagram_analyzer.parsers.json_parser import JSONParser
from instagram_analyzer.exporters.html_exporter import HTMLExporter
from instagram_analyzer.analyzers.basic_stats import BasicStatsAnalyzer

def main():
    # Configuración
    data_path = Path('data/sample_exports/instagram-pcFuHXmB')
    output_path = Path('final_analysis')
    
    print("🔍 Iniciando análisis HTML completo...")
    print(f"📁 Directorio de datos: {data_path}")
    print(f"📂 Directorio de salida: {output_path}")
    
    # 1. Detectar estructura de datos
    print("\n1️⃣ Detectando estructura de datos...")
    detector = DataDetector()
    structure = detector.detect_structure(data_path)
    
    print(f"✅ Estructura detectada: {structure['export_type']}")
    print(f"📊 Archivos encontrados:")
    print(f"   - Posts: {len(structure['post_files'])}")
    print(f"   - Stories: {len(structure['story_files'])}")
    print(f"   - Reels: {len(structure['reel_files'])}")
    print(f"   - Archived: {len(structure['archived_post_files'])}")
    print(f"   - Recently Deleted: {len(structure['recently_deleted_files'])}")
    
    # 2. Parsear contenido
    print("\n2️⃣ Parseando contenido...")
    parser = JSONParser()
    
    # Parsear posts
    posts = []
    for post_file in structure['post_files']:
        try:
            file_posts = parser.parse_posts_from_file(post_file)
            posts.extend(file_posts)
            print(f"   📄 Posts de {post_file.name}: {len(file_posts)}")
        except Exception as e:
            print(f"   ❌ Error parseando {post_file.name}: {e}")
    
    # Parsear stories
    stories = []
    for story_file in structure['story_files']:
        try:
            file_stories = parser.parse_stories_from_file(story_file)
            stories.extend(file_stories)
            print(f"   📄 Stories de {story_file.name}: {len(file_stories)}")
        except Exception as e:
            print(f"   ❌ Error parseando {story_file.name}: {e}")
    
    # Parsear reels
    reels = []
    for reel_file in structure['reel_files']:
        try:
            file_reels = parser.parse_reels_from_file(reel_file)
            reels.extend(file_reels)
            print(f"   📄 Reels de {reel_file.name}: {len(file_reels)}")
        except Exception as e:
            print(f"   ❌ Error parseando {reel_file.name}: {e}")
    
    # Parsear archived posts
    archived_posts = []
    for archived_file in structure['archived_post_files']:
        try:
            file_archived = parser.parse_archived_posts_from_file(archived_file)
            archived_posts.extend(file_archived)
            print(f"   📄 Archived de {archived_file.name}: {len(file_archived)}")
        except Exception as e:
            print(f"   ❌ Error parseando {archived_file.name}: {e}")
    
    # Parsear recently deleted
    recently_deleted = []
    for deleted_file in structure['recently_deleted_files']:
        try:
            file_deleted = parser.parse_recently_deleted_from_file(deleted_file)
            recently_deleted.extend(file_deleted)
            print(f"   📄 Recently Deleted de {deleted_file.name}: {len(file_deleted)}")
        except Exception as e:
            print(f"   ❌ Error parseando {deleted_file.name}: {e}")
    
    # 3. Crear analyzer mock con los datos
    print("\n3️⃣ Creando analyzer con datos...")
    
    # Crear clase simple para contener los datos
    class SimpleAnalyzer:
        def __init__(self, posts, stories, reels, archived_posts, recently_deleted, data_path):
            self.posts = posts
            self.stories = stories
            self.reels = reels
            self.archived_posts = archived_posts
            self.recently_deleted = recently_deleted
            self.profile = None
            self.conversations = []
            self.story_interactions = []
            self.data_path = data_path  # Necesario para el exporter
    
    analyzer = SimpleAnalyzer(posts, stories, reels, archived_posts, recently_deleted, data_path)
    
    # Generar estadísticas básicas
    stats_analyzer = BasicStatsAnalyzer()
    basic_stats = stats_analyzer.analyze(
        posts=posts,
        stories=stories,
        reels=reels,
        archived_posts=archived_posts,
        recently_deleted=recently_deleted,
        story_interactions=[]
    )
    
    print("📊 Estadísticas generadas:")
    print(f"   - Total posts: {basic_stats.get('total_posts', 0)}")
    print(f"   - Total stories: {basic_stats.get('total_stories', 0)}")
    print(f"   - Total reels: {basic_stats.get('total_reels', 0)}")
    print(f"   - Total archived: {len(archived_posts)}")
    print(f"   - Total recently deleted: {len(recently_deleted)}")
    
    # 4. Generar HTML con imágenes embebidas
    print("\n4️⃣ Generando HTML con imágenes embebidas...")
    output_path.mkdir(exist_ok=True)
    
    exporter = HTMLExporter()
    
    # Configurar para embeber imágenes
    html_file = output_path / "instagram_analysis_complete.html"
    
    try:
        html_file = exporter.export(
            analyzer=analyzer,
            output_path=output_path,
            embed_images=True,  # ¡Clave para imágenes embebidas!
            anonymize=False
        )
        
        print(f"✅ HTML generado exitosamente: {html_file}")
        print(f"📁 Tamaño del archivo: {html_file.stat().st_size / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"❌ Error generando HTML: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Mostrar resumen final
    print("\n🎉 ¡ANÁLISIS COMPLETO TERMINADO!")
    print("📊 Resumen del contenido procesado:")
    print(f"   - Posts: {len(posts)}")
    print(f"   - Stories: {len(stories)}")
    print(f"   - Reels: {len(reels)}")
    print(f"   - Archived Posts: {len(archived_posts)}")
    print(f"   - Recently Deleted: {len(recently_deleted)}")
    print(f"📄 Archivo HTML: {html_file}")
    print(f"🌐 Para ver el reporte, abre: {html_file.absolute()}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
