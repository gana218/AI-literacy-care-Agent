# Airbnb Design Specifications

This specification serves as the layout and shape standard for card widgets, modal containers, and gamified interface components.

## Corner Radius & Spacings
- **Container Radius**: `16px` (Generous rounded corner for warm friendliness)
- **Button / Small Input Radius**: `10px`
- **Pill Radius**: `9999px`
- **Padding Inside Cards**: `20px` to `24px`

## Soft Shadow & Elevation
- **Elevation Base (Card)**: `0 4px 16px rgba(42, 36, 33, 0.05)` (Dispersed soft shadow avoiding sharp contrast borders)
- **Elevation Hover (Card Lift)**: `0 8px 24px rgba(42, 36, 33, 0.08)` with translateY `-2px`
- **Modal Overlay Backdrop**: `rgba(42, 36, 33, 0.45)` (Soft warm dimmed overlay)

## Interactive States (Subtle Micro-interactions)
- Buttons slightly scale down on tap: `transform: scale(0.98)`
- Hover transition: `all 0.2s cubic-bezier(0.4, 0, 0.2, 1)`
