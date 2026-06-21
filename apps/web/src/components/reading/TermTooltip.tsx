/**
 * TermTooltip — 6/23 실구현
 * 특정 용어에 마우스를 올리면 RAG 기반 풀이가 팝업으로 표시되는 인라인 컴포넌트.
 * 실제 정의는 ②번 Content Reducer (RAG) 가 제공. 현재는 props로 받음.
 *
 * TODO 6/30: ②번 RAG 결과를 api.ts를 통해 비동기로 로드
 */
import React, { useState, useRef, useEffect } from 'react';

interface TermTooltipProps {
  term: string;
  definition: string;
  /** 팝업이 열릴 방향 */
  placement?: 'top' | 'bottom';
  children?: React.ReactNode;
}

export const TermTooltip: React.FC<TermTooltipProps> = ({
  term,
  definition,
  placement = 'top',
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  // 외부 클릭 시 닫기
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [isOpen]);

  const tooltipBase: React.CSSProperties = {
    position: 'absolute',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '240px',
    backgroundColor: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    boxShadow: 'var(--shadow-md)',
    padding: '10px 12px',
    zIndex: 'var(--z-tooltip)' as unknown as number,
    pointerEvents: 'none',
    fontFamily: 'var(--font-sans)',
    fontSize: 'var(--text-sm)',
    lineHeight: 'var(--leading-normal)',
  };

  const tooltipStyle: React.CSSProperties =
    placement === 'top'
      ? { ...tooltipBase, bottom: 'calc(100% + 8px)' }
      : { ...tooltipBase, top: 'calc(100% + 8px)' };

  return (
    <span
      ref={ref}
      style={{ position: 'relative', display: 'inline' }}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
      onFocus={() => setIsOpen(true)}
      onBlur={() => setIsOpen(false)}
    >
      {/* 용어 텍스트 — 점선 밑줄로 툴팁 암시 */}
      <span
        style={{
          borderBottom: '1.5px dashed var(--color-primary)',
          color: 'var(--color-primary)',
          cursor: 'help',
          fontWeight: 'var(--weight-medium)' as unknown as number,
        }}
        tabIndex={0}
        aria-describedby={`tooltip-${term}`}
      >
        {children ?? term}
      </span>

      {/* 팝업 툴팁 */}
      {isOpen && (
        <span
          id={`tooltip-${term}`}
          role="tooltip"
          style={tooltipStyle}
        >
          <span
            style={{
              display: 'block',
              fontWeight: 'var(--weight-semibold)' as unknown as number,
              color: 'var(--color-text)',
              marginBottom: '4px',
            }}
          >
            {term}
          </span>
          <span style={{ color: 'var(--color-text-secondary)' }}>
            {definition}
          </span>
          <span
            style={{
              display: 'block',
              marginTop: '6px',
              fontSize: 'var(--text-xs)',
              color: 'var(--color-text-muted)',
            }}
          >
            {/* TODO 6/30: RAG 출처 표시 */}
            📖 AI 리터러시 케어 용어 사전
          </span>
        </span>
      )}
    </span>
  );
};

export default TermTooltip;
