# Especificaciones de Diseño: Sistema de Gestión Clínica Dental

**Versión:** 1.0  
**Última actualización:** Noviembre 2025  
**Plataforma objetivo:** v0.dev  
**Framework:** React 18 + TypeScript + Tailwind CSS

---

## 1. Principios de Diseño

El sistema debe cumplir con estándares de diseño médico-tecnológico, balanceando profesionalismo clínico con usabilidad moderna.

**Objetivos principales:**
- Reducir fricción en tareas administrativas
- Presentar información médica compleja de forma clara
- Mantener consistencia visual en toda la plataforma
- Optimizar para diferentes niveles de alfabetización digital

---

## 2. Especificación: Dashboard Principal

### 2.1 Alcance Funcional

Interface central del paciente. Consolida información de citas, tratamientos activos, estado financiero y actividad reciente.

### 2.2 Prompt de Implementación

```
Implementar dashboard para portal de pacientes de clínica dental.

ESPECIFICACIONES TÉCNICAS:

Sistema de Color (Tailwind CSS):
- Primary: sky-500 (#0EA5E9)
- Secondary: violet-500 (#8B5CF6)  
- Success: emerald-500 (#10B981)
- Warning: amber-500 (#F59E0B)
- Error: rose-500 (#EF4444)
- Neutral: slate-500 (#64748B)

Gradientes:
- Principal: linear-gradient(135deg, #0EA5E9, #8B5CF6)
- Hover states: Variantes con alpha 0.05-0.1

Tipografía:
- UI: Inter (400, 500, 600)
- Display: Poppins (600, 700)
- Data: JetBrains Mono (500, 600)

Icons:
- Biblioteca: Lucide React
- Tamaño base: 20px (icons), 24px (features)

ESTRUCTURA DE LAYOUT:

Header (sticky top):
- Logo (izquierda)
- Breadcrumb navigation (centro)
- Notifications badge + Avatar dropdown (derecha)
- Background: backdrop-blur-xl bg-white/80
- Height: 64px
- Border: border-b border-gray-200/50

Sidebar (desktop, fixed left, 240px):
- Navigation items:
  * Inicio (Home icon)
  * Citas (Calendar icon)
  * Odontograma (Activity icon)
  * Historial (FileText icon)
  * Facturación (DollarSign icon)
  * Configuración (Settings icon)
- CTA Button: "Agendar Cita" (gradient background)
- Support link (bottom)
- Background: backdrop-blur-lg bg-white/60

Main Content Area:

1. Hero Section:
   - Greeting: "Hola, [Nombre]" (h1, font-semibold)
   - Subtitle contextual basado en próxima cita
   - Background: gradient sky-500 to violet-500
   - Padding: p-8
   - Border radius: rounded-2xl

2. Stats Grid (4 columnas, responsive a 2x2 en tablet, stack en mobile):
   - Card structure:
     * Icon (top-left, 48px)
     * Value (center, text-3xl font-bold)
     * Label (bottom, text-sm text-gray-600)
     * Progress indicator (bottom-right, circular SVG)
   - Hover: translateY(-4px), shadow-lg
   - Background: bg-white/50 backdrop-blur-md
   - Border: border-gray-200/50

3. Alert Banner (conditional):
   - Show si: solicitudes pendientes > 0
   - Layout: flex items-center justify-between
   - Icon + Message + Actions
   - Background: bg-amber-50 border-l-4 border-amber-500
   - Animation: slide-down on mount

4. Analytics Chart:
   - Library: Recharts
   - Type: BarChart con gradiente
   - Data: Últimos 6 meses de actividad
   - Height: 320px
   - Background: bg-white rounded-xl shadow-sm
   - Tooltip: Custom con data detallada

5. Próximas Citas:
   - Layout: Vertical stack de cards
   - Card structure:
     * Date badge (left)
     * Doctor info + specialty
     * Appointment reason
     * Status badge (color-coded)
     * Action buttons (right)
   - Max visible: 3, link "Ver todas"
   - Swipe horizontal en mobile

6. Activity Timeline:
   - Vertical line con dots
   - Items alternando left/right (desktop)
   - Stack en mobile
   - Icon types: Payment, Appointment, Approval
   - Relative dates: "Hace X días"

INTERACCIONES:

Stats Cards:
- Hover: transform: translateY(-4px), transition 200ms
- Count-up animation en mount (1.5s duration)
- Click: Navigate to detail view

Appointment Cards:
- Hover: Show hidden action buttons
- Status badge: Pulse animation si "PENDING"

Timeline:
- Click item: Expand panel (spring animation)
- Scroll trigger: Fade-in stagger

Sidebar:
- Active item: Blue underline (slide effect)
- Hover: Background opacity shift

ANIMATIONS:

Entry sequence (staggered):
1. Hero: opacity 0→1, translateY(-20px→0), 300ms
2. Stats: delay 100ms each, same fade-up
3. Chart: draw bars (800ms duration)
4. Cards: stagger 60ms, fade + scale

Loading:
- Skeleton: Shimmer gradient animation
- Spinner: Rotate 360deg, 1s linear infinite

Transitions:
- Page change: crossfade 200ms
- Modal: scale + backdrop blur

RESPONSIVE:

Desktop (≥1280px):
- Sidebar: Fixed 240px
- Stats: 4 columns
- Chart: Full width

Tablet (768-1279px):
- Sidebar: Collapsible
- Stats: 2×2 grid
- Chart: Maintain aspect ratio

Mobile (<768px):
- Bottom navigation (5 items)
- Stats: 2×2 compact
- Chart: Horizontal scroll
- Swipe gestures enabled

ACCESSIBILITY:

- Color contrast: Minimum 4.5:1 (text), 3:1 (UI)
- Focus indicators: ring-2 ring-sky-500 ring-offset-2
- ARIA labels en todos los interactive elements
- Keyboard navigation: Tab order lógico
- Screen reader: Descriptive labels, live regions para updates
- Reduced motion: Respeta prefers-reduced-motion

TECH STACK:

Required:
- React 18.3+
- TypeScript 5+
- Tailwind CSS 3.4+
- Framer Motion 11+ (animations)
- Recharts 2.10+ (charting)
- Radix UI (accessible primitives)
- Lucide React (icons)

Optional:
- Zustand (state management)
- React Hook Form + Zod (forms)
- date-fns (date manipulation)

CODE REQUIREMENTS:
- TypeScript strict mode
- ESLint + Prettier config
- Component composition pattern
- Custom hooks para lógica reutilizable
- Error boundaries
- Lazy loading para código no crítico
- Memoization donde corresponda
```

---

---

## 3. Especificación: Odontograma Interactivo

### 3.1 Alcance Funcional

Visualización interactiva del estado dental del paciente basada en sistema FDI. Permite consulta de historial por pieza dental específica.

### 3.2 Prompt de Implementación

```
Implementar odontograma dental interactivo según sistema FDI.

SISTEMA DE NUMERACIÓN FDI:

ARQUITECTURA ANATÓMICA:
┌─────────────────────────────────────┐
│    ARCADA SUPERIOR (Maxilar)        │
│  18 17 16 15 14 13 12 11 │ 21 22 23 24 25 26 27 28
│  └─ Cuadrante 1 ─┘        └─ Cuadrante 2 ─┘
│                                     │
│         [LÍNEA MEDIA]               │
│                                     │
│  48 47 46 45 44 43 42 41 │ 31 32 33 34 35 36 37 38
│  └─ Cuadrante 4 ─┘        └─ Cuadrante 3 ─┘
│    ARCADA INFERIOR (Mandíbula)      │
└─────────────────────────────────────┘

NOMENCLATURA:
- 1X: Superior Derecho (11-18)
- 2X: Superior Izquierdo (21-28)  
- 3X: Inferior Izquierdo (31-38)
- 4X: Inferior Derecho (41-48)

Dígitos finales:
1-2: Incisivos (frontales)
3: Caninos (colmillos)
4-5: Premolares
6-7-8: Molares (8 = muelas del juicio)

=== DISEÑO VISUAL REVOLUCIONARIO ===

HERO SECTION - Score de Salud:
┌───────────────────────────────────────────────────┐
│         🦷 MI ODONTOGRAMA INTERACTIVO             │
│    "Explora tu sonrisa diente por diente"        │
│                                                   │
│    ┌─────────────┐      ┌──────────────────┐    │
│    │     97%     │      │ 📊 ESTADÍSTICAS  │    │
│    │   ━━━━━○    │      │ ✅ 31 Sanos      │    │
│    │ Salud Dental│      │ 🔧 1 Tratado     │    │
│    │  EXCELENTE  │      │ ⚪ 0 Ausentes    │    │
│    └─────────────┘      │ ⚠️  0 Observación│    │
│  SVG animado circular   └──────────────────┘    │
│  + Partículas verdes                            │
│  + Glow pulsante                                │
└───────────────────────────────────────────────────┘

CONTROLES VISTA (Tab Pills):
[🔍 Vista Completa] [⬆️ Superior] [⬇️ Inferior] [➡️ Derecha] [⬅️ Izquierda]
+ Animación slide underline
+ Contador visible: "32 dientes" / "16 superiores" etc.

RENDERIZADO 3D DE DIENTES:
Cada diente es un componente visual avanzado:

┌──────────┐
│   [16]   │ ← Badge número (glassmorphism)
│  ┌────┐  │
│  │ ✅ │  │ ← Icono estado 3xl animado
│  └────┘  │
│  ●●●●○   │ ← Dots indicador tratamientos (max 5)
└──────────┘
   ▼
┌──────────────────────────────────────┐ ← Tooltip Rich
│ 🦷 Primer Molar Superior Derecho     │
│ Estado: SANO ✅                      │
│ Tratamientos: 2                      │
│ • Limpieza (2023)                   │
│ • Obturación (2024)                 │
│ [Ver historia completa →]            │
└──────────────────────────────────────┘

ANATOMÍA DEL DIENTE (CSS 3D):
- Perspectiva CSS: perspective(1000px)
- Forma realista: clip-path para simular corona
- Gradiente depth: linear-gradient(145deg, light, dark)
- Sombras múltiples:
  * Shadow 1: 0 4px 6px rgba(0,0,0,0.1) (base)
  * Shadow 2: 0 10px 15px rgba(0,0,0,0.1) (hover)
  * Shadow 3: inset 0 2px 4px rgba(255,255,255,0.2) (brillo)
- Border: 3px con gradiente según estado
- Transform hover: scale(1.15) rotateY(5deg) translateY(-8px)

SISTEMA DE COLORES MÉDICO AVANZADO:

SANO (Healthy Green):
- Background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)
- Border: #10B981 con glow verde
- Icon: ✅ con animación heartbeat sutil

TRATADO (Medical Blue):
- Background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)
- Border: #3B82F6 con glow azul
- Icon: 🔧 con rotación suave

CARIES (Alert Red):
- Background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)  
- Border: #EF4444 con pulse animation
- Icon: ⚠️ con shake micro-animation

AUSENTE (Neutral Gray):
- Background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%)
- Border: #9CA3AF dashe (discontinuo)
- Icon: ⚪ con opacity 50%

OBSERVACIÓN (Warning Amber):
- Background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)
- Border: #F59E0B con glow amarillo
- Icon: 👁️ con blink animation

IMPLANTE (Tech Purple):
- Background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%)
- Border: #8B5CF6 con glow púrpura
- Icon: 🔩 con shine animation

LAYOUT DENTAL INTERACTIVO:

┌─────────────────────────────────────────────────────┐
│           ARCADA SUPERIOR                           │
│   ┌─────────────┐       ┌─────────────┐           │
│   │ Cuadrante 1 │       │ Cuadrante 2 │           │
│   │  Superior   │       │  Superior   │           │
│   │   Derecho   │       │  Izquierdo  │           │
│   │             │       │             │           │
│   │ 18 17 16 15 │       │ 25 26 27 28 │           │
│   │ 14 13 12 11 │       │ 21 22 23 24 │           │
│   └─────────────┘       └─────────────┘           │
│                                                     │
│   ═══════════ LÍNEA MEDIA ═══════════             │
│              (Separador visual)                    │
│                                                     │
│   ┌─────────────┐       ┌─────────────┐           │
│   │ 48 47 46 45 │       │ 35 36 37 38 │           │
│   │ 44 43 42 41 │       │ 31 32 33 34 │           │
│   │             │       │             │           │
│   │ Cuadrante 4 │       │ Cuadrante 3 │           │
│   │  Inferior   │       │  Inferior   │           │
│   │   Derecho   │       │  Izquierdo  │           │
│   └─────────────┘       └─────────────┘           │
│          ARCADA INFERIOR                            │
└─────────────────────────────────────────────────────┘

MODAL DETALLE DIENTE (Premium):
════════════════════════════════════════
║  ⚡ DETALLE: Primer Molar Superior   ║
║     [Gradiente azul-púrpura]         ║
════════════════════════════════════════
    
    🦷 DIENTE #16
    [Badge: TRATADO 🔧]
    
┌──────────────────────────────────────┐
│ 📋 INFORMACIÓN GENERAL               │
├──────────────────────────────────────┤
│ Tipo: Molar                          │
│ Posición: Superior Derecho           │
│ Cuadrante: 1                         │
│ Estado Actual: TRATADO               │
│ Última revisión: 15 Nov 2025         │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 📜 HISTORIAL DE TRATAMIENTOS         │
├──────────────────────────────────────┤
│  ●═══════════════════════            │ ← Timeline
│  ║                                   │
│  ╠══● 15 Nov 2025                    │
│  ║   🔧 Obturación                   │
│  ║   Dr. Juan Pérez                  │
│  ║   [Ver episodio completo →]       │
│  ║                                   │
│  ╠══● 10 Mar 2023                    │
│  ║   🧹 Limpieza Profunda            │
│  ║   Dr. María López                 │
│  ║   [Ver episodio completo →]       │
│  ●                                    │
└──────────────────────────────────────┘

[Cerrar] [📅 Agendar Consulta →]

INTERACTIVIDAD GAMIFICADA:

HOVER STATES:
- Diente Idle: Leve breathing animation (scale 1.0 → 1.02)
- Diente Hover: 
  * Scale 1.15
  * RotateY 5deg (efecto 3D)
  * TranslateY -8px (levitación)
  * Shadow expansion (6px → 20px blur)
  * Glow color según estado
  * Tooltip aparece con slide-up + fade
  * Dientes adyacentes: subtle scale 1.05 (efecto domino)

CLICK INTERACTIONS:
- Click: Ripple effect desde punto de click
- Modal open: Backdrop blur-xl + scale-in
- Timeline items: Expand con spring physics

ANIMACIONES ENTRADA:
1. Hero score: Count-up desde 0% a 97% (1.5s)
2. Circular progress: Draw stroke con ease-out
3. Dientes: Stagger grid animation (50ms delay cada uno)
   * Fade in desde opacity 0
   * Scale desde 0.8
   * RotateY desde 90deg
4. Tooltips: Slide-up desde translateY(10px)

MICROINTERACCIONES:
- Badge número: Pulse suave cada 3s
- Dots tratamientos: Fill secuencial al cargar
- Estado icons: Loop animation (ej: heartbeat para sano)
- Cuadrantes: Hover group highlight
- Vista tabs: Slide underline seguimiento cursor

RESPONSIVE ADAPTATIVO:

Desktop (>1024px):
- Grid 2x2 cuadrantes
- Tooltips laterales
- Hover effects completos

Tablet (768-1023px):  
- Stack 2x1 (superior / inferior)
- Dientes 48px
- Tooltips posición auto

Mobile (<767px):
- Stack vertical
- Dientes 40px
- Tap para tooltip
- Swipe para navegar vistas
- Bottom sheet para modal

TECNOLOGÍA & PERFORMANCE:

Stack Core:
- React 18 (Concurrent features)
- TypeScript 5 (Strict mode)
- Tailwind CSS 3.4 (JIT)
- Framer Motion 11 (Layout animations)

Optimizaciones:
- Virtual scrolling (si >32 dientes)
- Lazy load modal components
- Memoization de renders pesados
- CSS containment para dientes
- Will-change en hover states
- Transform en GPU (translate3d)

SVG Optimization:
- SVGO para comprimir iconos
- Inline critical SVGs
- Lazy load decorative SVGs

Accesibilidad:
- ARIA labels descriptivos por diente
- Keyboard navigation (Tab + Arrow keys)
- Focus trap en modal
- Screen reader: "Diente 16, molar superior derecho, estado sano, 2 tratamientos"
- Reduced motion media query (deshabilita animaciones)

Testing:
- Unit tests (Jest + RTL)
- Visual regression (Chromatic)
- E2E (Playwright)
- Performance budget: <2s FCP, <3.5s LCP

Genera código production-grade con arquitectura escalable y documentación inline.
```

---

---

## 📅 PROMPT 3: Wizard de Agendamiento Cinematográfico

### **Contexto de Uso:**
Experiencia de booking fluida que convierte una tarea administrativa en un journey delightful. Inspirado en Calendly, Cal.com y los mejores sistemas de reservas modernos.

### **Prompt Cinematográfico para v0.dev:**

```
Diseña un wizard de agendamiento de citas premium con experiencia fluida tipo Calendly + magia de microinteracciones.

=== ARQUITECTURA DEL JOURNEY ===

FLUJO PSICOLÓGICO (4 Actos):
Acto I: Conexión Humana (Elegir Doctor)
Acto II: Compromiso Temporal (Elegir Fecha)
Acto III: Precisión (Elegir Hora)
Acto IV: Confirmación Motivadora

Progress Indicator (Always Visible):
┌─────────────────────────────────────────┐
│  ●━━━━━ ○━━━━━ ○━━━━━ ○               │
│  Doctor  Fecha   Hora  Confirmar        │
│  [1/4]                                  │
└─────────────────────────────────────────┘

=== PASO 1: SELECCIÓN DE DOCTOR (Human Connection) ===

DISEÑO:
- Cada card:
  * Foto circular grande
  * Nombre completo
  * Especialidad (badge azul)
  * Rating (estrellas)
  * Años experiencia
  * Botón "Seleccionar"
- Hover: Elevación y brillo
- Seleccionado: Borde azul grueso + check

PASO 2 - SELECCIONAR FECHA:
- Título: "📅 Selecciona la Fecha"
- Calendario mensual grande
- Días:
  * Pasados: Deshabilitados (gris claro)
  * Sin disponibilidad: Tachados (rojo)
  * Con disponibilidad: Verde claro
  * Seleccionado: Azul sólido + check
- Leyenda de colores abajo
- Navegación mes anterior/siguiente
- Vista de 7 columnas (L-D)

PASO 3 - SELECCIONAR HORA:
- Título: "⏰ Selecciona la Hora"
- Mostrar fecha seleccionada arriba
- Grid de slots (3-4 columnas):
  * Formato: "8:00 AM", "8:30 AM", etc.
  * Ocupados: Gris con icono candado
  * Disponibles: Blanco con borde
  * Hover disponibles: Azul claro
  * Seleccionado: Azul sólido + check
- Horario: 8:00 AM - 6:00 PM (slots 30 min)

PASO 4 - CONFIRMAR:
- Título: "✅ Confirmar Cita"
- Card grande de resumen:
  
  SECCIÓN DOCTOR:
  - Foto circular
  - Nombre + especialidad
  - Icono teléfono + número
  
  SECCIÓN FECHA Y HORA:
  - Icono calendario grande
  - Fecha completa: "Miércoles, 27 de Noviembre 2025"
  - Hora: "8:30 AM" (destacado)
  - Duración: "30 minutos"
  
  SECCIÓN MOTIVO:
  - Textarea para describir motivo
  - Placeholder: "Ej: Control de rutina, dolor molar..."
  
  SECCIÓN ACCIONES:
  - Botón "Volver" (gris)
  - Botón "Confirmar Cita" (gradiente azul-verde, grande)

INDICADOR DE PROGRESO:
- Barra superior con 4 círculos
- Completados: Verde con check
- Actual: Azul pulsante
- Pendientes: Gris
- Líneas conectoras

CARACTERÍSTICAS:
- Navegación: Botones "Atrás" y "Siguiente"
- "Siguiente" deshabilitado hasta seleccionar
- Animaciones entre pasos (slide)
- Loading spinner al confirmar
- Success modal al completar:
  * Confetti animation
  * "¡Cita Agendada!"
  * Detalles de la cita
  * Botones: "Ver Mis Citas" | "Agendar Otra"

DISEÑO:
- Container max-w-4xl centrado
- Fondo blanco con sombra
- Bordes redondeados grandes
- Padding generoso
- Espaciado consistente
- Iconos grandes y claros
- Colores: Azul primario, verde success, rojo error

RESPONSIVE:
- Desktop: 3-4 columnas
- Tablet: 2 columnas
- Móvil: 1 columna stack

TECNOLOGÍAS:
- React + TypeScript
- Tailwind CSS
- React Hook Form
- date-fns
- Framer Motion
- Lucide Icons

Genera wizard completo funcional con validación en cada paso.
```

---

## 📋 PROMPT 4 - Historial Clínico con Timeline

### **Prompt para v0.dev:**

```
Crea una vista de historial clínico completo con timeline visual y filtros avanzados.

DISEÑO:

1. HEADER:
   - Título: "🏥 Historial Clínico Completo"
   - Subtítulo: "Todos tus registros médicos dentales"
   - Botón "Volver"

2. ESTADÍSTICAS (3 cards):
   - Total Episodios: 15
   - Documentos: 10
   - Último Registro: "15 Nov"
   * Iconos grandes, colores distintivos

3. FILTROS (card expandible):
   - Título: "🔍 Filtros"
   - Campo búsqueda (texto libre)
   - Select tipo episodio: Consulta, Emergencia, Control, Tratamiento
   - Date range picker (desde - hasta)
   - Botón "Limpiar filtros" (rojo, solo visible si hay filtros)

4. TOGGLE VISTA:
   - Dos botones: "📋 Lista" | "⏱️ Timeline"
   - Activo: Azul sólido
   - Inactivo: Gris claro
   - Contador: "15 de 15 episodios"

5. VISTA LISTA:
   - Agrupado por mes: "Noviembre 2025", "Octubre 2025"...
   - Cards de episodio expandibles:
     
     HEADER CARD:
     - Icono grande tipo (🩺 consulta, 🚨 emergencia, etc)
     - Badge tipo (color coded)
     - Fecha y hora
     - Diagnóstico (título bold)
     - Doctor nombre
     - Badge documentos adjuntos (📎 2 documentos)
     - Botón expand (▼/▲)
     
     CONTENIDO EXPANDIDO:
     - Sección "🦷 Tratamiento Realizado" (fondo verde claro)
     - Sección "📝 Notas del Odontólogo" (fondo amarillo claro)
     - Grid documentos adjuntos:
       * Preview imagen si es foto/radiografía
       * Icono tipo documento
       * Nombre archivo
       * Badge tipo
       * Botón descargar
     - Link a cita relacionada (si existe)
     - Botón "Ver detalle completo →"

6. VISTA TIMELINE:
   - Línea vertical central (azul)
   - Episodios alternados izquierda/derecha
   - Cada episodio:
     * Círculo grande en la línea (icono tipo)
     * Card con shadow flotante
     * Badge tipo
     * Fecha destacada
     * Diagnóstico
     * Tratamiento resumido
     * Doctor
     * Documentos count

7. GALERÍA DOCUMENTOS (abajo):
   - Título: "📁 Todos los Documentos (10)"
   - Select filtro tipo
   - Grid 3 columnas:
     * Preview imagen o icono grande
     * Badge tipo (color)
     * Nombre archivo
     * Descripción (2 líneas max)
     * Fecha
     * Botón "⬇️ Descargar"

8. EMPTY STATES:
   - Sin episodios: Ilustración + "No hay episodios"
   - Sin resultados filtro: "🔍 No se encontraron episodios" + botón limpiar

CARACTERÍSTICAS:
- Lazy loading scroll infinito
- Skeleton loading
- Smooth scroll entre secciones
- Animaciones de expand/collapse
- Hover effects en cards
- Lightbox para imágenes
- Download con progress bar
- Responsive stacking

COLORES TIPO EPISODIO:
- Consulta: Azul (#3B82F6)
- Emergencia: Rojo (#EF4444)
- Control: Verde (#10B981)
- Tratamiento: Púrpura (#8B5CF6)

TECNOLOGÍAS:
- React + TypeScript
- Tailwind CSS
- Framer Motion
- React Window (virtualización)
- date-fns
- Lucide Icons

Genera componente completo con todas las vistas.
```

---

## 📋 PROMPT 5 - Detalle de Episodio Clínico

### **Prompt para v0.dev:**

```
Crea una vista de detalle completo de episodio clínico con diseño médico profesional.

ESTRUCTURA:

1. NAVEGACIÓN SUPERIOR:
   - Botón "← Volver al Historial"
   - Navegación episodios:
     * "← Anterior" (deshabilitado si es el primero)
     * "Siguiente →" (deshabilitado si es el último)

2. HEADER DESTACADO:
   - Card grande con:
     * Icono tipo 6xl (🩺)
     * Badge tipo (color)
     * Fecha y hora completa
     * Diagnóstico (h1 grande, bold)
     * Subtexto: "Episodio #45 - Registrado el 15/11/2025"

3. LAYOUT 2 COLUMNAS:

   COLUMNA PRINCIPAL (2/3):
   
   A) INFORMACIÓN CLÍNICA:
      - Título: "📋 Información Clínica Completa"
      
      Sección DIAGNÓSTICO:
      - Fondo azul claro con borde
      - Título: "🔍 Diagnóstico"
      - Texto completo (multi-línea)
      
      Sección TRATAMIENTO:
      - Fondo verde claro con borde
      - Título: "🦷 Tratamiento Realizado"
      - Texto detallado (preservar saltos línea)
      
      Sección NOTAS:
      - Fondo amarillo claro con borde
      - Título: "📝 Notas del Odontólogo"
      - Texto observaciones
   
   B) DOCUMENTOS ADJUNTOS:
      - Título: "📎 Documentos Adjuntos (3)"
      - Grid 2 columnas:
        
        RADIOGRAFÍA:
        - Preview imagen grande (hover zoom)
        - Badge "RADIOGRAFÍA" púrpura
        - Nombre archivo
        - Descripción
        - Fecha subida + "Por: Dr. Juan"
        - Botón "⬇️ Descargar" azul
        - Click imagen: Modal fullscreen
        
        RECETA:
        - Icono documento grande
        - Badge "RECETA" verde
        - Nombre archivo
        - Descripción
        - Fecha + subido por
        - Botón descargar
   
   C) CITA RELACIONADA:
      - Card destacado
      - Título: "📅 Cita Relacionada"
      - Info cita:
        * Número
        * Fecha y hora
        * Motivo
        * Badge estado
        * Duración
      - Botón "Ver detalle de la cita →"

   COLUMNA LATERAL (1/3):
   
   A) PROFESIONAL A CARGO:
      - Card centrado
      - Avatar grande circular (o icono 👨‍⚕️)
      - Nombre doctor (bold)
      - Especialidad (azul)
      - Email (link mailto)
      - Botón "📅 Agendar con este doctor" verde

   B) INFORMACIÓN ADICIONAL:
      - Card metadata
      - Título: "📅 Información Adicional"
      - Creado: fecha completa
      - Última actualización: fecha (si diferente)
   
   C) ACCIONES RÁPIDAS:
      - Card acciones
      - Título: "⚡ Acciones"
      - Botón "🖨️ Imprimir Episodio" azul
      - Botón "📅 Agendar Consulta" verde

4. MODAL IMAGEN FULLSCREEN:
   - Fondo negro 90% opacidad
   - Imagen centrada max-w/max-h
   - Botón cerrar (X) esquina superior
   - Click fuera cierra
   - Zoom suave con animación

CARACTERÍSTICAS:
- Diseño limpio y espaciado
- Jerarquía visual clara
- Secciones bien delimitadas
- Colores institucionales
- Responsive (columnas apilan en móvil)
- Print-friendly CSS
- Loading skeleton
- Error boundaries

ANIMACIONES:
- Fade in al cargar
- Smooth scroll
- Hover effects sutiles
- Transitions 200-300ms

TECNOLOGÍAS:
- React + TypeScript
- Tailwind CSS
- Framer Motion
- Radix UI (modal)
- Lucide Icons

Genera vista completa con todos los componentes.
```

---

## 📋 PROMPT 6 - Sistema de Componentes Base

### **Prompt para v0.dev:**

```
Crea un sistema de componentes reutilizables base para una aplicación médica dental moderna.

COMPONENTES A CREAR:

1. BUTTON (variantes):
   - Primary: Azul sólido, hover más oscuro
   - Secondary: Gris claro, hover gris medio
   - Success: Verde, hover oscuro
   - Danger: Rojo, hover oscuro
   - Ghost: Transparente, hover gris claro
   - Tamaños: sm, md, lg, xl
   - Loading state: Spinner
   - Disabled state: Opaco 50%
   - Con icono izquierda/derecha opcional

2. CARD:
   - Variantes: default, outlined, elevated
   - Header opcional con título + acciones
   - Body con padding
   - Footer opcional
   - Hover effect sutil
   - Click effect si interactivo

3. BADGE:
   - Variantes: info, success, warning, error, neutral
   - Tamaños: sm, md, lg
   - Con icono opcional
   - Dot indicator opcional

4. ALERT/NOTIFICATION:
   - Tipos: info (azul), success (verde), warning (amarillo), error (rojo)
   - Con icono grande
   - Título + descripción
   - Botón acción opcional
   - Botón cerrar (X)
   - Auto-dismiss opcional

5. INPUT FIELD:
   - Label flotante
   - Icono izquierda opcional
   - Error state con mensaje
   - Helper text
   - Disabled state
   - Tamaños: sm, md, lg

6. SELECT/DROPDOWN:
   - Label
   - Placeholder
   - Opciones con iconos opcionales
   - Búsqueda integrada (multi opciones)
   - Multi-select opcional
   - Error state

7. MODAL/DIALOG:
   - Overlay oscuro
   - Contenedor centrado
   - Header con título + cerrar
   - Body scrollable
   - Footer con acciones
   - Tamaños: sm, md, lg, xl, full
   - Animación fade + scale

8. TABS:
   - Horizontal/vertical
   - Con iconos
   - Badge contador opcional
   - Animación slide underline
   - Disabled state

9. SKELETON LOADER:
   - Card skeleton
   - List skeleton
   - Text skeleton (líneas)
   - Avatar skeleton
   - Animación shimmer

10. EMPTY STATE:
    - Ilustración/icono grande
    - Título
    - Descripción
    - Botón acción
    - Variantes por contexto

ESPECIFICACIONES:

COLORES (Tailwind):
- Primary: blue-600 (#3B82F6)
- Success: green-500 (#10B981)
- Warning: yellow-500 (#F59E0B)
- Error: red-500 (#EF4444)
- Neutral: gray-500 (#6B7280)

TIPOGRAFÍA:
- Font: Inter
- Escalas: text-xs a text-4xl
- Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

ESPACIADO:
- Padding interno: p-4 (md), p-6 (lg)
- Gaps: gap-2, gap-4, gap-6
- Margins: mt-4, mb-6, etc.

SOMBRAS:
- sm: shadow-sm
- md: shadow-md
- lg: shadow-lg
- xl: shadow-xl

ANIMACIONES:
- Duration: 150ms, 200ms, 300ms
- Easing: ease-in-out
- Hover: scale, brightness, shadow

ACCESIBILIDAD:
- ARIA labels
- Keyboard navigation
- Focus visible
- Screen reader support

ESTRUCTURA:
Cada componente en archivo separado con:
- TypeScript interfaces
- Props con valores por defecto
- Composición de variantes
- Storybook-ready
- Comentarios JSDoc

TECNOLOGÍAS:
- React + TypeScript
- Tailwind CSS
- Class Variance Authority (cva)
- Radix UI primitives
- Lucide Icons

Genera sistema completo de componentes con ejemplos de uso.
```

---

## 🎯 CÓMO USAR ESTOS PROMPTS EN v0.dev:

### **Paso 1:** Ir a [v0.dev](https://v0.dev)

### **Paso 2:** Copiar el prompt que necesites

### **Paso 3:** Pegarlo en v0.dev y generar

### **Paso 4:** Revisar el código generado

### **Paso 5:** Hacer ajustes específicos con prompts de refinamiento:

```
Refinamientos comunes:
- "Hazlo más moderno con gradientes"
- "Agrega animaciones con framer-motion"
- "Hazlo responsive para móvil"
- "Cambia los colores a [paleta específica]"
- "Agrega dark mode"
- "Incluye loading states"
- "Agrega empty states"
```

### **Paso 6:** Exportar y usar en tu proyecto

---

## 💡 TIPS PARA MEJORES RESULTADOS:

1. ✅ **Sé específico** con colores, tamaños, comportamientos
2. ✅ **Menciona tecnologías** que quieres usar
3. ✅ **Incluye referencias** de diseño (Vercel, Linear, etc.)
4. ✅ **Especifica responsive** behavior
5. ✅ **Pide código completo** funcional
6. ✅ **Itera** con prompts de refinamiento

---

## 🎨 PALETA DE COLORES RECOMENDADA:

```css
/* Colores principales */
--primary: #3B82F6;      /* Azul médico confiable */
--success: #10B981;      /* Verde salud */
--warning: #F59E0B;      /* Amarillo atención */
--error: #EF4444;        /* Rojo urgencia */

/* Neutros */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-500: #6B7280;
--gray-700: #374151;
--gray-900: #111827;

/* Gradientes */
--gradient-primary: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
--gradient-success: linear-gradient(135deg, #10B981 0%, #059669 100%);
```

---

## 🚀 ORDEN SUGERIDO DE IMPLEMENTACIÓN:

1. **Prompt 6** - Sistema de componentes base (primero)
2. **Prompt 1** - Dashboard (core)
3. **Prompt 2** - Odontograma (visual impact)
4. **Prompt 4** - Historial (contenido)
5. **Prompt 5** - Detalle episodio
6. **Prompt 3** - Agendamiento (funcionalidad clave)

---

**¡Listo!** Con estos prompts puedes generar un diseño completo, moderno y profesional en v0.dev. 🎨✨

Cada prompt está optimizado para obtener código funcional de alta calidad que solo necesitarás conectar con tu backend.
