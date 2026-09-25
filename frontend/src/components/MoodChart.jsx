import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

export default function MoodChart({ data }) {
  const chartData = data.map((d) => ({
    date: d.entry_date,
    score: d.mood_score,
  }));

  if (chartData.length === 0) {
    return <div className="text-soft">No mood data yet — log your first mood to see trends here.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--neu-border)" />
        <XAxis dataKey="date" tick={{ fontSize: 12, fill: "var(--neu-text-soft)" }} />
        <YAxis domain={[1, 5]} tick={{ fontSize: 12, fill: "var(--neu-text-soft)" }} />
        <Tooltip 
          contentStyle={{ 
            background: "var(--neu-surface)", 
            border: "none", 
            borderRadius: "var(--radius-sm)", 
            boxShadow: "var(--neu-shadow-raised)",
            color: "var(--neu-text)"
          }} 
        />
        <Line
          type="monotone"
          dataKey="score"
          stroke="var(--neu-primary)"
          strokeWidth={3}
          dot={{ r: 5, fill: "var(--neu-primary-dark)", strokeWidth: 2, stroke: "var(--neu-surface)" }}
          activeDot={{ r: 7, fill: "var(--neu-primary-dark)", strokeWidth: 2, stroke: "var(--neu-surface)" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
