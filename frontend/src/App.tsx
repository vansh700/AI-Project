import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectPage } from './pages/ProjectPage';
import './index.css';

function AppContent() {
  const { isAuthenticated, logout } = useAuth();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>AI Code Analyst</h1>
        <button type="button" className="link-btn" onClick={logout}>Logout</button>
      </header>
      <main>
        {selectedProjectId ? (
          <ProjectPage projectId={selectedProjectId} onBack={() => setSelectedProjectId(null)} />
        ) : (
          <DashboardPage onSelectProject={setSelectedProjectId} />
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
