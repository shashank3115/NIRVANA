import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Search, Zap, TrendingUp, Leaf as LeafIcon, Navigation } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent } from '../components/ui/card';
import { LocationMap } from '../components/LocationMap';

export function Home() {
  const navigate = useNavigate();
  const [address, setAddress] = useState('');
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [confirmedAddress, setConfirmedAddress] = useState('');
  const [locationError, setLocationError] = useState('');
  const [isResolvingLocation, setIsResolvingLocation] = useState(false);

  const reverseGeocode = async (lat, lng) => {
    const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
    const response = await fetch(url, {
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Could not resolve selected coordinates');
    }

    const data = await response.json();
    return data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  };

  const geocodeAddress = async () => {
    if (!address.trim()) {
      setLocationError('Enter a location before searching.');
      return;
    }

    setLocationError('');
    setIsResolvingLocation(true);

    try {
      const query = encodeURIComponent(address.trim());
      const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&q=${query}&limit=1`, {
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Location search failed');
      }

      const data = await response.json();
      if (!data.length) {
        throw new Error('No matching location found');
      }

      const bestMatch = data[0];
      const coords = [Number(bestMatch.lat), Number(bestMatch.lon)];
      setSelectedLocation(coords);
      setConfirmedAddress(bestMatch.display_name);
      setAddress(bestMatch.display_name);
    } catch (error) {
      setConfirmedAddress('');
      setLocationError(error.message || 'Unable to resolve this address.');
    } finally {
      setIsResolvingLocation(false);
    }
  };

  const handleMapLocationSelect = async (coords) => {
    setSelectedLocation(coords);
    setLocationError('');
    setIsResolvingLocation(true);

    try {
      const [lat, lng] = coords;
      const resolvedAddress = await reverseGeocode(lat, lng);
      setConfirmedAddress(resolvedAddress);
      setAddress(resolvedAddress);
    } catch {
      setConfirmedAddress('');
      setLocationError('Unable to confirm this pin. Try another point or search again.');
    } finally {
      setIsResolvingLocation(false);
    }
  };

  const handleAnalyze = () => {
    if (selectedLocation && confirmedAddress) {
      localStorage.setItem(
        'enerscope_location',
        JSON.stringify({
          address: confirmedAddress,
          coordinates: selectedLocation,
        }),
      );
      navigate('/results');
      return;
    }

    setLocationError('Select an exact point on the map or search and confirm a real location first.');
  };

  const handleKeyPress = async (e) => {
    if (e.key === 'Enter') {
      await geocodeAddress();
    }
  };

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      setLocationError('');
      setIsResolvingLocation(true);
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const coords = [position.coords.latitude, position.coords.longitude];
          setSelectedLocation(coords);

          try {
            const resolvedAddress = await reverseGeocode(coords[0], coords[1]);
            setConfirmedAddress(resolvedAddress);
            setAddress(resolvedAddress);
          } catch {
            setConfirmedAddress('');
            setLocationError('Current location found, but address could not be verified.');
          } finally {
            setIsResolvingLocation(false);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
          setLocationError('Unable to access your location. Please allow location permission.');
          setIsResolvingLocation(false);
        },
      );
      return;
    }

    setLocationError('Geolocation is not supported in this browser.');
  };

  return (
    <div className="min-h-[calc(100vh-8rem)]">
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/10 via-teal-500/5 to-blue-600/10" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 rounded-full mb-6">
              <Zap className="size-4 text-emerald-600" />
              <span className="text-sm font-medium text-emerald-700">
                AI-Powered Renewable Energy Platform
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Discover Your Perfect
              <br />
              <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                Renewable Energy Solution
              </span>
            </h1>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
              EnerScope AI analyzes satellite data, climate patterns, and geographic features to
              recommend the most suitable small-scale renewable energy source for any location.
            </p>
          </div>

          <Card className="max-w-4xl mx-auto shadow-xl border-emerald-100">
            <CardContent className="p-6 md:p-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Enter Your Location
                  </label>
                  <div className="flex gap-3">
                    <div className="flex-1 relative">
                      <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                      <Input
                        type="text"
                        placeholder="Enter address or coordinates..."
                        value={address}
                        onChange={(e) => {
                          setAddress(e.target.value);
                          setConfirmedAddress('');
                          setLocationError('');
                        }}
                        onKeyPress={handleKeyPress}
                        className="pl-10 h-12"
                      />
                    </div>
                    <Button
                      variant="outline"
                      onClick={geocodeAddress}
                      disabled={isResolvingLocation || !address.trim()}
                      className="h-12 px-4 border-emerald-200 hover:bg-emerald-50"
                    >
                      <Search className="size-5" />
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleUseCurrentLocation}
                      disabled={isResolvingLocation}
                      className="h-12 px-4 border-emerald-200 hover:bg-emerald-50"
                    >
                      <Navigation className="size-5" />
                    </Button>
                  </div>
                  {locationError && <p className="mt-2 text-sm text-red-600">{locationError}</p>}
                  {!locationError && isResolvingLocation && (
                    <p className="mt-2 text-sm text-gray-500">Confirming location details...</p>
                  )}
                  {!locationError && !isResolvingLocation && confirmedAddress && (
                    <p className="mt-2 text-sm text-emerald-700">Confirmed location: {confirmedAddress}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Or Select on Map
                  </label>
                  <div className="rounded-lg overflow-hidden border-2 border-emerald-100">
                    <LocationMap selectedLocation={selectedLocation} onLocationSelect={handleMapLocationSelect} />
                  </div>
                  {selectedLocation && (
                    <p className="mt-2 text-xs text-gray-600">
                      Selected coordinates: {selectedLocation[0].toFixed(6)}, {selectedLocation[1].toFixed(6)}
                    </p>
                  )}
                </div>

                <Button
                  size="lg"
                  onClick={handleAnalyze}
                  disabled={!selectedLocation || !confirmedAddress || isResolvingLocation}
                  className="w-full h-12 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
                >
                  <Search className="size-5 mr-2" />
                  Analyze Location
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-16">
            <Card className="border-emerald-100 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="size-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center mb-4">
                  <MapPin className="size-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Satellite Analysis</h3>
                <p className="text-sm text-gray-600">
                  Leverages Sentinel-2 imagery and NASA POWER data for accurate environmental
                  assessment.
                </p>
              </CardContent>
            </Card>

            <Card className="border-emerald-100 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="size-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                  <TrendingUp className="size-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI Recommendations</h3>
                <p className="text-sm text-gray-600">
                  Machine learning algorithms compute feasibility scores and ROI projections for
                  each energy type.
                </p>
              </CardContent>
            </Card>

            <Card className="border-emerald-100 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="size-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mb-4">
                  <LeafIcon className="size-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Impact Estimation</h3>
                <p className="text-sm text-gray-600">
                  Calculate environmental benefits including CO₂ reduction and energy generation
                  potential.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
