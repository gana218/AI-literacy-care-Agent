/**
 * XpCounter — 6/22 실구현
 * 경험치 수치를 스타일링하여 표시. 미래: 숫자가 올라가는 애니메이션 (Framer Motion, 7/1).
 */
import React from 'react';

interface XpCounterProps {
  xp: number;
}

export const XpCounter: React.FC<XpCounterProps> = ({ xp }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
      <span style={{ fontSize: '16px' }}>✨</span>
      <span
        style={{
          fontSize: 'var(--text-base)',
          fontWeight: 'var(--weight-bold)' as unknown as number,
          color: 'var(--color-xp)',
          fontFamily: 'var(--font-sans)',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {xp.toLocaleString()}
      </span>
      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)' }}>
        XP
      </span>
    </div>
  );
};

export default XpCounter;
