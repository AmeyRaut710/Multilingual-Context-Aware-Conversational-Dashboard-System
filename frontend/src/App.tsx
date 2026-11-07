import React, { useState, useEffect } from 'react';
import { WelcomePage } from './pages/WelcomePage';
import { DashboardWorkspace } from './pages/DashboardWorkspace';
import { DashboardState } from './types/dashboard';

export const App: React.FC = () => {
  const [activeState, setActiveState] = useState<DashboardState | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('theme') === 'dark' ||
      (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  const handleProjectLoaded = (sessionId: string, state: DashboardState) => {
    setActiveState(state);
  };

  const handleBackToWelcome = () => {
    setActiveState(null);
  };

  return (
    <div className="min-h-screen">
      {!activeState ? (
        <WelcomePage
          onProjectLoaded={handleProjectLoaded}
          darkMode={darkMode}
        />
      ) : (
        <DashboardWorkspace
          initialState={activeState}
          darkMode={darkMode}
          onToggleTheme={toggleTheme}
          onBackToWelcome={handleBackToWelcome}
        />
      )}
    </div>
  );
};

export default App;
