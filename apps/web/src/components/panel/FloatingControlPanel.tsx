/**
 * FloatingControlPanel — 6/22 스토어 실시간 구독
 *
 * [구현된 기능]
 * - focusStore 구독 → 집중도 점수 게이지 실시간 반영
 * - readingStore 구독 → 진행률 실시간 반영
 * - scoreStore 구독 → XP·레벨 표시
 * - 집중도에 따라 게이지 색상 변화
 *
 * TODO 6/24: nudgeLevel 변화 → Nudge 컴포넌트 트리거
 * TODO 7/1: 퀴즈 정답 이후 XP 애니메이션 (Framer Motion)
 */
import React from 'react';
import { useFocusStore } from '../../stores/focusStore';
import { useReadingStore } from '../../stores/readingStore';
import { useScoreStore } from '../../stores/scoreStore';
import LevelBar from '../gamification/LevelBar';
import XpCounter from '../gamification/XpCounter';
import BadgeShelf from '../gamification/BadgeShelf';

// 집중도 수치에 따른 색상 매핑
function getFocusColor(score: number): string {
  if (score >= 80) return 'var(--color-engagement)';
  if (score >= 60) return 'var(--color-comprehension)';
  if (score >= 40) return 'var(--color-xp)';
  return 'var(--color-nudge-hard)';
}

function getFocusLabel(score: number): string {
  if (score >= 80) return '매우 집중';
  if (score >= 60) return '보통 집중';
  if (score >= 40) return '집중 저하';
  return '주의 필요';
}

export const FloatingControlPanel: React.FC = () => {
  const { focusScore } = useFocusStore();
  const { progress } = useReadingStore();
  const { literacyScore, xp, level, levelProgress } = useScoreStore();

  const focusColor = getFocusColor(focusScore);
  const focusLabel = getFocusLabel(focusScore);

  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-md)',
        overflow: 'hidden',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* 패널 헤더 */}
      <div
        style={{
          padding: 'var(--space-4) var(--space-5)',
          borderBottom: '1px solid var(--color-border)',
          background: `linear-gradient(135deg, var(--color-primary-tint), var(--color-surface))`,
        }}
      >
        <p style={{ fontSize: 'var(--text-xs)', fontWeight: 'var(--weight-semibold)' as unknown as number, color: 'var(--color-primary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          실시간 케어 제어판
        </p>
      </div>

      <div style={{ padding: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>

        {/* ── 집중도 ── */}
        <section>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>⚡ 집중도</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{focusLabel}</span>
              <span style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--weight-bold)' as unknown as number, color: focusColor, fontVariantNumeric: 'tabular-nums' }}>
                {focusScore}
              </span>
            </div>
          </div>
          <GaugeBar value={focusScore} color={focusColor} />
        </section>

        {/* ── 읽기 진행률 ── */}
        <section>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>📖 진행률</span>
            <span style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--weight-bold)' as unknown as number, color: 'var(--color-primary)', fontVariantNumeric: 'tabular-nums' }}>
              {progress}%
            </span>
          </div>
          <GaugeBar value={progress} color="var(--color-primary)" />
        </section>

        {/* 구분선 */}
        <hr style={{ borderColor: 'var(--color-border)', margin: '0' }} />

        {/* ── Literacy Score ── */}
        <section>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-1)' }}>🎯 리터러시 점수</p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-1)' }}>
            <span style={{ fontSize: '2rem', fontWeight: 'var(--weight-bold)' as unknown as number, color: 'var(--color-primary)', fontVariantNumeric: 'tabular-nums' }}>
              {literacyScore}
            </span>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>/ 100</span>
          </div>
        </section>

        {/* ── 레벨 & XP ── */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <LevelBar level={level} percentage={levelProgress} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>누적 경험치</span>
            <XpCounter xp={xp} />
          </div>
        </section>

        {/* ── 배지 ── */}
        <section>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>🎖️ 최근 획득 배지</p>
          <BadgeShelf compact />
        </section>

      </div>
    </div>
  );
};

/** 공통 게이지 바 */
function GaugeBar({ value, color }: { value: number; color: string }) {
  return (
    <div
      style={{
        height: '8px',
        borderRadius: 'var(--radius-full)',
        backgroundColor: 'var(--color-surface-alt)',
        border: '1px solid var(--color-border)',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          height: '100%',
          width: `${Math.min(100, value)}%`,
          borderRadius: 'var(--radius-full)',
          background: color,
          transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      />
    </div>
  );
}

export default FloatingControlPanel;
