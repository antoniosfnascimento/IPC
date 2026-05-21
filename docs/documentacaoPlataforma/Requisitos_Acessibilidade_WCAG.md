# Accessibility Requirements (WCAG 2.1) — CityFlow MVP

This document maps the essential WCAG 2.1 guidelines to the direct technical implementations the Frontend team (React + Tailwind CSS) must follow for the MVP. The criteria focus on the established personas (motor limitations, low vision and colour-blindness).

| ID | WCAG 2.1 criterion | Level | Goal on CityFlow | Technical implementation (React / Tailwind CSS) |
| :---: | :--- | :---: | :--- | :--- |
| **1.4.3** | **Minimum contrast** | AA | Ensure the low-vision / colour-blind persona can read UI text (menus, errors) without strain. | Contrast ratio must be **4.5:1**. Use Tailwind utility classes such as `text-gray-900 bg-white` (Normal) or `text-yellow-400 bg-gray-900` (High-contrast mode). *Mandatory to validate the primary palette with WebAIM.* |
| **1.4.6** | **Enhanced contrast** | AAA | Make sure vital components ("Report obstacle" and "Calculate route") have very high contrast. | Contrast ratio above **7:1**. E.g. `bg-blue-700` with bold white text. |
| **2.5.5** | **Target size** | AAA | Prevent severe miss-clicks for the wheelchair persona who may tremble or move over uneven ground. | Every interactive element (`<button>`, `<input>`, Leaflet markers) must be **at least 44×44 CSS pixels**. Tailwind: `min-h-[44px] min-w-[44px] p-4`. |
| **1.4.4** | **Text resize** | AA | Allow OS-level zoom (Android/iOS) up to 200% without breaking the layout. | Use Tailwind `rem` units (`text-base`, `text-lg`) instead of rigid px. The parent container must not use `overflow-hidden` without scroll, to avoid hiding turn-by-turn text when zoomed. |
| **3.3.2** | **Labels and instructions** | AA | Reduce cognitive load when entering coordinates. | The origin/destination `<input>` cannot rely on `placeholder` alone. Use `<label htmlFor="origin" className="sr-only">` for screen readers or a visible label for the senior persona. |
| **4.1.2** | **Name, role and value (ARIA)** | A | The spinner state and dynamic alerts must be readable by screen readers. | The loading spinner during the API call must have `role="status" aria-live="polite"`. The "Easy-Read mode" toggle needs `aria-expanded={isOpen}`. |
| **1.3.3** | **Sensory characteristics** | A | Do not rely solely on colour in the map UI (for the colour-blind persona). | When showing a "Blocked street" warning, the UI cannot be "red is bad" only. Tailwind must combine `flex items-center gap-2` joining colour with an explicit W3C icon (e.g. `LucideIcon` triangle). |
| **2.4.7** | **Focus visible** | AA | Keyboard / switch navigation must always show a visible focus ring. | Drop `outline: none` (anti-pattern). Require `focus:ring-2 focus:ring-blue-500 focus:outline-none` on every form and control. |

## Dev check-list
Before committing any screen / component (e.g. `ProfileSelector.jsx`), answer these 3 questions:
1. Does it have at least 44 px target size (Tailwind `h-11 w-11` or larger)?
2. Can I navigate the whole component via `[TAB]` and see a clear focus ring?
3. Does it pass a contrast check against the background (no light grey on white)?
