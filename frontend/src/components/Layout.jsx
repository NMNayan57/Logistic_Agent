import { Link, useLocation } from 'react-router-dom';
import { Truck, Bot, Settings, GitCompare, Layers, Home as HomeIcon } from 'lucide-react';

function Layout({ children }) {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: HomeIcon, label: 'Home' },
    { path: '/agent', icon: Bot, label: 'Copilot' },
    { path: '/direct', icon: Settings, label: 'Direct Solver' },
    { path: '/compare', icon: GitCompare, label: 'Compare' },
    { path: '/scenarios', icon: Layers, label: 'Scenarios' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition">
              <div className="bg-primary-500 p-2 rounded-lg">
                <Truck className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Logistics Copilot</h1>
                <p className="text-xs text-gray-500">AI-Powered Routing • Research Demo v0.1.0</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`
                      flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all
                      ${active
                        ? 'bg-primary-50 text-primary-600 border border-primary-200'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-2 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-green-700">API Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <nav className="md:hidden bg-white border-b border-gray-200 px-2 py-2 flex space-x-1 overflow-x-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-2 px-3 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-all
                ${active
                  ? 'bg-primary-50 text-primary-600 border border-primary-200'
                  : 'text-gray-600 hover:bg-gray-100'
                }
              `}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-gray-500">
              © 2025 Logistics Copilot Research Project
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-primary-600">
                API Docs
              </a>
              <span>•</span>
              <a href="https://github.com" className="hover:text-primary-600">
                GitHub
              </a>
              <span>•</span>
              <span>GPT-4 + OR-Tools</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
