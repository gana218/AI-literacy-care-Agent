/**
 * focusStore — 집중도 & 넛지 상태
 * 6/22: mock 초기값 연결, nudgeLevel 추가
 * 6/24: ③서버 WebSocket 이벤트 → setFocusScore, setNudgeLevel 호출
 */
import { create } from 'zustand';

export type NudgeLevel = 'none' | 'soft' | 'medium' | 'hard';

interface FocusState {
  focusScore: number;           // 0~100
  nudgeLevel: NudgeLevel;
  isNudgeVisible: boolean;
  isQuizVisible: boolean;

  setFocusScore: (score: number) => void;
  setNudgeLevel: (level: NudgeLevel) => void;
  showNudge: (level: NudgeLevel) => void;
  dismissNudge: () => void;
  showQuiz: () => void;
  dismissQuiz: () => void;
  reset: () => void;
}

export const useFocusStore = create<FocusState>((set) => ({
  // 6/22: mock 초기값 — 집중도 85%, nudge 없음
  focusScore: 85,
  nudgeLevel: 'none',
  isNudgeVisible: false,
  isQuizVisible: false,

  setFocusScore: (focusScore) => set({ focusScore }),
  setNudgeLevel: (nudgeLevel) => set({ nudgeLevel }),
  showNudge: (level) => set({ nudgeLevel: level, isNudgeVisible: true }),
  dismissNudge: () => set({ isNudgeVisible: false, nudgeLevel: 'none' }),
  showQuiz: () => set({ isQuizVisible: true }),
  dismissQuiz: () => set({ isQuizVisible: false }),
  reset: () =>
    set({ focusScore: 100, nudgeLevel: 'none', isNudgeVisible: false, isQuizVisible: false }),
}));
