import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sun,
  Wind,
  Droplet,
  TrendingUp,
  IndianRupee,
  Calendar,
  MapPin,
  ArrowLeft,
  Sparkles,
  Activity,
  FileText,
  AlertTriangle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import { analyzeMultiRenewable } from '../../services/apiService';

const CURRENCY_FORMATTER = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

const ENERGY_TYPES = {
  Solar: {
    icon: Sun,
    gradientFrom: 'from-amber-500',
    gradientTo: 'to-orange-600',
  },
  Wind: {
    icon: Wind,
    gradientFrom: 'from-blue-500',
    gradientTo: 'to-cyan-600',
  },
  Hydro: {
    icon: Droplet,
    gradientFrom: 'from-teal-500',
    gradientTo: 'to-emerald-600',
  },
};

function estimateInstallationCostInr(annualOutputKwh, paybackYears, electricityRate = 8) {
  const annualSavings = annualOutputKwh * electricityRate;
  return annualSavings * paybackYears;
}

function formatKwh(value) {
  return `${Math.round(value).toLocaleString('en-IN')} kWh/year`;
}

function formatYears(value) {
  return `${Number(value).toFixed(1)} years`;
}

function estimateCo2Kg(annualOutputKwh) {
  return Math.round(annualOutputKwh * 0.72);
}

export function Results() {
  const navigate = useNavigate();
  const [location] = useState(() => {
    const stored = localStorage.getItem('enerscope_location');
    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  });

  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' });
    if (!location) {
      navigate('/', { replace: true });
      return;
    }

    const [lat, lng] = location.coordinates || [];
    if (typeof lat !== 'number' || typeof lng !== 'number') {
      navigate('/', { replace: true });
      return;
    }

    let cancelled = false;

    async function runAnalysis() {
      setIsLoading(true);
      setError('');

      try {
        const data = await analyzeMultiRenewable({
          lat,
          lng,
          include_solar: true,
          include_wind: true,
        });

        if (!cancelled) {
          setAnalysis(data);
        }
      } catch (analysisError) {
        if (!cancelled) {
          setError(
            analysisError?.response?.data?.detail
              || analysisError?.message
              || 'Failed to fetch live analysis. Please try again.',
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    runAnalysis();

    return () => {
      cancelled = true;
    };
  }, [location, navigate]);

  const renewableOptions = useMemo(() => {
    if (!analysis) {
      return [];
    }

    const electricityRate = 8;

    return [
      {
        type: 'Solar',
        score: analysis.solar_suitability_score,
        confidence: analysis.solar_confidence_index,
        annualOutput: analysis.solar_annual_output_kwh,
        paybackYears: analysis.solar_payback_years,
        recommendation: analysis.solar_recommendation?.recommendation || 'CAUTION',
        risks: analysis.solar_risk_analysis?.risk_level || 'Medium',
        installationCostInr: estimateInstallationCostInr(
          analysis.solar_annual_output_kwh,
          analysis.solar_payback_years,
          electricityRate,
        ),
      },
      {
        type: 'Wind',
        score: analysis.wind_suitability_score,
        confidence: analysis.wind_confidence_index,
        annualOutput: analysis.wind_annual_output_kwh,
        paybackYears: analysis.wind_payback_years,
        recommendation: analysis.wind_recommendation?.recommendation || 'CAUTION',
        risks: analysis.wind_risk_analysis?.risk_level || 'Medium',
        installationCostInr: estimateInstallationCostInr(
          analysis.wind_annual_output_kwh,
          analysis.wind_payback_years,
          electricityRate,
        ),
      },
      {
        type: 'Hydro',
        score: analysis.hydro_suitability_score || 0,
        confidence: analysis.hydro_confidence_index || 0,
        annualOutput: analysis.hydro_annual_output_kwh || 0,
        paybackYears: analysis.hydro_payback_years || 99,
        recommendation: analysis.hydro_recommendation?.recommendation || 'NO-GO',
        risks: analysis.hydro_risk_analysis?.risk_level || 'High',
        installationCostInr: estimateInstallationCostInr(
          analysis.hydro_annual_output_kwh || 0,
          analysis.hydro_payback_years || 99,
          electricityRate,
        ),
      },
    ].sort((a, b) => b.score - a.score);
  }, [analysis]);

  const comparisonData = useMemo(
    () => renewableOptions.map((option) => ({
      name: option.type,
      feasibility: option.score,
      output: Math.round(option.annualOutput),
      payback: Number(option.paybackYears.toFixed(1)),
      confidence: option.confidence,
    })),
    [renewableOptions],
  );

  const projectionData = useMemo(() => {
    const years = [1, 3, 5, 10, 15];
    const electricityRate = 8;

    const getSeries = (option, year) => {
      const annualSavings = option.annualOutput * electricityRate;
      const net = annualSavings * year - option.installationCostInr;
      return Math.round(net);
    };

    const solar = renewableOptions.find((item) => item.type === 'Solar');
    const wind = renewableOptions.find((item) => item.type === 'Wind');
    const hydro = renewableOptions.find((item) => item.type === 'Hydro');

    return years.map((year) => ({
      year: `Y${year}`,
      solar: solar ? getSeries(solar, year) : 0,
      wind: wind ? getSeries(wind, year) : 0,
      hydro: hydro ? getSeries(hydro, year) : 0,
    }));
  }, [renewableOptions]);

  const reportPoints = useMemo(() => {
    if (!analysis || renewableOptions.length === 0) {
      return [];
    }

    const top = renewableOptions[0];
    const second = renewableOptions[1];

    return [
      `Best overall option is ${analysis.best_renewable_option} with decision confidence ${analysis.overall_decision_confidence?.confidence_index || 0}%.`,
      `${top.type} shows ${top.score}/100 suitability, ${top.confidence}% confidence, and estimated payback of ${formatYears(top.paybackYears)}.`,
      second ? `${second.type} is the next strong option with ${second.score}/100 suitability and ${formatKwh(second.annualOutput)} generation.` : 'No secondary option available.',
      `Weather basis: solar irradiance ${analysis.solar_irradiance?.toFixed(2)} kWh/m²/day, wind ${analysis.wind_speed?.toFixed(1)} m/s, cloud cover ${analysis.cloud_cover_pct?.toFixed(0)}%, humidity ${analysis.humidity_pct?.toFixed(0)}%, slope ${analysis.slope_degrees?.toFixed(1)}° and elevation ${analysis.elevation?.toFixed(0)}m.`,
      `Data sources combined in backend pipeline: solar irradiance (NASA POWER), weather (Open-Meteo), elevation/slope (Google Elevation or Open-Elevation).`,
    ];
  }, [analysis, renewableOptions]);

  const weatherRows = useMemo(() => {
    if (!analysis || renewableOptions.length === 0) {
      return [];
    }

    const bestNow = renewableOptions[0]?.type || 'Solar';
    const windFavored = analysis.wind_speed >= 6;
    const cloudFavoredWind = analysis.cloud_cover_pct >= 65;
    const solarFavored = analysis.solar_irradiance >= 4.8 && analysis.cloud_cover_pct <= 45;

    return [
      {
        condition: 'Current observed',
        solarIrradiance: `${analysis.solar_irradiance.toFixed(2)} kWh/m²/day`,
        windSpeed: `${analysis.wind_speed.toFixed(1)} m/s`,
        cloudCover: `${analysis.cloud_cover_pct.toFixed(0)}%`,
        humidity: `${analysis.humidity_pct.toFixed(0)}%`,
        bestOption: bestNow,
      },
      {
        condition: 'High cloud / monsoon-like',
        solarIrradiance: `${(analysis.solar_irradiance * 0.78).toFixed(2)} kWh/m²/day`,
        windSpeed: `${(analysis.wind_speed * 1.2).toFixed(1)} m/s`,
        cloudCover: `${Math.min(95, analysis.cloud_cover_pct + 20).toFixed(0)}%`,
        humidity: `${Math.min(95, analysis.humidity_pct + 12).toFixed(0)}%`,
        bestOption: windFavored || cloudFavoredWind ? 'Wind' : bestNow,
      },
      {
        condition: 'Clear summer-like',
        solarIrradiance: `${(analysis.solar_irradiance * 1.12).toFixed(2)} kWh/m²/day`,
        windSpeed: `${(analysis.wind_speed * 0.9).toFixed(1)} m/s`,
        cloudCover: `${Math.max(8, analysis.cloud_cover_pct - 20).toFixed(0)}%`,
        humidity: `${Math.max(20, analysis.humidity_pct - 10).toFixed(0)}%`,
        bestOption: solarFavored ? 'Solar' : bestNow,
      },
    ];
  }, [analysis, renewableOptions]);

  if (!location) {
    return null;
  }

  return (
    <div className="min-h-screen py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate('/')} className="mb-4 hover:bg-emerald-50">
            <ArrowLeft className="size-4 mr-2" />
            Back to Home
          </Button>

          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Renewable Energy Analysis</h1>
              <div className="flex items-center gap-2 text-gray-600">
                <MapPin className="size-4" />
                <span>{location.address}</span>
              </div>
            </div>
            <Badge className="bg-gradient-to-r from-emerald-600 to-teal-600">Live Analysis</Badge>
          </div>
        </div>

        {isLoading && (
          <Card className="mb-8 border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50">
            <CardContent className="p-6">
              <div className="flex items-center gap-2 text-gray-600">
                <Activity className="size-4 animate-pulse" />
                <span>Running weather + terrain + multi-renewable analysis...</span>
              </div>
            </CardContent>
          </Card>
        )}

        {!isLoading && error && (
          <Card className="mb-8 border-red-200 bg-red-50">
            <CardContent className="p-6">
              <div className="flex items-center gap-2 text-red-700">
                <AlertTriangle className="size-5" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {!isLoading && !error && analysis && (
          <>
            <Card className="mb-8 border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="size-5 text-purple-600" />
                  AI-Powered Multi-Parameter Insight
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 leading-relaxed">
                  {analysis.ai_decision_summary || 'Live analysis completed successfully.'}
                </p>
              </CardContent>
            </Card>

            <Tabs defaultValue="options" className="mb-8">
              <TabsList className="grid w-full grid-cols-4 max-w-4xl">
                <TabsTrigger value="options">All Options</TabsTrigger>
                <TabsTrigger value="comparison">Comparison</TabsTrigger>
                <TabsTrigger value="projections">Projections</TabsTrigger>
                <TabsTrigger value="weather">Weather Parameters</TabsTrigger>
              </TabsList>

              <TabsContent value="options" className="space-y-6">
                {renewableOptions.map((option, index) => {
                  const energyVisual = ENERGY_TYPES[option.type];
                  const IconComponent = energyVisual?.icon || Sun;
                  return (
                    <Card key={option.type} className="border-emerald-100 hover:shadow-lg transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start gap-4">
                          <div className={`bg-gradient-to-br ${energyVisual.gradientFrom} ${energyVisual.gradientTo} p-3 rounded-xl`}>
                            <IconComponent className="size-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-3">
                              <h3 className="text-xl font-semibold text-gray-900">{option.type} Energy</h3>
                              {index === 0 && <Badge className="bg-emerald-600">Recommended</Badge>}
                            </div>

                            <div className="mb-4">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-gray-700">Feasibility Score</span>
                                <span className="text-sm font-bold text-gray-900">{option.score}/100</span>
                              </div>
                              <Progress value={option.score} className="h-2" />
                            </div>

                            <div className="grid md:grid-cols-5 gap-4">
                              <div className="flex items-center gap-2">
                                <Activity className="size-4 text-gray-500" />
                                <div>
                                  <p className="text-xs text-gray-600">Generation</p>
                                  <p className="text-sm font-semibold">{formatKwh(option.annualOutput)}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <IndianRupee className="size-4 text-gray-500" />
                                <div>
                                  <p className="text-xs text-gray-600">Cost</p>
                                  <p className="text-sm font-semibold">{CURRENCY_FORMATTER.format(option.installationCostInr)}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Calendar className="size-4 text-gray-500" />
                                <div>
                                  <p className="text-xs text-gray-600">Payback</p>
                                  <p className="text-sm font-semibold">{formatYears(option.paybackYears)}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <TrendingUp className="size-4 text-gray-500" />
                                <div>
                                  <p className="text-xs text-gray-600">Confidence</p>
                                  <p className="text-sm font-semibold">{option.confidence}%</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Sun className="size-4 text-gray-500" />
                                <div>
                                  <p className="text-xs text-gray-600">CO₂ Saved</p>
                                  <p className="text-sm font-semibold">{estimateCo2Kg(option.annualOutput).toLocaleString('en-IN')} kg/year</p>
                                </div>
                              </div>
                            </div>

                            <div className="mt-4 flex flex-wrap gap-2">
                              <Badge variant="secondary">Recommendation: {option.recommendation}</Badge>
                              <Badge variant="outline">Risk: {option.risks}</Badge>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </TabsContent>

              <TabsContent value="comparison" className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Feasibility Comparison</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={comparisonData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="feasibility" fill="#10b981" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Annual Output Comparison (kWh)</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={comparisonData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="output" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="projections" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="size-5 text-emerald-600" />
                      15-Year Projection Report (Net Savings)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={360}>
                      <LineChart data={projectionData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Tooltip formatter={(value) => CURRENCY_FORMATTER.format(Number(value))} />
                        <Legend />
                        <Line type="monotone" dataKey="solar" stroke="#f59e0b" strokeWidth={2} name="Solar" />
                        <Line type="monotone" dataKey="wind" stroke="#3b82f6" strokeWidth={2} name="Wind" />
                        <Line type="monotone" dataKey="hydro" stroke="#14b8a6" strokeWidth={2} name="Hydro" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="size-5 text-emerald-600" />
                      Projection Summary Report
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-sm text-gray-700">
                      {reportPoints.map((point) => (
                        <li key={point} className="flex items-start gap-2">
                          <span className="text-emerald-600 mt-0.5">•</span>
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="weather">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="size-5 text-emerald-600" />
                      Best Parameters in Different Weather Conditions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-200 text-left">
                            <th className="py-3 pr-4 font-semibold text-gray-800">Condition</th>
                            <th className="py-3 pr-4 font-semibold text-gray-800">Solar Irradiance</th>
                            <th className="py-3 pr-4 font-semibold text-gray-800">Wind Speed</th>
                            <th className="py-3 pr-4 font-semibold text-gray-800">Cloud Cover</th>
                            <th className="py-3 pr-4 font-semibold text-gray-800">Humidity</th>
                            <th className="py-3 font-semibold text-gray-800">Best Option</th>
                          </tr>
                        </thead>
                        <tbody>
                          {weatherRows.map((row) => (
                            <tr key={row.condition} className="border-b border-gray-100">
                              <td className="py-3 pr-4 font-medium text-gray-900">{row.condition}</td>
                              <td className="py-3 pr-4 text-gray-700">{row.solarIrradiance}</td>
                              <td className="py-3 pr-4 text-gray-700">{row.windSpeed}</td>
                              <td className="py-3 pr-4 text-gray-700">{row.cloudCover}</td>
                              <td className="py-3 pr-4 text-gray-700">{row.humidity}</td>
                              <td className="py-3">
                                <Badge variant="secondary">{row.bestOption}</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </>
        )}

        <div className="flex gap-4 justify-center">
          <Button size="lg" variant="outline" onClick={() => navigate('/')} className="border-emerald-200 hover:bg-emerald-50">
            Analyze New Location
          </Button>
          <Button
            size="lg"
            className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
            onClick={() => window.print()}
          >
            Download Report
          </Button>
        </div>
      </div>
    </div>
  );
}
