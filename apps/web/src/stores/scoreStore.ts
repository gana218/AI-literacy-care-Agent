/**
 * scoreStore — Literacy Score & 게이미피케이션
 * 6/22: mock 초기값 연결 (리터러시 점수 87, XP 265, 레벨 2)
 * 6/26: ①번 Score Engine 결과 JSON 수신 후 업데이트
 */
import { create } from 'zustand';
import type { ScoreDataPoint, AcquiredBadge } from '../types/shared';
import { scoreSeries as mockScoreSeries } from '../mock/scoreSeries';

interface ScoreState {
  literacyScore: number;        // 0~100 최종 합산
  comprehensionScore: number;   // 이해도 (퀴즈 기반)
  engagementScore: number;      // 집중도 (행동 기반)
  xp: number;
  level: number;
  levelProgress: number;        // 0~100 (현재 레벨 내 진행률)
  scoreSeries: ScoreDataPoint[];
  badges: AcquiredBadge[];

  setLiteracyScore: (score: number, comprehension: number, engagement: number) => void;
  addXp: (amount: number) => void;
  setScoreSeries: (series: ScoreDataPoint[]) => void;
  addBadge: (badge: AcquiredBadge) => void;
  reset: () => void;
}

const LEVEL_THRESHOLDS = [0, 100, 250, 500, 1000, 2000]; // 레벨별 XP 기준

function calcLevel(xp: number): { level: number; progress: number } {
  let level = 1;
  for (let i = 1; i < LEVEL_THRESHOLDS.length; i++) {
    if (xp >= LEVEL_THRESHOLDS[i]) level = i + 1;
    else {
      const base = LEVEL_THRESHOLDS[i - 1];
      const next = LEVEL_THRESHOLDS[i];
      const progress = Math.floor(((xp - base) / (next - base)) * 100);
      return { level, progress };
    }
  }
  return { level, progress: 100 };
}

export const useScoreStore = create<ScoreState>((set) => ({
  // 6/22: mock 초기값
  literacyScore: 87,
  comprehensionScore: 82,
  engagementScore: 91,
  xp: 265,
  level: 2,
  levelProgress: 65,
  scoreSeries: mockScoreSeries.map((d) => ({
    label: d.day,
    before: d.beforeCare,
    after: d.afterCare,
  })),
  badges: [
    {
      id: 'first-read',
      name: '첫 완독',
      emoji: '📚',
      description: '첫 번째 글을 끝까지 읽었어요!',
      acquiredAt: new Date().toISOString(),
    },
    {
      id: 'focus-master',
      name: '초집중 리더',
      emoji: '⚡',
      description: '평균 집중도 90% 이상 달성!',
      acquiredAt: new Date().toISOString(),
    },
  ],

  setLiteracyScore: (literacyScore, comprehensionScore, engagementScore) =>
    set({ literacyScore, comprehensionScore, engagementScore }),

  addXp: (amount) =>
    set((s) => {
      const nextXp = s.xp + amount;
      const { level, progress } = calcLevel(nextXp);
      return { xp: nextXp, level, levelProgress: progress };
    }),

  setScoreSeries: (scoreSeries) => set({ scoreSeries }),

  addBadge: (badge) =>
    set((s) => ({ badges: [...s.badges, badge] })),

  reset: () =>
    set({
      literacyScore: 0, comprehensionScore: 0, engagementScore: 0,
      xp: 0, level: 1, levelProgress: 0, scoreSeries: [], badges: [],
    }),
}));
