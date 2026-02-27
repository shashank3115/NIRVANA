import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

export function LocationMap({ selectedLocation, onLocationSelect }) {
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current).setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      onLocationSelect([lat, lng]);
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [onLocationSelect]);

  useEffect(() => {
    if (!mapRef.current || !selectedLocation) return;

    if (markerRef.current) {
      markerRef.current.setLatLng(selectedLocation);
    } else {
      markerRef.current = L.marker(selectedLocation, { draggable: true }).addTo(mapRef.current);
      markerRef.current.on('dragend', (e) => {
        const { lat, lng } = e.target.getLatLng();
        onLocationSelect([lat, lng]);
      });
    }

    mapRef.current.setView(selectedLocation, 12);
  }, [selectedLocation, onLocationSelect]);

  return <div ref={containerRef} className="relative z-0 w-full h-[400px]" />;
}
