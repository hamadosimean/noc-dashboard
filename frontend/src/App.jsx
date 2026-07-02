import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/layout/Header';
import TabNav from './components/layout/TabNav';
import GlobalView from './pages/GlobalView';
import LocalityView from './pages/LocalityView';
import SLAView from './pages/SLAView';
import InteropView from './pages/InteropView';
import DataModelView from './pages/DataModelView';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />
        <TabNav />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/global" replace />} />
            <Route path="/global" element={<GlobalView />} />
            <Route path="/locality" element={<LocalityView />} />
            <Route path="/sla" element={<SLAView />} />
            <Route path="/interop" element={<InteropView />} />
            <Route path="/datamodel" element={<DataModelView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
