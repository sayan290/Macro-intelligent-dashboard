'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useDashboardStore } from '@/store/dashboard';
import {
  LayoutDashboard, TrendingUp, Globe, GitBranch, BarChart3,
  Calendar, Bot, Bell, FlaskConical, ChevronLeft, ChevronRight, Zap
} from 'lucide-react';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/markets', label: 'Markets', icon: TrendingUp },
  { href: '/macro', label: 'Macro', icon: Globe },
  { href: '/regime', label: 'Regime', icon: GitBranch },
  { href: '/correlation', label: 'Correlation', icon: BarChart3 },
  { href: '/calendar', label: 'Calendar', icon: Calendar },
  { href: '/ai', label: 'AI Assistant', icon: Bot },
  { href: '/alerts', label: 'Alerts', icon: Bell },
  { href: '/backtest', label: 'Backtest', icon: FlaskConical },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useDashboardStore();

  return (
    <aside className={`fixed left-0 top-0 h-screen bg-dark-900/95 backdrop-blur-xl border-r border-dark-600/50 z-30 transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-16'}`}>
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-dark-600/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          {sidebarOpen && (
            <div className="animate-fade-in">
              <h1 className="text-sm font-bold gradient-text">MACRO INTEL</h1>
              <p className="text-[10px] text-dark-300 tracking-widest">DASHBOARD</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              id={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group
                ${isActive
                  ? 'bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20'
                  : 'text-dark-300 hover:bg-dark-700/50 hover:text-dark-100'
                }`}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 transition-colors ${isActive ? 'text-accent-cyan' : 'text-dark-400 group-hover:text-dark-200'}`} />
              {sidebarOpen && <span className="animate-fade-in">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Toggle */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 w-6 h-6 bg-dark-700 border border-dark-500 rounded-full flex items-center justify-center text-dark-300 hover:text-white hover:bg-dark-600 transition-all z-40"
      >
        {sidebarOpen ? <ChevronLeft className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
      </button>
    </aside>
  );
}
