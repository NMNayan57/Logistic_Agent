import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import AgentMode from './pages/AgentMode';
import DirectMode from './pages/DirectMode';
import CompareView from './pages/CompareView';
import ScenariosView from './pages/ScenariosView';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/agent" element={<AgentMode />} />
          <Route path="/direct" element={<DirectMode />} />
          <Route path="/compare" element={<CompareView />} />
          <Route path="/scenarios" element={<ScenariosView />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
