import { useNavigate } from 'react-router-dom';
import { Home, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
      <Card className="max-w-md w-full border-amber-200">
        <CardContent className="p-8 text-center">
          <div className="bg-gradient-to-br from-amber-500 to-orange-600 size-16 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="size-8 text-white" />
          </div>
          <h1 className="mb-2 text-3xl font-bold text-gray-900">404 - Page Not Found</h1>
          <p className="mb-6 text-gray-600">The page you're looking for doesn't exist or has been moved.</p>
          <Button onClick={() => navigate('/')} className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700">
            <Home className="size-4 mr-2" />
            Back to Home
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
