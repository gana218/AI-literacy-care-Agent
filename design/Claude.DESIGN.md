# Claude Design Specifications

This specification serves as the primary standard for the design overhaul, focusing on readability and cognitive ease.

## Color System (Warm Paper Editorial)
- **Background (Paper)**: `#FBF9F6` (Very soft warm cream/beige)
- **Surface (Alt)**: `#FAF6F0` (Slightly deeper cream for containers/inputs)
- **Base Text (Charcoal)**: `#2A2421` (Soft warm charcoal, avoids high contrast stress)
- **Text Muted**: `#6E655F` (Gentle warm gray for metadata)
- **Primary (Terracotta)**: `#C85A32` (Terracotta highlight, used for primary actions)
- **Primary Tint**: `#F7ECE6` (Terracotta background accent, 8-10% opacity)
- **Border**: `#EAE3DB` (Soft warm divider color)

## Typography (Focus on Reading)
- **Body Font (Reading Content)**: `Georgia, "Noto Serif KR", "Batang", serif`
- **UI Font**: `Pretendard, -apple-system, sans-serif`
- **Metrics**:
  - Max text width: `680px`
  - Line height: `1.85`
  - Paragraph spacing: `1.5rem`
  - Letter spacing: `-0.01em`

## Interactive States
- Subdued animations, 200ms easing transitions.
- Light amber highlighter overlay for focused paragraphs: `background-color: rgba(217, 119, 6, 0.12)`.
