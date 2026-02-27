import { Outlet, Link, useLocation } from 'react-router-dom';
import { Leaf, Menu, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Button } from '../components/ui/button';

export function Root() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [location.pathname]);

  const isActive = (path) => (path === '/' ? location.pathname === '/' : location.pathname.startsWith(path));

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-blue-50">
      <header className="sticky top-0 z-[1000] border-b border-emerald-100 bg-white/80 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="group flex items-center gap-2">
            <div className="rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 p-2 transition-transform group-hover:scale-110">
              <Leaf className="size-6 text-white" />
            </div>
            <div>
              <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-xl font-semibold text-transparent">EnerScope AI</span>
              <p className="-mt-1 text-xs text-gray-500">Renewable Intelligence</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            <Link to="/"><Button variant={isActive('/') ? 'default' : 'ghost'} className={isActive('/') ? 'bg-emerald-600 hover:bg-emerald-700' : ''}>Home</Button></Link>
            <Link to="/results"><Button variant={isActive('/results') ? 'default' : 'ghost'} className={isActive('/results') ? 'bg-emerald-600 hover:bg-emerald-700' : ''}>Results</Button></Link>
            <Link to="/about"><Button variant={isActive('/about') ? 'default' : 'ghost'} className={isActive('/about') ? 'bg-emerald-600 hover:bg-emerald-700' : ''}>About</Button></Link>
          </nav>

          <button className="rounded-lg p-2 hover:bg-emerald-50 md:hidden" onClick={() => setMobileMenuOpen((v) => !v)}>
            {mobileMenuOpen ? <X className="size-6 text-gray-600" /> : <Menu className="size-6 text-gray-600" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <nav className="md:hidden py-4 space-y-2">
            <Link to="/" onClick={() => setMobileMenuOpen(false)}><Button variant={isActive('/') ? 'default' : 'ghost'} className={`w-full justify-start ${isActive('/') ? 'bg-emerald-600 hover:bg-emerald-700' : ''}`}>Home</Button></Link>
            <Link to="/results" onClick={() => setMobileMenuOpen(false)}><Button variant={isActive('/results') ? 'default' : 'ghost'} className={`w-full justify-start ${isActive('/results') ? 'bg-emerald-600 hover:bg-emerald-700' : ''}`}>Results</Button></Link>
            <Link to="/about" onClick={() => setMobileMenuOpen(false)}><Button variant={isActive('/about') ? 'default' : 'ghost'} className={`w-full justify-start ${isActive('/about') ? 'bg-emerald-600 hover:bg-emerald-700' : ''}`}>About</Button></Link>
          </nav>
        )}
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="bg-white/50 border-t border-emerald-100 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Leaf className="size-5 text-emerald-600" />
              <span className="text-sm text-gray-600">© 2026 EnerScope AI. Powering sustainable futures.</span>
            </div>
            <div className="text-sm text-gray-500">Version 1.0 | Built for a greener tomorrow</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
