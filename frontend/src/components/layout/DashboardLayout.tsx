'use client';
import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { useDashboardStore } from '@/store/dashboard';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useDashboardStore();

  return (
    <div className="flex h-screen overflow-hidden bg-dark-950">
      <Sidebar />
      <div className={`flex flex-col flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <Header />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
}
