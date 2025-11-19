# Design System: Clinical Management Platform

**Target:** v0.dev  
**Framework:** React + TypeScript + Tailwind CSS  
**Version:** 2.0

---

## Color Palette

### Primary System Colors

```css
/* Professional Blue-Gray Palette */
--primary-50:  #f8fafc;   /* slate-50 */
--primary-100: #f1f5f9;   /* slate-100 */
--primary-200: #e2e8f0;   /* slate-200 */
--primary-300: #cbd5e1;   /* slate-300 */
--primary-400: #94a3b8;   /* slate-400 */
--primary-500: #64748b;   /* slate-500 */
--primary-600: #475569;   /* slate-600 - Main brand */
--primary-700: #334155;   /* slate-700 */
--primary-800: #1e293b;   /* slate-800 */
--primary-900: #0f172a;   /* slate-900 */

/* Accent - Medical Teal */
--accent-50:  #f0fdfa;    /* teal-50 */
--accent-100: #ccfbf1;    /* teal-100 */
--accent-200: #99f6e4;    /* teal-200 */
--accent-300: #5eead4;    /* teal-300 */
--accent-400: #2dd4bf;    /* teal-400 */
--accent-500: #14b8a6;    /* teal-500 - Accent brand */
--accent-600: #0d9488;    /* teal-600 */
--accent-700: #0f766e;    /* teal-700 */

/* Semantic Colors */
--success:  #059669;      /* emerald-600 - Darker, more professional */
--warning:  #d97706;      /* amber-600 - Less bright */
--error:    #dc2626;      /* red-600 - More serious */
--info:     #0284c7;      /* sky-600 - Softer than bright blue */
```

### Background System

```css
/* Sophisticated layering */
--bg-base:      #ffffff;
--bg-subtle:    #f8fafc;  /* slate-50 */
--bg-muted:     #f1f5f9;  /* slate-100 */
--bg-emphasis:  #e2e8f0;  /* slate-200 */

/* Cards and surfaces */
--surface-base:    rgba(255, 255, 255, 0.8);
--surface-overlay: rgba(248, 250, 252, 0.9);
--surface-glass:   rgba(255, 255, 255, 0.6);
```

---

## Dashboard Implementation

```
Build a clinical management dashboard with professional, muted aesthetic.

COLOR SYSTEM:

Primary Brand: slate-600 (#475569)
Accent: teal-500 (#14b8a6)
Success: emerald-600 (#059669)
Warning: amber-600 (#d97706)
Error: red-600 (#dc2626)

Backgrounds:
- Base: white
- Subtle: slate-50
- Muted: slate-100
- Cards: white with subtle border (slate-200)

Text:
- Primary: slate-900
- Secondary: slate-600
- Tertiary: slate-500
- Muted: slate-400

TYPOGRAPHY:

System font stack:
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;

Weights:
- Regular: 400
- Medium: 500
- Semibold: 600

Sizes:
- xs: 0.75rem (12px)
- sm: 0.875rem (14px)
- base: 1rem (16px)
- lg: 1.125rem (18px)
- xl: 1.25rem (20px)
- 2xl: 1.5rem (24px)
- 3xl: 1.875rem (30px)

LAYOUT STRUCTURE:

Header (64px height, fixed top):
- Background: white
- Border bottom: 1px solid slate-200
- Shadow: subtle (0 1px 3px rgba(0,0,0,0.05))
- Logo: Left (slate-700 text)
- Navigation: Center breadcrumbs (slate-600)
- Actions: Right (notifications + avatar)

Sidebar (256px width, fixed left):
- Background: slate-50
- Border right: 1px solid slate-200
- Navigation items:
  * Default: slate-600 text
  * Hover: slate-700 background, slate-900 text
  * Active: teal-50 background, teal-700 text, 3px left border teal-600
- Icons: 20px, stroke-width: 1.5
- CTA Button:
  * Background: teal-600
  * Hover: teal-700
  * Text: white
  * No gradient, solid color

Main Content Area:

1. Welcome Section
   Style: Clean card, no gradient
   - Background: white
   - Border: 1px solid slate-200
   - Border radius: 12px
   - Padding: 24px
   - Greeting: "Good morning, María" (slate-900, text-2xl)
   - Subtitle: "You have 3 appointments this week" (slate-600, text-base)
   - Action button: teal-600 solid (not gradient)

2. Stats Grid (4 columns)
   Card design:
   - Background: white
   - Border: 1px solid slate-200
   - Border radius: 8px
   - Padding: 20px
   - Hover: border-slate-300, shadow-sm
   - NO background colors (no blue, green, yellow, pink backgrounds)
   
   Each stat:
   - Icon: 40px, stroke-width: 1.5, slate-400
   - Value: slate-900, text-3xl, font-semibold
   - Label: slate-600, text-sm
   - Trend indicator (if applicable): Small badge
     * Positive: emerald-600 text, emerald-50 background
     * Negative: red-600 text, red-50 background

3. Alert Banner (if needed)
   - Background: amber-50
   - Border left: 3px solid amber-600
   - Icon: amber-600
   - Text: slate-900 (title), slate-700 (description)
   - Action link: amber-700 underline on hover

4. Appointments List
   Card per appointment:
   - Background: white
   - Border: 1px solid slate-200
   - Left accent: 4px solid based on status
     * Confirmed: teal-500
     * Pending: amber-500
     * Completed: emerald-500
   - Date badge: slate-100 background, slate-700 text
   - Doctor name: slate-900, font-medium
   - Details: slate-600, text-sm
   - Status badge:
     * Subtle backgrounds (teal-50, amber-50, emerald-50)
     * Darker text (teal-700, amber-700, emerald-700)

5. Activity Timeline
   - Vertical line: slate-300, 2px
   - Event dots: 8px circles
     * Default: slate-400
     * Recent: teal-500
   - Event card:
     * Background: slate-50
     * Border: 1px solid slate-200
     * Hover: white background
   - Timestamps: slate-500, text-sm

INTERACTIONS:

Hover effects (subtle):
- Cards: border-slate-300, shadow-sm
- Buttons: Darken by one shade
- Links: Underline, no color change

Focus states:
- Ring: 2px solid teal-500
- Ring offset: 2px
- No glow, clean outline

Active states:
- Slightly darker background
- No scale transforms

Transitions:
- Duration: 150ms
- Easing: ease-in-out
- Properties: background-color, border-color, box-shadow

SHADOWS (very subtle):

- xs: 0 1px 2px rgba(0,0,0,0.05)
- sm: 0 1px 3px rgba(0,0,0,0.1)
- md: 0 4px 6px rgba(0,0,0,0.07)
- lg: 0 10px 15px rgba(0,0,0,0.1)

NO dramatic shadows, no neon glows, no colorful shadows.

SPACING:

Consistent 8px grid:
- Tight: 8px
- Normal: 16px
- Relaxed: 24px
- Loose: 32px

BORDERS:

All borders: 1px solid slate-200
Hover borders: 1px solid slate-300
Active borders: 2px solid teal-500

Border radius:
- sm: 6px (buttons, badges)
- md: 8px (cards)
- lg: 12px (modals, major cards)
- full: 9999px (avatars, pills)

ICONS:

Library: Lucide React
Size: 20px default, 24px for features, 16px for inline
Stroke width: 1.5 (not 2, more refined)
Color: Inherit from text color

BUTTONS:

Primary:
- Background: teal-600
- Text: white
- Hover: teal-700
- Active: teal-800
- Padding: 10px 16px
- Border radius: 6px
- Font weight: 500
- NO gradients

Secondary:
- Background: white
- Border: 1px solid slate-300
- Text: slate-700
- Hover: slate-50 background

Ghost:
- Background: transparent
- Text: slate-600
- Hover: slate-100 background

Danger:
- Background: red-600
- Text: white
- Hover: red-700

BADGES:

Solid style (no outline):
- Small padding: 4px 8px
- Font size: 12px
- Font weight: 500
- Border radius: 4px

Status badges:
- Success: emerald-50 bg, emerald-700 text
- Warning: amber-50 bg, amber-700 text
- Error: red-50 bg, red-700 text
- Info: sky-50 bg, sky-700 text
- Neutral: slate-100 bg, slate-700 text

CHARTS:

Library: Recharts
Color palette for data:
- Series 1: teal-500
- Series 2: slate-400
- Series 3: emerald-500
- Series 4: sky-500
- Series 5: amber-500

Grid lines: slate-200
Axis text: slate-500
Tooltip: white background, slate-900 text, subtle shadow

NO gradients in bars or areas.

RESPONSIVE:

Desktop (≥1280px):
- Sidebar: 256px fixed
- Content: max-width 1400px, centered
- Stats grid: 4 columns

Tablet (768-1279px):
- Sidebar: Collapsible overlay
- Stats grid: 2x2
- Reduced spacing

Mobile (<768px):
- Bottom navigation (5 items)
- Stats grid: 1 column
- Full-width cards
- Sticky header

ACCESSIBILITY:

- Contrast ratios: WCAG AA minimum (4.5:1)
- Focus indicators: Visible 2px ring
- Semantic HTML
- ARIA labels on icons
- Keyboard navigation
- Screen reader support

TECH STACK:

- React 18+
- TypeScript 5+
- Tailwind CSS 3.4+
- Lucide React (icons)
- Recharts (charts)
- date-fns (dates)
- Radix UI (accessible primitives)

DESIGN REFERENCES:

- Linear (clean, professional interface)
- Stripe Dashboard (data presentation)
- GitHub UI (neutral, functional)
- Notion (organized, clear hierarchy)
- Vercel Dashboard (modern but not flashy)

AVOID:

- Bright, saturated colors (no #0EA5E9, #8B5CF6, #F59E0B)
- Gradients (especially in backgrounds)
- Neon glows or colorful shadows
- Overly rounded corners (max 12px)
- Emoji in UI
- Playful language
- Animated illustrations
- Heavy animations
- Glassmorphism effects
- Neumorphism
- 3D transforms

AIM FOR:

- Clean, professional appearance
- Medical/clinical credibility
- Enterprise-grade polish
- Subtle, refined details
- Functional over decorative
- Scannable information hierarchy
- Comfortable extended use
- Trust and reliability

Generate clean, production-ready code with this refined aesthetic.
```

---

## Odontogram Implementation

```
Build dental odontogram with professional clinical aesthetic.

COLOR PALETTE:

Use same system colors as dashboard:
- Primary: slate-600
- Accent: teal-500
- Backgrounds: white, slate-50, slate-100

LAYOUT:

Header:
- Title: "Dental Chart" (slate-900, text-2xl)
- Subtitle: "FDI Notation System" (slate-600, text-sm)
- Back button: slate-600

Health Overview Card:
- Background: white
- Border: 1px solid slate-200
- Padding: 24px
- Layout: Horizontal split

Left side - Score:
- Circular progress (SVG)
  * Track: slate-200
  * Progress: teal-500
  * Stroke width: 8px
  * Size: 120px
- Score: "31/32" (slate-900, text-3xl)
- Label: "Healthy teeth" (slate-600, text-sm)
- Rating: "Excellent" (emerald-600, text-sm, font-medium)

Right side - Stats (4 items):
- Icon + Value + Label layout
- Icons: 20px, slate-400
- Values: slate-900, text-xl
- Labels: slate-600, text-sm
- Dividers: 1px slate-200 between items

Dental Grid:

Container:
- Background: slate-50
- Padding: 32px
- Border radius: 12px

Quadrant labels:
- Text: slate-700, text-sm, font-medium
- Position: Above each section

Midline separator:
- 2px solid slate-300
- Label: "Midline" (slate-500, text-xs)

TOOTH COMPONENT:

Size: 48px × 64px (smaller, more professional)
Shape: Rounded rectangle (border-radius: 6px 6px 2px 2px)

Structure:
- Number badge (top): 
  * Background: slate-100
  * Text: slate-700, 10px
  * Padding: 2px 6px
  * Border radius: 4px
  
- Status icon (center):
  * Size: 20px
  * Stroke width: 1.5
  
- Treatment indicator (bottom):
  * Small dot: 4px circle
  * Max 3 dots
  * Color: slate-400

TOOTH STATES (subtle, professional):

Healthy:
- Background: white
- Border: 1.5px solid emerald-500
- Icon: Check (emerald-600)
- NO background color

Treated:
- Background: white
- Border: 1.5px solid teal-500
- Icon: Tool (teal-600)
- Small "treated" label: teal-50 background, teal-700 text

Cavity:
- Background: white
- Border: 1.5px solid red-500
- Icon: AlertCircle (red-600)
- Subtle pulse: border only

Missing:
- Background: slate-50
- Border: 1.5px dashed slate-300
- Icon: Minus (slate-400)
- Opacity: 0.6

Observation:
- Background: white
- Border: 1.5px solid amber-500
- Icon: Eye (amber-600)

Implant:
- Background: white
- Border: 1.5px solid slate-500
- Icon: Zap (slate-600)
- Badge: "Implant" (slate-100 bg, slate-700 text)

INTERACTIONS:

Hover:
- Border: 2px solid (same color)
- Shadow: 0 2px 4px rgba(0,0,0,0.1)
- Scale: 1.05
- Transition: 150ms ease

Tooltip (on hover):
- Background: slate-900
- Text: white, 12px
- Padding: 8px 12px
- Border radius: 6px
- Arrow: 6px
- Shadow: 0 4px 6px rgba(0,0,0,0.2)
- Content:
  * Tooth name (font-medium)
  * Status
  * "X treatments" (if any)
  * "Click for details" (slate-300, 11px)

DETAIL MODAL:

Backdrop: rgba(0, 0, 0, 0.5)
Modal:
- Background: white
- Border radius: 12px
- Max width: 600px
- Padding: 0
- Shadow: 0 20px 25px rgba(0,0,0,0.15)

Header:
- Background: slate-50
- Border bottom: 1px solid slate-200
- Padding: 20px 24px
- Icon: 24px, slate-600
- Title: "Tooth #16" (slate-900, text-xl)
- Subtitle: "First Upper Right Molar" (slate-600, text-sm)
- Status badge: Right aligned

Body (padding: 24px):
- Information table:
  * Labels: slate-600, 13px
  * Values: slate-900, 14px, font-medium
  * Row spacing: 12px
  * Dividers: 1px slate-200

- Treatment timeline:
  * Vertical line: slate-300, 2px
  * Event circles: 8px, status color
  * Event cards:
    - Background: slate-50
    - Border: 1px solid slate-200
    - Padding: 12px
    - Date: slate-500, 12px
    - Treatment: slate-900, 14px
    - Doctor: slate-600, 13px

Footer:
- Border top: 1px solid slate-200
- Padding: 16px 24px
- Buttons: Aligned right
  * Close: Secondary button
  * "Schedule checkup": Primary button (teal-600)

ANIMATIONS:

Entry:
1. Fade in opacity (0 → 1)
2. Subtle scale (0.98 → 1)
3. Duration: 200ms
4. Easing: ease-out

Grid teeth:
- Stagger: 20ms delay each
- No dramatic effects

Hover:
- Smooth transition: 150ms
- Subtle lift, no rotation

RESPONSIVE:

Desktop:
- 4 quadrants in 2×2 grid
- Teeth: 48px × 64px
- Spacing: 8px between teeth

Tablet:
- 2×1 stack (upper/lower)
- Teeth: 44px × 60px

Mobile:
- Vertical stack all quadrants
- Teeth: 40px × 56px
- Horizontal scroll per quadrant
- Snap scroll

AVOID:

- Bright colored backgrounds
- Gradients
- 3D transforms
- Emoji icons
- Playful elements
- Complex animations

Generate professional, clinical-grade interface.
```

---

## Component Guidelines

### Cards

```tsx
// Standard card style
className="bg-white border border-slate-200 rounded-lg p-4 
           hover:border-slate-300 hover:shadow-sm
           transition-all duration-150"
```

### Buttons

```tsx
// Primary
className="bg-teal-600 text-white px-4 py-2 rounded-md
           hover:bg-teal-700 active:bg-teal-800
           font-medium text-sm
           transition-colors duration-150"

// Secondary
className="bg-white border border-slate-300 text-slate-700 px-4 py-2 rounded-md
           hover:bg-slate-50
           font-medium text-sm
           transition-colors duration-150"
```

### Badges

```tsx
// Status badge
className="px-2 py-1 rounded text-xs font-medium
           bg-emerald-50 text-emerald-700"
```

### Typography

```tsx
// Heading
className="text-2xl font-semibold text-slate-900"

// Subheading
className="text-lg font-medium text-slate-700"

// Body
className="text-base text-slate-600"

// Caption
className="text-sm text-slate-500"
```

---

**This design system prioritizes:**
- Professional medical aesthetic
- Subtle, refined color palette
- Clean, functional interface
- Enterprise-grade polish
- Long-term usability over trend
