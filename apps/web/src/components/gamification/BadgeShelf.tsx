/**
 * BadgeShelf — 6/22 스토어 연결 실구현
 * scoreStore에서 배지 목록을 구독하여 획득/미획득 상태를 렌더링.
 */
import React from 'react';
import { useScoreStore } from '../../stores/scoreStore';

// 전체 배지 카탈로그 (획득 여부는 scoreStore.badges와 id로 비교)
const BADGE_CATALOG = [
  { id: 'first-read',    emoji: '📚', name: '첫 완독',    desc: '첫 번째 글을 끝까지 읽었어요!' },
  { id: 'focus-master',  emoji: '⚡', name: '초집중 리더', desc: '평균 집중도 90% 이상 달성!' },
  { id: 'vocab-master',  emoji: '🎯', name: '어휘 마스터', desc: '용어 툴팁을 10번 이상 확인했어요!' },
  { id: 'streak-3',      emoji: '🔥', name: '3일 연속',   desc: '3일 연속 읽기 세션 완료!' },
];

interface BadgeShelfProps {
  /** true이면 이름 숨기고 아이콘만 표시 (FloatingPanel 축약형) */
  compact?: boolean;
}

export const BadgeShelf: React.FC<BadgeShelfProps> = ({ compact = false }) => {
  const { badges } = useScoreStore();
  const acquiredIds = new Set(badges.map((b) => b.id));

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: compact ? '8px' : '12px' }}>
      {BADGE_CATALOG.map((badge) => {
        const acquired = acquiredIds.has(badge.id);
        return (
          <div
            key={badge.id}
            title={`${badge.name} (${acquired ? '획득' : '미획득'}) — ${badge.desc}`}
            style={{
              display: 'flex',
              flexDirection: compact ? 'row' : 'column',
              alignItems: 'center',
              gap: '4px',
              cursor: 'help',
              opacity: acquired ? 1 : 0.35,
              filter: acquired ? 'none' : 'grayscale(1)',
              transition: 'opacity 0.3s, filter 0.3s',
            }}
          >
            <div
              style={{
                width: compact ? '32px' : '44px',
                height: compact ? '32px' : '44px',
                borderRadius: '50%',
                border: `1px solid ${acquired ? 'var(--color-border)' : 'var(--color-border)'}`,
                backgroundColor: acquired ? 'var(--color-surface-alt)' : 'var(--color-surface-alt)',
                boxShadow: acquired ? 'var(--shadow-sm)' : 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: compact ? '16px' : '22px',
              }}
            >
              {badge.emoji}
            </div>
            {!compact && (
              <span
                style={{
                  fontSize: 'var(--text-xs)',
                  color: acquired ? 'var(--color-text-secondary)' : 'var(--color-text-muted)',
                  fontFamily: 'var(--font-sans)',
                  textAlign: 'center',
                  maxWidth: '52px',
                  lineHeight: '1.2',
                }}
              >
                {badge.name}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default BadgeShelf;
