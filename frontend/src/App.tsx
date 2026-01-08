import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { AgentConfigPage } from './pages/AgentConfigPage'
import { TriggerCallPage } from './pages/TriggerCallPage'
import { CallHistoryPage } from './pages/CallHistoryPage'
import { CallDetailsPage } from './pages/CallDetailsPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/agents" element={<AgentConfigPage />} />
        <Route path="/trigger-call" element={<TriggerCallPage />} />
        <Route path="/calls" element={<CallHistoryPage />} />
        <Route path="/calls/:id" element={<CallDetailsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
