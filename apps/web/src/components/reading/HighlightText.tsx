/**
 * HighlightText — 6/23 실구현
 * 지정된 텍스트 범위에 --color-highlight 배경을 씌우는 인라인 컴포넌트.
 * ReadingPane에서 highlightedParagraphs 인덱스에 해당하는 단락에 적용.
 */
import React from 'react';

interface HighlightTextProps {
  children: React.ReactNode;
  /** 하이라이트 강도: normal(기본), strong(진하게) */
  intensity?: 'normal' | 'strong';
  /** 하이라이트 색 오버라이드 (없으면 --color-highlight 사용) */
  color?: string;
}

export const HighlightText: React.FC<HighlightTextProps> = ({
  children,
  intensity = 'normal',
  color,
}) => {
  const bgColor = color ?? 'var(--color-highlight)';
  const opacity = intensity === 'strong' ? 1 : 0.75;

  return (
    <mark
      style={{
        backgroundColor: bgColor,
        opacity,
        color: 'inherit',
        padding: '0 2px',
        borderRadius: '3px',
        boxDecorationBreak: 'clone',
        WebkitBoxDecorationBreak: 'clone',
        transition: 'background-color 0.3s ease',
      }}
    >
      {children}
    </mark>
  );
};

export default HighlightText;
