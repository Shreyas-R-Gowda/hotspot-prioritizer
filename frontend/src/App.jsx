import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import MapView from './components/MapView';
import ReportForm from './components/ReportForm';
import HotspotList from './components/HotspotList';
import Login from './components/Login';
import CursorHighlighter from './components/CursorHighlighter';
import ReportDetail from './components/ReportDetail';

import AdminDashboard from './components/AdminDashboard';
import CitizenDashboard from './components/CitizenDashboard';
import ProtectedRoute from './components/ProtectedRoute';

import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <CursorHighlighter />
        <div className="flex flex-col h-screen">
          <Navbar />
          <div className="flex-grow pt-16">
            <Routes>
              <Route path="/" element={<MapView />} />
              <Route path="/report/new" element={<ReportForm />} />
              <Route path="/reports/:id" element={<ReportDetail />} />
              <Route path="/hotspots" element={<HotspotList />} />
              <Route path="/auth/login" element={<Login />} />

              {/* Protected Admin Routes */}
              <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
              </Route>

              {/* Citizen Routes */}
              <Route path="/citizen/dashboard" element={<CitizenDashboard />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
