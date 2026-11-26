# Rutina diaria de GTA 6 al Día (la sigue la tarea programada)

Repo: marcolopezmunoz2005-art/gta6aldia-media. Clave de ElevenLabs: en el repo PRIVADO marcolopezmunoz2005-art/gta6aldia-privado,
archivo elevenlabs_key.txt (no copiarla nunca a ningún otro sitio, ni al repo público, ni a mensajes, ni a logs).

## 0. Preparar
1. add_repo (owner marcolopezmunoz2005-art, repo gta6aldia-media, access push) y clonar en /home/claude/gta6aldia-media.
2. Leer state/playbook.md, state/learning.md, state/log.md, state/facts.md.
3. add_repo (gta6aldia-privado, access read) y clonar en /home/claude/gta6aldia-privado. La clave queda en /home/claude/gta6aldia-privado/elevenlabs_key.txt. Si no se puede leer: avisar a Marco y parar.

## 1. Medir (gratis primero)
- vidiq_social_post_list (últimos 7 días, completed) para tener las publicaciones.
- Instagram: vidiq_instagram_owner_insights (platformAccountId 29026053427037843, mode reels) → vistas, alcance, guardados, compartidos, % visto.
- YouTube: vidiq_channel_analytics (dimensions video) solo si vidiq_balance > 20; si no, omitir.
- TikTok: no hay lectura gratis; omitir salvo que haya créditos de sobra.
- Métricas que pasa Marco a mano (TikTok y YouTube): mirar la carpeta metricas/ del repo PRIVADO (/home/claude/gta6aldia-privado/metricas/).
  Acepta capturas (png/jpg: abrirlas con Read), CSV exportados de TikTok Studio / YouTube Studio o un metricas.md con números.
  Pasar los números a state/scoreboard.csv (nota "dato de Marco, captura del DD/MM HH:MM") y apuntar en state/learning.md qué archivos se han leído.
  No copiar las capturas al repo público. Si la carpeta no existe o está vacía, seguir sin esos datos.
- Apuntar métricas en state/scoreboard.csv (12 h, 24 h, 72 h). No inventar números: vacío si no hay dato.

## 2. Aprender
- Comparar por pilar, gancho, duración y hora. Reglas: una sola variable de prueba por día; no sacar conclusiones antes de 24 h.
- Escribir en state/learning.md: Ganan / Pierden / Reglas actuales + la prueba de hoy.

## 3. Investigar
- WebSearch de noticias de GTA 6 de las últimas 24–48 h (oficiales primero) y de trucos/secretos nuevos.
- Elegir **4 temas** que no estén en state/log.md, distintos entre sí (mezclar pilares), priorizando lo que learning.md dice que funciona.
  Datos con fuentes → state/facts.md.
- Clips de otros streamers: NO (decisión de Marco del 25/11). Solo material oficial de Rockstar y clips propios de Marco.

## 4. Guiones y montaje (4 candidatos)
- Para cada vídeo, un spec en specs/AAAA-MM-DD_x.json (x = a, b, c, d; formato en pipeline/render.py): 4–5 frases,
  **≤ 225 caracteres de voz por vídeo (≈ 900 al día)**; frase 1 = gancho; captions cortas; tags del catálogo (pipeline/catalog.json).
- Última frase = pregunta de ELEGIR ENTRE DOS ("¿Tú escondes el coche o huyes?"), no "¿cuál no sabías?" (0 comentarios en 15 posts).
- Clips propios de Marco: si hay vídeos en /home/claude/gta6aldia-privado/clips/, usarlos antes que el tráiler (ver playbook).
- Renderizar: python3 pipeline/render.py specs/X.json --key-file /home/claude/gta6aldia-privado/elevenlabs_key.txt --work /home/claude/work --usage state/usage.json --out videos/X.mp4
- Revisar cada vídeo: sacar 8 fotogramas con ffmpeg y mirarlos (textos completos, sin franjas, sin rótulos de Rockstar).
  Si algo falla, corregir y volver a renderizar (la voz queda en caché en --work: re-renderizar no gasta caracteres).
- Ordenar los 4 de mejor a peor según learning.md (1 = el que creo que funcionará mejor).
- Commit y push de videos/, specs/ y state/ (git -c push.negotiate=true push).

## Horarios (desde el 27/11)
- La rutina corre a las **23:12** y prepara los vídeos del **día siguiente**. Marco elige por la noche o por la mañana.
- Horas por defecto (decisión de Marco del 26/11: "lo de mediodía y tarde ha funcionado mejor"): **13:00 · 17:00 · 21:00**.
  La rotación de franjas A/B/C (26–27/11) queda parada mientras Marco no diga otra cosa.
- Excepción: si en el mensaje de disparo o en el chat se dan horas concretas, usar esas.
- Marco decide las horas al elegir: las de arriba son la propuesta para los borradores. Si en su respuesta da horas, mandan las suyas.
  En el mensaje, después de la pregunta, añadir: "Si quieres otras horas, dímelas con los números."
- YouTube: como las 3 horas son después de las 09:00, si Marco elige de noche se programan TikTok e IG en el momento y YouTube
  se publica a las 09:02 (send_later), cuando se reinicia el límite (ver sección 5).
- Apuntar la hora de cada post en scoreboard.csv (vistas a 24 h por franja y por plataforma).

## 5. Borradores y elección
- vidiq_video_upload con https://raw.githubusercontent.com/marcolopezmunoz2005-art/gta6aldia-media/main/videos/X.mp4 (gratis).
- vidiq_social_post_draft_create: un borrador por vídeo con TikTok + Instagram + YouTube (ajustes de playbook.md; poner publishAt
  también en el destino de YouTube). Candidatos 1–3 con las 3 franjas en orden; el candidato 4 sin hora (publishAt omitido).
- Enviar a Marco (SendUserMessage + notificación push): los 4 vídeos NUMERADOS en orden de preferencia (enlace raw de GitHub, texto,
  una línea de por qué), las 3 horas y una línea de qué se ha aprendido. Preguntar: "¿Cuáles publico? Responde con 3 números (p. ej. 1, 3, 4) o 'elige tú'."
- Sin respuesta de Marco no se publica nada. "elige tú" = publicar los candidatos 1, 2 y 3.
- Antes de publicar, repetirle los elegidos POR NOMBRE (no solo por número), con su hora (el 25/11 se publicó el de la serpiente y él dice que no lo quería).
- Cuando elija: con vidiq_social_post_draft_update poner a los 3 elegidos las 3 franjas en el orden en que los dijo (el que no tenga hora
  la recibe), comprobar que todas las horas siguen en el futuro (si una ya pasó, usar la siguiente franja libre y decírselo),
  y entonces vidiq_social_post_publish de cada uno. El no elegido se queda como borrador.
- Límite de YouTube (plan gratis de vidIQ): **3 subidas al día**, que se cuentan al publicar (YouTube se sube al momento con publishAt)
  y se reinician a medianoche de Los Ángeles (**09:00 en Madrid**). Si Marco elige antes de las 09:00 y ese día ya se gastaron las 3
  subidas (p. ej. el 25/11 se gastaron a las 17:11), publicar solo TikTok e IG (publicationIds) y avisarle de que YouTube
  tiene que publicarse después de las 09:00 (volver a llamar a vidiq_social_post_publish con la publicationId de YouTube).
- Apuntar en state/log.md (hora, postId y enlaces) y en scoreboard.csv. Commit y push.
