import {
  Satellite,
  Brain,
  Database,
  Sparkles,
  Sun,
  Wind,
  Droplet,
  Leaf as LeafIcon,
  Target,
  Users,
  TrendingUp,
  Shield,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

export function About() {
  const features = [
    {
      icon: Satellite,
      title: 'Satellite Analysis',
      description:
        'Leverages Sentinel-2 imagery and NASA POWER API for accurate solar irradiance, land classification, and vegetation indexing.',
      color: 'from-blue-500 to-indigo-600',
    },
    {
      icon: Brain,
      title: 'Machine Learning',
      description:
        'Random Forest and Linear Regression models compute feasibility scores and energy generation estimates with high precision.',
      color: 'from-purple-500 to-pink-600',
    },
    {
      icon: Database,
      title: 'Multi-Source Data',
      description:
        'Integrates climate data from Open-Meteo, geographic context from OpenStreetMap, and environmental indicators for comprehensive analysis.',
      color: 'from-emerald-500 to-teal-600',
    },
    {
      icon: Sparkles,
      title: 'AI Reasoning',
      description:
        'LLM-powered explanation engine contextualizes ML outputs into clear, actionable insights for users.',
      color: 'from-amber-500 to-orange-600',
    },
  ];

  const renewableTypes = [
    {
      icon: Sun,
      name: 'Solar',
      description:
        'Evaluates solar irradiance, roof orientation, shading, and available space for photovoltaic installations.',
      color: 'text-amber-600',
    },
    {
      icon: Wind,
      name: 'Micro-Wind',
      description:
        'Analyzes wind speed patterns, turbulence, urban density, and zoning regulations for small-scale turbines.',
      color: 'text-blue-600',
    },
    {
      icon: Droplet,
      name: 'Micro-Hydro',
      description:
        'Assesses water flow, elevation changes, proximity to streams, and seasonal variations for hydroelectric potential.',
      color: 'text-teal-600',
    },
    {
      icon: LeafIcon,
      name: 'Biomass',
      description:
        'Evaluates vegetation density, agricultural waste availability, and organic material supply for bioenergy systems.',
      color: 'text-green-600',
    },
  ];

  const methodology = [
    {
      step: '01',
      title: 'Location Input',
      description: 'User provides address or selects location via interactive map interface.',
    },
    {
      step: '02',
      title: 'Data Collection',
      description:
        'System retrieves satellite imagery, climate data, solar irradiance, wind patterns, and geographic features.',
    },
    {
      step: '03',
      title: 'Feature Extraction',
      description:
        'ML pipeline computes land openness, NDVI, water proximity, elevation, and urban density metrics.',
    },
    {
      step: '04',
      title: 'Feasibility Scoring',
      description:
        'Random Forest algorithms generate 0-100 suitability scores for each renewable energy type.',
    },
    {
      step: '05',
      title: 'Financial Analysis',
      description: 'System estimates installation costs, energy generation, ROI, and payback periods.',
    },
    {
      step: '06',
      title: 'AI Explanation',
      description:
        'LLM interprets ML outputs and generates human-readable recommendations with trade-off analysis.',
    },
  ];

  const userClasses = [
    {
      icon: Users,
      title: 'Homeowners',
      description: 'Individuals exploring renewable energy options for their property.',
    },
    {
      icon: Target,
      title: 'Rural Landowners',
      description: 'Agricultural property owners evaluating energy independence.',
    },
    {
      icon: LeafIcon,
      title: 'Eco-Conscious Users',
      description: 'Users motivated by reducing their carbon footprint.',
    },
    {
      icon: TrendingUp,
      title: 'Infrastructure Planners',
      description: 'Analysts evaluating community-scale energy solutions (future scope).',
    },
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-gradient-to-r from-emerald-600 to-teal-600">Version 1.0 | 2026</Badge>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">About EnerScope AI</h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            An AI-powered renewable energy recommendation platform that analyzes geographic,
            satellite, and climate data to recommend the most suitable small-scale renewable
            energy source for any location.
          </p>
        </div>

        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Core Technologies</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature) => (
              <Card key={feature.title} className="border-emerald-100 hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={`bg-gradient-to-br ${feature.color} p-3 rounded-xl`}>
                      <feature.icon className="size-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-sm text-gray-600">{feature.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Evaluated Renewable Sources</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {renewableTypes.map((type) => (
              <Card key={type.name} className="border-emerald-100">
                <CardContent className="p-6 text-center">
                  <type.icon className={`size-12 ${type.color} mx-auto mb-4`} />
                  <h3 className="font-semibold text-gray-900 mb-2">{type.name}</h3>
                  <p className="text-sm text-gray-600">{type.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Analysis Methodology</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {methodology.map((item) => (
              <Card key={item.step} className="border-emerald-100">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-bold text-lg size-10 rounded-lg flex items-center justify-center shrink-0">
                      {item.step}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                      <p className="text-sm text-gray-600">{item.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Who We Serve</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {userClasses.map((userClass) => (
              <Card key={userClass.title} className="border-emerald-100">
                <CardContent className="p-6 text-center">
                  <div className="bg-gradient-to-br from-emerald-500 to-teal-600 p-3 rounded-xl inline-flex mb-4">
                    <userClass.icon className="size-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{userClass.title}</h3>
                  <p className="text-sm text-gray-600">{userClass.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <Card className="border-emerald-100">
          <CardHeader>
            <CardTitle className="text-center">Technology Stack</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Frontend</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• React with TypeScript</li>
                  <li>• Tailwind CSS</li>
                  <li>• Recharts for visualization</li>
                  <li>• Leaflet for mapping</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Backend</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• FastAPI (Python)</li>
                  <li>• scikit-learn (ML)</li>
                  <li>• Random Forest & Linear Regression</li>
                  <li>• Gemini/OpenAI LLM</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Data Sources</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• NASA POWER API</li>
                  <li>• Open-Meteo API</li>
                  <li>• Sentinel-2 Satellite</li>
                  <li>• OpenStreetMap</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-8 border-amber-200 bg-amber-50/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Shield className="size-5 text-amber-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Important Notice</h3>
                <p className="text-sm text-gray-700">
                  EnerScope AI provides preliminary renewable energy feasibility assessments based
                  on publicly available data. Results should not replace professional engineering
                  consultation, site surveys, or detailed feasibility studies. Always consult with
                  certified renewable energy professionals before making installation decisions.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
