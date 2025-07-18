==============================
Formatos de Datos Soportados
==============================

El sistema soporta múltiples formatos y variantes de exportación de Instagram, tanto antiguos como recientes. A continuación se describen los principales:

Export JSON de Instagram
------------------------
- posts.json: Publicaciones del usuario (fotos, videos, captions, likes, comentarios)
- stories.json: Historias publicadas (con media, timestamps, viewers)
- reels.json: Reels publicados (video, métricas, comentarios)
- archived_posts.json: Publicaciones archivadas
- recently_deleted_content.json: Contenido eliminado recientemente
- story_interactions/: Carpeta con archivos de interacciones en historias
- liked_posts.json: Posts que el usuario ha dado like
- post_comments.json: Comentarios realizados en posts
- reel_comments.json: Comentarios en reels
- profile.json: Información del perfil (username, bio, followers, etc)
- followers.json / following.json: Seguidores y seguidos
- messages/: Carpeta con conversaciones (mensajes directos)

Estructura de Carpetas
----------------------
- /media/: Archivos multimedia (fotos, videos, thumbnails)
- /messages/: Conversaciones en formato JSON
- /story_interactions/: Interacciones de historias (vistas, respuestas, reacciones)

Campos y Tipos de Datos
-----------------------
- Timestamps: ISO 8601, epoch, o string (auto-detectados)
- Media: URLs relativas o absolutas, archivos locales
- Comentarios: Listas de objetos con autor, texto, timestamp
- Engagement: Likes, shares, impresiones, reach
- Perfil: username, nombre, bio, foto, seguidores, seguidos

Compatibilidad y Validación
---------------------------
- El sistema detecta automáticamente variantes de export (legacy, nuevo formato, multi-cuenta)
- Validación estricta de estructura y tipos usando Pydantic
- Soporte para campos opcionales y backward compatibility

Ejemplo de estructura mínima válida:

.. code-block:: json

    {
      "posts": [
        {
          "id": "123",
          "caption": "Mi post",
          "media": ["media/photo1.jpg"],
          "timestamp": "2025-07-18T12:00:00Z",
          "likes": 42,
          "comments": [
            {"user": "amigo1", "text": "Genial!", "timestamp": "2025-07-18T12:01:00Z"}
          ]
        }
      ],
      "profile": {
        "username": "usuario",
        "full_name": "Nombre Apellido"
      }
    }

Para más detalles, consulta la documentación de cada parser y modelo en la referencia API.
