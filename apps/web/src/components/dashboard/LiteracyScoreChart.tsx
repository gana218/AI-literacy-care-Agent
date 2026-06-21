/**
 * LiteracyScoreChart — 6/22 Recharts 실구현 (데모 핵심 ★)
 *
 * scoreStore의 scoreSeries를 구독해 케어 전/후 Literacy Score 비교 라인 그래프를 렌더링.
 * 심사위원에게 "이게 ChatGPT와 다른 이유"를 눈으로 보여주는 핵심 차트.
 *
 * TODO 6/26: ①번 Score Engine 실제 데이터 연결
 */
import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import { useScoreStore } from '../../stores/scoreStore';

// ── 커스텀 툴팁 ──────────────────────────────────────────────────────
interface TooltipProps {
  active?: boolean;
  payload?: Array<{ color: string; name: string; value: number }>;
  label?: string;
}

const CustomTooltip: React.FC<TooltipProps> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-md)',
        padding: '10px 14px',
        boxShadow: 'var(--shadow-md)',
        fontFamily: 'var(--font-sans)',
        fontSize: 'var(--text-sm)',
      }}
    >
      <p style={{ fontWeight: 'var(--weight-semibold)' as unknown as number, color: 'var(--color-text)', marginBottom: '6px' }}>
        {label}
      </p>
      {payload.map((item) => (
        <p key={item.name} style={{ color: item.color, margin: '2px 0' }}>
          {item.name}: <strong>{item.value}점</strong>
        </p>
      ))}
      {payload.length === 2 && (
        <p style={{ color: 'var(--color-growth)', marginTop: '6px', fontSize: 'var(--text-xs)' }}>
          +{payload[1].value - payload[0].value}점 향상 ↑
        </p>
      )}
    </div>
  );
};

// ── 메인 차트 ────────────────────────────────────────────────────────
export const LiteracyScoreChart: React.FC = () => {
  const { scoreSeries } = useScoreStore();

  return (
    <div>
      <div style={{ marginBottom: '12px' }}>
        <p
          style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-text-muted)',
            fontFamily: 'var(--font-sans)',
            marginTop: '4px',
          }}
        >
          AI 케어 에이전트 개입 전/후 Literacy Score 비교
        </p>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={scoreSeries} margin={{ top: 8, right: 16, left: -8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 12, fontFamily: 'var(--font-sans)', fill: 'var(--color-text-secondary)' }}
            axisLine={{ stroke: 'var(--color-border)' }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12, fontFamily: 'var(--font-sans)', fill: 'var(--color-text-secondary)' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontFamily: 'var(--font-sans)', fontSize: '12px', paddingTop: '12px' }}
          />

          {/* 케어 없이 예상 점수 (점선) */}
          <Line
            type="monotone"
            dataKey="before"
            name="케어 미적용"
            stroke="var(--color-text-muted)"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={{ fill: 'var(--color-text-muted)', r: 4 }}
            activeDot={{ r: 6 }}
          />

          {/* 케어 적용 후 실제 점수 (실선, 강조) */}
          <Line
            type="monotone"
            dataKey="after"
            name="케어 적용"
            stroke="var(--color-comprehension)"
            strokeWidth={3}
            dot={{ fill: 'var(--color-comprehension)', r: 5 }}
            activeDot={{ r: 7, stroke: 'var(--color-comprehension)', strokeWidth: 2 }}
          />

          {/* 기준선 — 평균 리터러시 점수 50점 */}
          <ReferenceLine
            y={50}
            stroke="var(--color-nudge-soft)"
            strokeDasharray="4 4"
            label={{ value: '평균', fill: 'var(--color-text-muted)', fontSize: 11, fontFamily: 'var(--font-sans)' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LiteracyScoreChart;
