# DIRECTRICES FARO
## Vigilante personal de metaeficiencia LLM (Strange Loop Factory)

### 0. Decision estrategica (NO reabrir sin datos nuevos)

**Lo que FARO NO es:**
- NO es otro leaderboard/comparador de modelos. Artificial Analysis, LMArena y pricepertoken.com ya existen, son gratis y muy buenos. Competir ahi de frente = morir.
- NO es otra herramienta de observability B2B para desarrolladores. Ese espacio esta saturado: Bifrost, LiteLLM, Langfuse, Datadog, Braintrust, Opik, Helicone, OpenObserve...

**El hueco real (validado julio 2026):**
La capa PERSONAL para prosumidores y pymes: "que significa este mercado para MI factura y MI forma de trabajar". Evidencia: el usuario avanzado medio paga 60-110 USD/mes en suscripciones sin auditarlas y hace hojas de calculo a mano; los proveedores migran a limites por computo y pricing por uso (opacidad creciente); hay presion documentada de subidas por rentabilidad pre-IPO. Nadie ocupa el rol "Fintonic del gasto en IA". En espanol: nada.

**Posicionamiento en una frase:**
"FARO no compara modelos. Vigila el oceano LLM por ti y te dice que significa cada ola para tu bolsillo y tu forma de trabajar."

**El activo defendible es el HISTORIAL.** Cada dia de cron acumula datos que nadie puede reconstruir retroactivamente. Por eso el YA importa: no por hype, por acumulacion. El repo publico de historial es ademas SEO + credibilidad (patron pro-bono ARGOS).

### 1. Arquitectura por capas

**Capa 1 - Observatorio (el mundo). HECHA EN v0.1:**
- Fuente primaria: OpenRouter `/api/v1/models` (publica, gratuita, 400+ modelos, USD/token, contexto, fechas). Cubre TODO el mercado API con una sola llamada diaria.
- Motor: `faro_watch.py` (stdlib pura) + GitHub Actions cron. Git = base de datos historica. Coste de infraestructura: 0 EUR.
- Eventos: PRICE_UP, PRICE_DOWN, NEW_MODEL, REMOVED, CONTEXT_CHANGE.

**Capa 2 - Traductor personal (que significa para ti). PARCIAL EN v0.1:**
- perfil.json con consumo mensual -> delta EUR/mes por cada cambio. HECHO.
- Fase 1: anadir fuente de SUSCRIPCIONES de consumidor (ChatGPT Plus/Pro, Claude Pro/Max, Gemini AI Pro/Ultra, Perplexity, Mistral, Copilot). No hay API: tabla curada `data/subs.json` + script de verificacion semanal contra las paginas de pricing oficiales que marque discrepancias para revision humana. Aqui SI puede entrar un LLM barato (haiku) para extraer precios del HTML: coste ~centimos/semana.
- Calculadora estrella para la landing: "Pagas X en suscripciones. Segun tu uso real, via API pagarias Y. Ahorro/sobrecoste: Z EUR/anno."

**Capa 3 - Coach de metaeficiencia (como usas la IA). FASE 2:**
- Import del export oficial de conversaciones (ChatGPT y Claude permiten exportar JSON). Procesado 100% LOCAL en el navegador (privacy-first, argumento de venta central: tus conversaciones nunca salen de tu maquina).
- Metricas: longitud media de mensajes, chats zombi que arrastran contexto gigante (coste y degradacion), ratio pregunta/respuesta, cuando deberia haber abierto chat nuevo, que porcentaje de tareas eran de modelo barato.
- Salida: Informe de Metaeficiencia mensual con 3-5 habitos concretos a cambiar. La narrativa la genera haiku sobre las metricas ya calculadas (nunca sobre el texto crudo de las conversaciones).
- Recomendador tarea -> modelo usando el propio catalogo + indice de inteligencia que OpenRouter ya expone (sort=intelligence-high-to-low, datos de Artificial Analysis).

**Capa 4 - Medidor activo (FASE 3, conecta con ARCA):**
- ARCA como proxy local opcional para usuarios API: medicion real por peticion, presupuestos, failover. FARO es la cara; ARCA es el musculo. No duplicar codigo: ARCA ya tiene circuit breaker y cache.

### 2. Monetizacion

- **Free:** web con observatorio, ALERTAS publicas, calculadora suscripcion-vs-API, newsletter/Telegram global.
- **Pro (4-5 EUR/mes):** perfil personal, alertas que solo disparan cuando TE afectan, informe mensual de metaeficiencia, recomendador.
- **B2B (mas adelante):** feed de eventos de pricing por API + informe de gasto IA para equipos (el dolor "AI bill shock" es real y documentado en CIOs).

### 3. Distribucion (el producto es copiable; la distribucion no)

- Cada cambio de tarifa de un grande = pico de busquedas y cabreo. FARO debe ser el PRIMERO en contarlo: bot que publica automaticamente el evento (X/Twitter + Telegram + RSS del repo) en cuanto el cron lo detecta. Ese es el canal de adquisicion, gratis y recurrente.
- Hueco idiomatico: todo el ecosistema de comparadores es ingles. FARO nace bilingue ES/EN con ventaja hispana.

### 4. Roadmap 90 dias

- **Semana 0 (hoy):** repo publico + cron activo. El contador de historial empieza a correr.
- **Semanas 1-2:** subs.json curado + landing (Next.js 14, mismo stack SLF, dominio o subdominio faro.strangeloopfactory.com) con calculadora + captura de email. Bot de publicacion automatica de eventos.
- **Semanas 3-6:** import de exports + informe de metaeficiencia local (Capa 3 MVP). Beta con 10-20 usuarios.
- **Semanas 7-12:** Pro con Stripe (reutilizar integracion de INDOMITUS), perfil persistente en Supabase, recomendador v1.

### 5. Reglas SLF (obligatorias)

- Sin em-dashes en ningun texto publico. Sin nombres de instituciones externas en archivos publicos.
- Coste API bajo control: el core (Capa 1) es 100% determinista, CERO llamadas a LLM. Los LLM solo entran en extraccion de subs (haiku, semanal) y narrativa de informes (haiku, mensual, sobre metricas agregadas). Alertar coste estimado antes de cada nueva integracion.
- Claude Code solo en local, nunca en VPS.
- PowerShell: sin `&&`, rutas entre comillas, UTF-8 sin BOM.
- Ruta local del proyecto: `D:\DEV\faro`.

### 6. Estado v0.1 (entregado)

- `faro_watch.py`: motor completo, testado con fixtures (subida, bajada, lanzamiento, retirada, cambio de contexto, impacto en perfil). Stdlib pura.
- `.github/workflows/faro.yml`: cron diario 06:00 UTC + commit automatico + Telegram opcional via secrets.
- `perfil.ejemplo.json`, `README.md` publico.
- Pendiente inmediato: crear repo, primer push, activar Actions, ejecutar workflow_dispatch manual para el snapshot base.
