import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReadingPane from '../components/reading/ReadingPane';
import FloatingControlPanel from '../components/panel/FloatingControlPanel';
import SoftNudge from '../components/nudge/SoftNudge';
import { Card } from '../components/common/Card';
import { useReadingStore } from '../stores/readingStore';

/**
 * ReadingPage — /reading
 * 6/22: 스토어 실시간 구독 — progress가 readingStore에서 읽힘
 * 6/23: ReadingPane이 실제 스크롤 이벤트로 progress를 갱신하고, ReadingPage의 진행률 바에 반영됨
 * TODO 6/24: focusStore.isNudgeVisible 기반 조건부 Nudge 렌더
 */
export default function ReadingPage() {
  const progress = useReadingStore((s) => s.progress);

  useEffect(() => {
    document.title = 'AI 리터러시 케어 — 읽기';
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      <div className="flex flex-col lg:flex-row gap-6 items-start">

        {/* ── 좌측: 본문 읽기 영역 ── */}
        <div className="flex-1 min-w-0 space-y-4">

          {/* 읽기 진행률 바 — readingStore 실시간 구독 */}
          <ReadingProgressBar progress={progress} />

          {/* 본문 패널 — 스크롤 이벤트로 progress 갱신 */}
          <ReadingPane />

          {/* Soft Nudge (TODO 6/24: focusStore 조건부 렌더) */}
          <SoftNudge message="이 단락에는 핵심 개념이 집중되어 있어요. 조금 더 천천히 읽어볼까요?" />

          {/* 안내 카드 */}
          <Card variant="flat" className="p-4">
            <p
              className="text-xs"
              style={{
                color: 'var(--color-text-muted)',
                fontFamily: 'var(--font-sans)',
                lineHeight: 'var(--leading-normal)',
              }}
            >
              <span className="font-semibold" style={{ color: 'var(--color-text-secondary)' }}>
                [6/22~23 M0 완성]
              </span>{' '}
              스크롤 진행률·집중도·XP가 실시간 업데이트됩니다.
              밑줄 용어에 마우스를 올려 툴팁을 확인하고,
              노란 하이라이트 단락은 케어 에이전트가 집중 권장 구간으로 마킹한 영역입니다.
            </p>
          </Card>
        </div>

        {/* ── 우측: 플로팅 제어판 ── */}
        <aside className="w-full lg:w-80 lg:shrink-0 lg:sticky lg:top-20 space-y-4">
          <FloatingControlPanel />
        </aside>

      </div>
    </div>
  );
}

/** 읽기 진행률 상단 바 — 스토어 값 직접 수신 */
function ReadingProgressBar({ progress }: { progress: number }) {
  // 예상 남은 시간 계산 (mock: 총 5분 기준)
  const remainingMin = Math.max(0, Math.round((5 * (100 - progress)) / 100));

  return (
    <div
      className="rounded-lg border p-3 flex items-center gap-4"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div className="flex items-center gap-2 shrink-0">
        <span className="text-sm" style={{ color: 'var(--color-text-secondary)', fontFamily: 'var(--font-sans)' }}>
          읽기 진행률
        </span>
        <span
          className="text-sm font-semibold tabular-nums"
          style={{ color: 'var(--color-primary)', fontFamily: 'var(--font-sans)' }}
        >
          {progress}%
        </span>
      </div>
      <div
        className="flex-1 rounded-full h-2 overflow-hidden"
        style={{ backgroundColor: 'var(--color-surface-alt)', border: '1px solid var(--color-border)' }}
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${progress}%`,
            background: `linear-gradient(90deg, var(--color-primary), var(--color-engagement))`,
            transition: 'width 0.5s ease',
          }}
        />
      </div>
      <span className="text-xs shrink-0" style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)' }}>
        {progress >= 100 ? '🎉 완독!' : `약 ${remainingMin}분 남음`}
      </span>
      {progress > 0 && (
        <Link
          to="/dashboard"
          className="shrink-0 text-xs px-2 py-1 rounded"
          style={{ backgroundColor: 'var(--color-primary-tint)', color: 'var(--color-primary)', fontFamily: 'var(--font-sans)' }}
        >
          📊 점수 보기
        </Link>
      )}
    </div>
  );
}
