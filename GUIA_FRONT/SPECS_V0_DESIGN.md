# Design Specifications for Dental Management System

**Version:** 1.0  
**Target Platform:** v0.dev  
**Stack:** React 18 + TypeScript + Tailwind CSS  
**Last Updated:** November 2025

---

## 1. Dashboard - Patient Portal

### 1.1 Functional Scope

Central interface consolidating patient's appointments, active treatments, financial status, and recent activity.

### 1.2 Implementation Prompt

```
Build a patient dashboard for dental clinic management system.

TECHNICAL SPECS:

Color System (Tailwind):
- Primary: sky-500 (#0EA5E9)
- Accent: violet-500 (#8B5CF6)
- Success: emerald-500 (#10B981)
- Warning: amber-500 (#F59E0B)
- Error: rose-500 (#EF4444)

Typography:
- UI: Inter (400, 500, 600)
- Headings: Poppins (600, 700)
- Monospace: JetBrains Mono (data display)

Icons: Lucide React, 20-24px base size

LAYOUT STRUCTURE:

Header (sticky, 64px height):
- Logo (left)
- Breadcrumb (center)
- Notifications + Avatar (right)
- Style: backdrop-blur-xl bg-white/80

Sidebar (fixed left, 240px):
Navigation:
  - Home
  - Appointments
  - Odontogram
  - Medical History
  - Billing
  - Settings
CTA: "Schedule Appointment" (gradient button)
Support link (bottom)

Main Content:

1. Hero Section
   - Patient greeting with name
   - Contextual subtitle
   - Gradient background (sky-500 to violet-500)
   - Padding: 32px, rounded-2xl

2. Stats Grid (4 columns, responsive)
   Cards showing:
   - Upcoming appointments (count)
   - Active treatments (count)
   - Pending requests (count)
   - Outstanding balance (currency)
   
   Each card:
   - Icon (48px)
   - Value (text-3xl font-bold)
   - Label (text-sm text-gray-600)
   - Circular progress indicator
   - Hover: lift 4px, shadow-lg

3. Conditional Alert Banner
   Display when: pending actions > 0
   Layout: Icon + Message + Action buttons
   Style: bg-amber-50 border-l-4 border-amber-500

4. Activity Chart
   Type: Bar chart (Recharts)
   Data: Last 6 months activity
   Height: 320px
   Interactive tooltip

5. Upcoming Appointments List
   Max 3 visible, "View all" link
   Each card:
   - Date badge
   - Doctor name + specialty
   - Appointment reason
   - Color-coded status badge
   - Action buttons
   
6. Recent Activity Timeline
   Vertical timeline with:
   - Payment events
   - Completed appointments
   - Treatment approvals
   Relative timestamps ("2 days ago")

INTERACTIONS:

Stats Cards:
- Hover: translateY(-4px), 200ms transition
- Mount: Count-up animation 1.5s
- Click: Navigate to detail

Timeline:
- Click: Expand details (spring animation)
- Scroll: Stagger fade-in

ANIMATIONS:

Entry sequence (staggered):
1. Hero: fade + translateY, 300ms
2. Stats: delay 100ms each
3. Chart: bar draw animation 800ms
4. Cards: stagger 60ms

RESPONSIVE:

Desktop (≥1280px):
- Sidebar fixed
- Stats: 4 columns
- Chart full width

Tablet (768-1279px):
- Sidebar collapsible
- Stats: 2×2 grid

Mobile (<768px):
- Bottom navigation
- Stats: 2×2 compact
- Chart: horizontal scroll

ACCESSIBILITY:

- Contrast: 4.5:1 minimum
- Focus indicators: ring-2 ring-sky-500
- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader optimized
- Respects prefers-reduced-motion

TECH REQUIREMENTS:

- React 18.3+
- TypeScript 5+ (strict mode)
- Tailwind CSS 3.4+
- Framer Motion 11+
- Recharts 2.10+
- Radix UI primitives
- Lucide React icons

Generate production-ready code with:
- Component composition
- Custom hooks
- Error boundaries
- Lazy loading
- Performance optimization (memo, useMemo)
```

---

## 2. Odontogram - Interactive Dental Chart

### 2.1 Functional Scope

Interactive visualization of patient's dental health status using FDI notation system. Displays treatment history per tooth.

### 2.2 Implementation Prompt

```
Build interactive dental odontogram using FDI notation system.

FDI SYSTEM:

Quadrants:
- 1: Upper right (11-18)
- 2: Upper left (21-28)
- 3: Lower left (31-38)
- 4: Lower right (41-48)

Tooth positions:
- 1-2: Incisors
- 3: Canines
- 4-5: Premolars
- 6-7-8: Molars

LAYOUT:

Header:
- Title: "My Odontogram"
- Subtitle: "Interactive dental map"
- Back button

Health Score (prominent):
- Circular progress (SVG)
- Percentage (large text)
- Rating: Excellent/Good/Fair/Poor
- Animated on mount

Stats Cards (4 columns):
- Healthy teeth: X/32 (green)
- Treated: X/32 (blue)
- Missing: X/32 (gray)
- Under observation: X/32 (yellow)

View Controls (tabs):
- Complete view
- Upper arcade
- Lower arcade
- Right side
- Left side

Dental Grid:

Upper Arcade:
[Quadrant 1: 11-18] | [Quadrant 2: 21-28]

Midline separator (visual divider)

Lower Arcade:
[Quadrant 4: 41-48] | [Quadrant 3: 31-38]

TOOTH COMPONENT:

Structure:
- Size: 56px × 80px
- Shape: Rounded top (simulates tooth crown)
- Number badge (top, small)
- Status icon (center, 32px)
- Treatment count dots (bottom, max 5)

States with colors:

HEALTHY:
- Background: linear-gradient(135deg, #D1FAE5, #A7F3D0)
- Border: 3px solid #10B981
- Icon: ✓
- Animation: Subtle heartbeat

TREATED:
- Background: linear-gradient(135deg, #DBEAFE, #BFDBFE)
- Border: 3px solid #3B82F6
- Icon: Wrench

CAVITY:
- Background: linear-gradient(135deg, #FEE2E2, #FECACA)
- Border: 3px solid #EF4444
- Icon: Warning
- Animation: Pulse

MISSING:
- Background: linear-gradient(135deg, #F3F4F6, #E5E7EB)
- Border: 2px dashed #9CA3AF
- Icon: Circle
- Opacity: 0.5

OBSERVATION:
- Background: linear-gradient(135deg, #FEF3C7, #FDE68A)
- Border: 3px solid #F59E0B
- Icon: Eye

IMPLANT:
- Background: linear-gradient(135deg, #EDE9FE, #DDD6FE)
- Border: 3px solid #8B5CF6
- Icon: Screw

CSS 3D EFFECTS:

.tooth {
  perspective: 1000px;
  clip-path: polygon(20% 0%, 80% 0%, 100% 40%, 100% 100%, 0% 100%, 0% 40%);
  box-shadow: 
    0 4px 6px rgba(0,0,0,0.1),
    0 10px 15px rgba(0,0,0,0.15),
    inset 0 2px 4px rgba(255,255,255,0.3);
}

.tooth:hover {
  transform: scale(1.15) rotateY(5deg) translateY(-8px);
  box-shadow: 0 20px 25px rgba(0,0,0,0.15);
}

TOOLTIP (on hover):
- Tooth name (e.g., "First Upper Right Molar")
- Current status
- Treatment count
- List of recent treatments (max 3)
- "View full history" link

DETAIL MODAL (on click):

Header:
- Gradient background (blue-purple)
- Large tooth icon
- Tooth number + name
- Status badge

Content:
- Tooth information table:
  * Type
  * Position
  * Quadrant
  * Current status
  * Last checkup date

- Treatment timeline:
  * Vertical timeline
  * Chronological list
  * Treatment type
  * Doctor name
  * Date
  * Link to full episode

Footer:
- Close button
- "Schedule checkup" CTA

INTERACTIONS:

Hover:
- Scale: 1 → 1.15
- Shadow expansion
- Tooltip slide-up (spring animation)
- Adjacent teeth: subtle scale 1.05

Click:
- Ripple effect from click point
- Modal: backdrop blur + scale-in

ANIMATIONS:

Mount sequence:
1. Health score: count-up 0 → X%, 1.5s
2. Circular progress: stroke-dashoffset animation
3. Teeth: Grid stagger (50ms delay)
   - Fade in (opacity 0 → 1)
   - Scale (0.8 → 1)
   - RotateY (90deg → 0)

RESPONSIVE:

Desktop (>1024px):
- 2×2 quadrant grid
- Teeth: 56px × 80px
- Lateral tooltips

Tablet (768-1023px):
- Stack 2×1 (upper/lower)
- Teeth: 48px × 72px

Mobile (<767px):
- Vertical stack
- Teeth: 44px × 64px
- Tap for tooltip
- Swipe navigation
- Modal: bottom sheet

TECH REQUIREMENTS:

- React 18 + TypeScript 5
- Tailwind CSS 3.4
- Framer Motion 11
- Radix UI (modal, tooltip)
- Lucide React (icons)

Performance:
- CSS containment on tooth elements
- GPU acceleration (translate3d)
- Lazy load modal
- Virtualization if >32 teeth
- Memoize expensive renders

Accessibility:
- ARIA label: "Tooth 16, first upper right molar, healthy, 2 treatments"
- Keyboard navigation (Tab, Arrow keys)
- Focus trap in modal
- Reduced motion support

Generate clean, maintainable code with inline documentation.
```

---

## 3. Appointment Booking - Wizard Flow

### 3.1 Functional Scope

Multi-step booking wizard for scheduling appointments. Guides patient through doctor selection, date/time picking, and confirmation.

### 3.2 Implementation Prompt

```
Build appointment booking wizard with 4-step flow.

WIZARD STRUCTURE:

Progress Indicator (always visible):
[●━━━━ ○━━━━ ○━━━━ ○]
[Step 1 of 4]

States:
- Completed: Green with checkmark
- Current: Blue with pulse
- Pending: Gray
- Connecting lines animate on progress

STEP 1: SELECT DOCTOR

Layout:
- Title: "Select Your Dentist"
- Search input (filter by name/specialty)
- Grid: 2-3 columns (responsive)

Doctor Card:
- Photo (circular, 96px)
- Name (text-lg font-semibold)
- Specialty badge (blue)
- Rating (stars, out of 5)
- Experience years
- Languages
- "Select" button

States:
- Hover: Elevate, shadow expansion
- Selected: Blue border (3px), checkmark badge

STEP 2: SELECT DATE

Layout:
- Title: "Choose Date"
- Selected doctor info (small card)
- Calendar (monthly view)
- Month navigation (prev/next)

Calendar:
- 7 columns (Mon-Sun)
- Day states:
  * Past: Disabled, opacity 0.3
  * No availability: Crossed out, red
  * Available: Green background
  * Today: Double border, "TODAY" badge
  * Selected: Blue solid, checkmark

Legend:
- Green: Available
- Gray: Unavailable
- Blue: Selected
- Border: Today

STEP 3: SELECT TIME

Layout:
- Title: "Choose Time"
- Selected date display (prominent)
- Selected doctor + location
- Time slots grid (3-4 columns)

Time Slot:
- Format: "8:00 AM", "8:30 AM", etc.
- 30-minute intervals
- Range: 8:00 AM - 6:00 PM

States:
- Occupied:
  * Gray background
  * Lock icon
  * Disabled cursor
  
- Available:
  * White with border
  * Checkmark icon
  * Hover: Blue tint
  
- Selected:
  * Blue solid
  * Large checkmark
  * Glow effect

Popular indicator: Fire icon for frequently booked times

STEP 4: CONFIRM

Layout:
- Title: "Confirm Appointment"
- Summary card (large, centered)

Summary Sections:

1. Doctor:
   - Photo
   - Name + specialty
   - Phone number

2. Date & Time:
   - Full date: "Wednesday, November 27, 2025"
   - Time: "8:30 AM" (prominent)
   - Duration: "30 minutes"
   - Location

3. Reason:
   - Textarea (expandable)
   - Placeholder: "e.g., Regular checkup, molar pain..."
   - Character count: 0/500

4. Reminders:
   - Checkbox: Email 24h before
   - Checkbox: SMS 2h before
   - Checkbox: WhatsApp (optional)

Actions:
- "Back" button (gray)
- "Confirm Appointment" button (gradient, large)

SUCCESS MODAL:

After confirmation:
- Confetti animation
- Large checkmark with draw animation
- Title: "Appointment Booked!"
- Confirmation details
- Appointment code: #CT-2025-XXXXX
- Confirmation sent: Email + SMS
- Actions:
  * "View My Appointments"
  * "Schedule Another"
  * "Download .ics"

NAVIGATION:

- "Back" and "Next" buttons
- "Next" disabled until selection made
- Step transitions: Slide animation (300ms)
- Validation per step

INTERACTIONS:

Doctor cards:
- Mount: Stagger fade-in
- Hover: All properties smooth transition
- Select: Checkmark bounce

Calendar:
- Days: Fade-in stagger
- Month change: Horizontal slide
- Day hover: Tooltip with slot count

Time slots:
- Mount: Grid stagger
- Scroll: Infinite smooth scroll
- Select: Pulse effect

Confirm:
- Submit: Button squeeze + spinner
- Success: Confetti burst
- Modal: Scale-in + backdrop blur

RESPONSIVE:

Desktop (>1024px):
- Doctors: 3 columns
- Calendar: Full monthly
- Slots: 4 columns

Tablet (768-1023px):
- Doctors: 2 columns
- Calendar: Compact monthly
- Slots: 3 columns

Mobile (<768px):
- Doctors: 1 column (horizontal cards)
- Calendar: Week view with swipe
- Slots: 2 columns
- Bottom navigation

VALIDATION:

Step 1: Doctor must be selected
Step 2: Date must be future + available
Step 3: Slot must be available (check race condition)
Step 4: Reason optional but recommended

Error handling:
- Toast notifications
- Inline error messages
- Auto-retry on network errors
- Suggest alternatives if slot taken

TECH REQUIREMENTS:

- React Hook Form (form state)
- Zod (validation schemas)
- date-fns (date manipulation)
- Framer Motion (animations)
- canvas-confetti (celebration)
- React Hot Toast (notifications)

Generate complete wizard with validation and error handling.
```

---

## 4. Medical History - Timeline View

### 4.1 Functional Scope

Comprehensive medical history display with filtering, search, and document management.

### 4.2 Implementation Prompt

```
Build medical history interface with timeline and list views.

LAYOUT:

Header:
- Title: "Medical History"
- Subtitle: "Complete dental records"
- Back button

Stats Cards (3 cards):
- Total episodes: X
- Documents: X
- Last record: Date

Filters (expandable card):
- Search input (free text)
- Episode type selector:
  * Consultation
  * Emergency
  * Checkup
  * Treatment
- Date range picker
- "Clear filters" button (visible when active)

View Toggle:
- Button group: "List" | "Timeline"
- Active: Blue solid
- Counter: "X of Y episodes"

LIST VIEW:

Grouped by month: "November 2025", "October 2025"...

Episode Card (expandable):

Header (always visible):
- Type icon (large, color-coded)
- Type badge
- Date + time
- Diagnosis (title, bold)
- Doctor name
- Documents badge ("2 documents")
- Expand button

Expanded content:
- Treatment section (green background)
- Notes section (yellow background)
- Documents grid:
  * Image preview or file icon
  * File name
  * Type badge
  * Download button
- Related appointment link (if exists)
- "View full details" button

TIMELINE VIEW:

- Vertical line (center, blue)
- Episodes alternate left/right
- Each episode:
  * Large circle on line (type icon)
  * Floating card with shadow
  * Type badge
  * Date (prominent)
  * Diagnosis
  * Treatment summary
  * Doctor name
  * Document count

DOCUMENTS GALLERY:

Below main content:
- Title: "All Documents (X)"
- Type filter selector
- Grid: 3 columns

Document card:
- Image preview or icon
- Type badge (color-coded)
- File name
- Description (2 lines max, ellipsis)
- Date
- Download button

EMPTY STATES:

No episodes:
- Illustration
- Message: "No medical records yet"
- CTA: "Schedule first appointment"

No results:
- Icon: Search
- Message: "No episodes found"
- "Clear filters" button

EPISODE TYPES (color-coded):

- Consultation: Blue (#3B82F6)
- Emergency: Red (#EF4444)
- Checkup: Green (#10B981)
- Treatment: Purple (#8B5CF6)

INTERACTIONS:

Cards:
- Hover: Shadow expansion
- Click expand: Spring animation
- Collapse: Smooth height transition

Timeline:
- Scroll: Reveal animation
- Click: Navigate to detail

Documents:
- Hover: Scale 1.05
- Click: Lightbox (images) or download (files)
- Download: Progress bar

FEATURES:

- Lazy loading: Infinite scroll
- Skeleton loading: Shimmer effect
- Smooth scroll: Between sections
- Lightbox: Image full-screen view
- Download progress: Visual feedback

RESPONSIVE:

Desktop:
- Timeline: Alternating left/right
- Documents: 3 columns

Tablet:
- Timeline: Centered cards
- Documents: 2 columns

Mobile:
- Timeline: Vertical stack
- Documents: 1 column
- Sticky filters

TECH REQUIREMENTS:

- React Window (virtualization)
- Framer Motion (animations)
- date-fns (date formatting)
- React-use (hooks)

Generate complete history view with both display modes.
```

---

## 5. Technical Guidelines

### 5.1 Code Standards

- TypeScript strict mode
- ESLint + Prettier configuration
- Semantic HTML5
- CSS-in-JS via Tailwind
- Component composition over inheritance

### 5.2 Performance

- Code splitting per route
- Lazy loading for heavy components
- Image optimization (next/image or similar)
- Memoization: useMemo, useCallback, React.memo
- Virtual scrolling for long lists

### 5.3 Accessibility

- Semantic HTML tags
- ARIA attributes where needed
- Keyboard navigation
- Focus management
- Screen reader testing
- Color contrast compliance (WCAG 2.1 AA minimum)
- Support for prefers-reduced-motion

### 5.4 Testing

- Unit tests: Jest + React Testing Library
- E2E tests: Playwright
- Visual regression: Chromatic
- Accessibility: axe-core

### 5.5 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 6. Design Tokens

```css
/* Colors */
:root {
  --color-primary: #0ea5e9;
  --color-accent: #8b5cf6;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  
  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --font-display: 'Poppins', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}
```

---

## 7. Component Library

Recommended components from shadcn/ui:
- Button
- Card
- Badge
- Dialog
- Dropdown Menu
- Input
- Select
- Tabs
- Toast
- Tooltip
- Skeleton
- Progress

Custom components to build:
- Tooth (odontogram)
- Timeline
- Stats Card
- Appointment Card
- Document Card

---

**End of Specifications**

For implementation questions, refer to v0.dev documentation and the referenced libraries' official docs.
