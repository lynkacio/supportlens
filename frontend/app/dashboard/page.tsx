// frontend/app/dashboard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  ArrowUpRight,
  BarChart3,
  CalendarRange,
  CircleDashed,
  Inbox,
  Sparkles,
} from 'lucide-react';
import PageContainer from "@/components/PageContainer";

type Stats = {
  total: number;
  unanalyzed: number;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
};

const statusPillStyles = {
  neutral: 'border-slate-200 bg-slate-100 text-slate-700',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  warning: 'border-amber-200 bg-amber-50 text-amber-700',
  info: 'border-sky-200 bg-sky-50 text-sky-700',
};

const categoryLabelMap: Record<string, string> = {
  billing: 'Billing',
  technical: 'Technical',
  account: 'Account',
  feature_request: 'Feature Request',
  other: 'Other',
};

const priorityLabelMap: Record<string, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent',
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/tickets/stats")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: Stats) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <PageContainer>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">
            Dashboard
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
            Ticket Dashboard
          </h1>
          <p className="mt-4 text-sm text-slate-500">Loading analytics...</p>
        </div>
      </PageContainer>
    );
  }

  if (!stats || error) {
    return (
      <PageContainer>
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-red-500">
            Dashboard
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
            Ticket Dashboard
          </h1>
          <p className="mt-4 text-sm text-red-600">
            {error ? `Loading failed: ${error}` : "No analytics data available"}
          </p>
        </div>
      </PageContainer>
    );
  }

  const categoryData = Object.entries(stats.by_category).map(([name, value]) => ({
    name: categoryLabelMap[name] ?? name,
    value,
  }));
  const priorityData = Object.entries(stats.by_priority).map(([name, value]) => ({
    name: priorityLabelMap[name] ?? name,
    value,
  }));

  const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"];

  const analyzed = stats.total - stats.unanalyzed;
  const completionRate = stats.total
    ? Math.round((analyzed / stats.total) * 100)
    : 0;

  return (
    <PageContainer>
      <div className="space-y-6">
        <header className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">
              Overview
            </p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
              Ticket Dashboard
            </h1>
          </div>

          <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium ${statusPillStyles.success}`}>
            <Sparkles size={14} />
            Live analytics
          </div>
        </header>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">Total Tickets</span>
              <div className="rounded-lg bg-slate-100 p-2 text-slate-700">
                <Inbox size={16} />
              </div>
            </div>
            <p className="mt-5 text-3xl font-bold tracking-tight text-slate-900">{stats.total}</p>
            <div className={`mt-4 inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${statusPillStyles.neutral}`}>
              <ArrowUpRight size={12} />
              Overall volume
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">Analyzed</span>
              <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
                <BarChart3 size={16} />
              </div>
            </div>
            <p className="mt-5 text-3xl font-bold tracking-tight text-slate-900">{analyzed}</p>
            <div className={`mt-4 inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${statusPillStyles.success}`}>
              Processed tickets
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">Unanalyzed</span>
              <div className="rounded-lg bg-amber-50 p-2 text-amber-600">
                <CircleDashed size={16} />
              </div>
            </div>
            <p className="mt-5 text-3xl font-bold tracking-tight text-slate-900">{stats.unanalyzed}</p>
            <div className={`mt-4 inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${statusPillStyles.warning}`}>
              Pending review
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">Completion</span>
              <div className="rounded-lg bg-sky-50 p-2 text-sky-600">
                <CalendarRange size={16} />
              </div>
            </div>
            <p className="mt-5 text-3xl font-bold tracking-tight text-slate-900">{completionRate}%</p>
            <div className={`mt-4 inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${statusPillStyles.info}`}>
              Rate today
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Ticket Categories</h3>
              <span className="rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                Breakout
              </span>
            </div>

            {categoryData.length === 0 ? (
              <p className="text-sm text-slate-400">No analyzed tickets available</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={92}
                    innerRadius={40}
                    paddingAngle={3}
                  >
                    {categoryData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      borderRadius: '12px',
                      border: '1px solid #e2e8f0',
                      backgroundColor: '#ffffff',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Priority Distribution</h3>
              <span className="rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                Severity
              </span>
            </div>

            {priorityData.length === 0 ? (
              <p className="text-sm text-slate-400">No analyzed tickets available</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={priorityData} barGap={8}>
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 12 }}
                  />
                  <YAxis
                    allowDecimals={false}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 12 }}
                  />
                  <Tooltip
                    cursor={{ fill: '#f8fafc' }}
                    contentStyle={{
                      borderRadius: '12px',
                      border: '1px solid #e2e8f0',
                      backgroundColor: '#ffffff',
                    }}
                  />
                  <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}