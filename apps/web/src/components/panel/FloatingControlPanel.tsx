import React, { useState, useEffect, useRef } from 'react';
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

        {/* ── 데모 시뮬레이터 ── */}
        <section style={{ borderTop: '1px dashed var(--color-border)', paddingTop: 'var(--space-4)' }}>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)', fontFamily: 'var(--font-sans)' }}>
            🎮 집중도 시뮬 (데모용)
          </p>
          <FocusSimulator />
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

/**
 * FocusSimulator — 데모·심사 시연용 집중도 직접 조작 및 자동 E2E 시연기
 */
function FocusSimulator() {
  const { setFocusScore, dismissNudge, dismissQuiz, isQuizVisible } = useFocusStore();
  const { setProgress } = useReadingStore();
  const { restartDemoSession, quizResults, recordQuizResult, addXp } = useScoreStore();

  const [demoStep, setDemoStep] = useState<number | null>(null);
  const [demoStatus, setDemoStatus] = useState<string>('');
  const timeoutIds = useRef<number[]>([]);

  const clearAllTimeouts = () => {
    timeoutIds.current.forEach((id) => window.clearTimeout(id));
    timeoutIds.current = [];
  };

  useEffect(() => {
    return () => clearAllTimeouts();
  }, []);

  // 퀴즈 결과가 추가되면 데모 Step 4에서 자동으로 Step 5로 이동
  useEffect(() => {
    if (demoStep === 4 && quizResults.length > 0) {
      proceedToStep5();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [quizResults.length, demoStep]);

  const resetAll = () => {
    clearAllTimeouts();
    setDemoStep(null);
    setDemoStatus('');
    setProgress(0);
    setFocusScore(85);
    dismissNudge();
    dismissQuiz();
    restartDemoSession();
  };

  const proceedToStep5 = () => {
    clearAllTimeouts();
    setDemoStep(5);
    setDemoStatus('✨ 퀴즈 정답! 집중도 회복 및 90% 돌파');
    setFocusScore(85);
    dismissNudge();
    dismissQuiz();
    setProgress(90);

    const t1 = window.setTimeout(() => {
      setDemoStep(6);
      setDemoStatus('🎉 완독 완료! 최종 결과 분석');
      setProgress(100);
      setDemoStep(null);
    }, 3000);
    timeoutIds.current.push(t1);
  };

  const handleAutoAnswer = () => {
    recordQuizResult({
      quizId: 'mock-q1',
      correct: true,
      xpAwarded: 30,
      timestamp: Date.now(),
    });
    addXp(30);
  };

  const startAutoDemo = () => {
    resetAll();
    setDemoStep(0);
    setDemoStatus('📖 E2E 데모 시작: 독서 중... (집중도 85)');

    const t1 = window.setTimeout(() => {
      setDemoStep(1);
      setDemoStatus('📊 25% 지점 통과 (점수 기록)');
      setProgress(25);
    }, 2500);

    const t2 = window.setTimeout(() => {
      setDemoStep(2);
      setDemoStatus('⚠️ 집중력 저하 감지 → Soft Nudge 작동');
      setProgress(35);
      setFocusScore(65);
    }, 5500);

    const t3 = window.setTimeout(() => {
      setDemoStep(3);
      setDemoStatus('⚠️ 추가 저하 → Medium Nudge (요약 힌트)');
      setProgress(50);
      setFocusScore(45);
    }, 9000);

    const t4 = window.setTimeout(() => {
      setDemoStep(4);
      setDemoStatus('🚨 주의 필요 → Hard Nudge + 퀴즈 팝업');
      setProgress(75);
      setFocusScore(25);
    }, 13000);

    timeoutIds.current.push(t1, t2, t3, t4);
  };

  const steps = [
    { label: '집중 (85)', score: 85, color: 'var(--color-engagement)' },
    { label: 'Soft (65)', score: 65, color: 'var(--color-nudge-soft)' },
    { label: 'Medium (45)', score: 45, color: 'var(--color-nudge-medium)' },
    { label: 'Hard (25)', score: 25, color: 'var(--color-nudge-hard)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {/* 수동 집중도 조작 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        {steps.map(({ label, score, color }) => (
          <button
            key={label}
            onClick={() => {
              clearAllTimeouts();
              setDemoStep(null);
              setDemoStatus('');
              setFocusScore(score);
            }}
            style={{
              padding: '6px 4px',
              fontSize: '10px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 600,
              borderRadius: 'var(--radius-md)',
              border: `1px solid ${color}`,
              backgroundColor: 'var(--color-surface)',
              color,
              cursor: 'pointer',
              transition: 'background-color 0.2s',
              textAlign: 'center',
            }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-surface-alt)')}
            onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-surface)')}
          >
            {label}
          </button>
        ))}
      </div>

      {/* 데모 제어 및 자동 데모 버튼 */}
      <div style={{ display: 'flex', gap: '6px' }}>
        {demoStep === null ? (
          <button
            onClick={startAutoDemo}
            style={{
              flex: 1,
              padding: '8px',
              fontSize: '11px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 700,
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-primary)',
              color: '#fff',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
            }}
          >
            🤖 자동 E2E 데모 시작
          </button>
        ) : (
          <button
            onClick={resetAll}
            style={{
              flex: 1,
              padding: '8px',
              fontSize: '11px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 700,
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-nudge-hard)',
              color: '#fff',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            ⏹️ 데모 중지 / 리셋
          </button>
        )}

        <button
          onClick={resetAll}
          style={{
            padding: '8px 10px',
            fontSize: '11px',
            fontFamily: 'var(--font-sans)',
            fontWeight: 600,
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-surface)',
            color: 'var(--color-text-secondary)',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-surface-alt)')}
          onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.backgroundColor = 'var(--color-surface)')}
        >
          🔄 리셋
        </button>
      </div>

      {/* 데모 진행 정보 */}
      {demoStep !== null && (
        <div
          style={{
            padding: '8px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-primary-tint)',
            border: '1px solid var(--color-border)',
            fontFamily: 'var(--font-sans)',
          }}
        >
          <p style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-primary)', marginBottom: '2px' }}>
            [E2E 시연 시나리오 진행 중]
          </p>
          <p style={{ fontSize: '11px', color: 'var(--color-text)', lineHeight: '1.4' }}>
            {demoStatus}
          </p>
          {demoStep === 4 && isQuizVisible && (
            <div style={{ marginTop: '6px', display: 'flex', gap: '4px' }}>
              <button
                onClick={handleAutoAnswer}
                style={{
                  flex: 1,
                  padding: '4px',
                  fontSize: '9px',
                  fontFamily: 'var(--font-sans)',
                  fontWeight: 700,
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-comprehension)',
                  color: '#fff',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                💡 자동 정답 제출 후 계속
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
