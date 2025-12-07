import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import CreateAnalysisForm from './components/CreateAnalysisForm';
import AnalysisResults from './components/AnalysisResults';
import ReasoningPath from './components/ReasoningPath';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-[#E5E7EB] overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateAnalysisForm />} />
            <Route path="/analysis/:id" element={<AnalysisResults />} />
            <Route path="/reasoning/:id" element={<ReasoningPath />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App
