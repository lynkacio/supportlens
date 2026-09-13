'use client';

import Link from "next/link";
import { BarChart3, FileUp, Home, MessageSquareText } from "lucide-react";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/upload", label: "Upload tickets", icon: FileUp },
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/query", label: "Ask AI", icon: MessageSquareText },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-full shrink-0 flex-col border-b border-slate-200 bg-white lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r">
      <div className="flex items-center justify-between px-5 py-5 lg:block lg:px-6 lg:py-7">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex size-9 items-center justify-center rounded-xl bg-teal-700 text-sm font-bold text-white shadow-sm">
            SL
          </span>
          <span>
            <span className="block text-sm font-bold tracking-tight text-slate-950">
              SupportLens
            </span>
            <span className="block text-xs text-slate-500">Support intelligence</span>
          </span>
        </Link>
      </div>

      <nav aria-label="Primary navigation" className="flex gap-1 overflow-x-auto px-3 pb-3 lg:flex-col lg:px-3 lg:py-3">
        {navigation.map(({ href, label, icon: Icon }) => {
          const isActive = href === "/" ? pathname === href : pathname.startsWith(href);

          return (
            <Link
              key={href}
              href={href}
              className={`flex min-w-max items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-teal-50 text-teal-800"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
              }`}
            >
              <Icon size={17} strokeWidth={1.8} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto hidden border-t border-slate-100 px-6 py-5 lg:block">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Workspace</p>
        <p className="mt-2 text-sm text-slate-600">Customer support analytics</p>
      </div>
    </aside>
  );
}