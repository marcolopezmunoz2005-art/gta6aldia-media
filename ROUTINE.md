# Rutina diaria de GTA 6 al Día (la sigue la tarea programada)

Repo: marcolopezmunoz2005-art/gta6aldia-media. Clave de ElevenLabs: en el ordenador de Marco,
C:\Users\marco\OneDrive\Documentos\gta6aldia\elevenlabs_key.txt (no copiarla nunca a ningún otro sitio, ni al repo, ni a mensajes).

## 0. Preparar
1. add_repo (owner marcolopezmunoz2005-art, repo gta6aldia-media, access push) y clonar en /home/claude/gta6aldia-media.
2. Leer state/playbook.md, state/learning.md, state/log.md, state/facts.md.
3. device_stage_files de la clave → /mnt/user-data/uploads/gta6aldia/elevenlabs_key.txt. Si el ordenador no responde: avisar a Marco (push) y parar.

## 1. Medir (gratis primero)
- vidiq_social_post_list (últimos 7 días, completed) para tener las publicaciones.
- Instagram: vidiq_instagram_owner_insights (platformAccountId 29026053427037843, mode reels) → vistas, alcance, guardados, compartidos, % visto.
- YouTube: vidiq_channel_analytics (dimensions video) solo si vidiq_balance > 20; si no, omitir.
- TikTok: no hay lectura gratis; omitir salvo que haya créditos de sobra.
- Apuntar métricas en state/scoreboard.csv (12 h, 24 h, 72 h). No inventar números: vacío si no hay dato.

## 2. Aprender
- Comparar por pilar, gancho, duración y hora. Reglas: una sola variable de prueba por día; no sacar conclusiones antes de 24 h.
- Escribir en state/learning.md: Ganan / Pierden / Reglas actuales + la prueba de hoy.

## 3. Investigar
- WebSearch de noticias de GTA 6 de las últimas 24–48 h (oficiales primero) y de trucos/secretos nuevos.
- Elegir 3 temas que no estén en state/log.md, priorizando lo que learning.md dice que funciona. Datos con fuentes → state/facts.md.

## 4. Guiones y montaje
- Para cada vídeo, un spec en specs/AAAA-MM-DD_x.json (formato en pipeline/render.py): 4–5 frases, ≤ 300 caracteres de voz en total,
  frase 1 = gancho; última frase = cierre o pregunta; captions cortas; tags del catálogo (pipeline/catalog.json).
- Renderizar: python3 pipeline/render.py specs/X.json --key-file /mnt/user-data/uploads/gta6aldia/elevenlabs_key.txt --work /home/claude/work --usage state/usage.json --out videos/X.mp4
- Revisar cada vídeo: sacar 8 fotogramas con ffmpeg y mirarlos (textos completos, sin franjas, sin rótulos de Rockstar).
  Si algo falla, corregir y volver a renderizar.
- Commit y push de videos/, specs/ y state/ (git -c push.negotiate=true push).

## 5. Borradores y aprobación
- vidiq_video_upload con https://raw.githubusercontent.com/marcolopezmunoz2005-art/gta6aldia-media/main/videos/X.mp4
- vidiq_social_post_draft_create: un borrador por vídeo con TikTok + Instagram + YouTube (ajustes de playbook.md) y horas 19:30 / 21:00 / 22:30 de hoy.
- Enviar a Marco (SendUserMessage + notificación push): los 3 vídeos (enlaces raw de GitHub), textos, horas y una línea de qué se ha aprendido.
  Pedir "sí" para publicar. Sin su "sí" no se publica nada.
- Cuando diga "sí": vidiq_social_post_publish de cada borrador y apuntar en state/log.md (con postId y enlaces). Commit y push.
