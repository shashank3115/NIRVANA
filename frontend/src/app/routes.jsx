import { createBrowserRouter } from 'react-router-dom';
import { Root } from './pages/Root';
import { Home } from './pages/Home';
import { Results } from './pages/Results';
import { About } from './pages/About';
import { NotFound } from './pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      { index: true, element: <Home /> },
      { path: 'results', element: <Results /> },
      { path: 'about', element: <About /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]);
