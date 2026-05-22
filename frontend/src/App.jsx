import { useEffect, useMemo, useRef, useState } from 'react';
import { Map as MapIcon, AlertCircle, Loader2, Navigation, Goal, Route as RouteIcon, ShieldCheck, AlertTriangle, CheckCircle, Menu, X, Info, Building2, ChevronDown, Check } from 'lucide-react';

import axios from 'axios';
import { MapContainer, TileLayer, Marker, Polyline, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Lista de fallback usada apenas se o endpoint /cities não responder no primeiro arranque.
const FALLBACK_CITIES = [
  { slug: 'vila_real', display_name: 'Vila Real', center: [41.296, -7.746],  radius_meters: 1500 },
  { slug: 'paris',     display_name: 'Paris',     center: [48.8584, 2.347],  radius_meters: 1500 },
];

function computeBounds(center, radius) {
  const marginLat = radius / 111000;
  const marginLng = radius / (111000 * Math.cos(center[0] * Math.PI / 180));
  return [
    [center[0] - marginLat, center[1] - marginLng],
    [center[0] + marginLat, center[1] + marginLng],
  ];
}

const startIconHtml = `<div class="bg-blue-600 text-white rounded-full p-2 w-9 h-9 flex items-center justify-center shadow-lg border-2 border-white">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
</div>`;

const endIconHtml = `<div class="bg-red-600 text-white rounded-full p-2 w-9 h-9 flex items-center justify-center shadow-lg border-2 border-white">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg>
</div>`;

const startMarkerIcon = new L.divIcon({ html: startIconHtml, className: 'custom-marker', iconSize: [36, 36], iconAnchor: [18, 36] });
const endMarkerIcon   = new L.divIcon({ html: endIconHtml,   className: 'custom-marker', iconSize: [36, 36], iconAnchor: [18, 36] });

function CityFly({ city }) {
  const map = useMap();
  useEffect(() => {
    if (!map || !city) return;
    try {
      const bounds = computeBounds(city.center, city.radius_meters);
      map.setMaxBounds(L.latLngBounds(bounds));
      map.flyTo(L.latLng(city.center[0], city.center[1]), 15, { duration: 0.8 });
    } catch (err) {
      console.warn('CityFly skipped:', err);
    }
  }, [city, map]);
  return null;
}

function InteractiveMap({ city, startCoords, setStartCoords, endCoords, setEndCoords, setRouteGeometry, setError, setInfo, setIsSnapping }) {
  // O useMapEvents regista os handlers uma única vez, com a closure que existir
  // no primeiro render. Espelhamos o `city` (e algumas outras props) através de
  // um ref para que o handler veja sempre a seleção atual do utilizador, sem
  // precisar de voltar a registar eventos quando a cidade muda.
  const cityRef    = useRef(city);
  const startRef   = useRef(startCoords);
  const endRef     = useRef(endCoords);
  useEffect(() => { cityRef.current  = city;        }, [city]);
  useEffect(() => { startRef.current = startCoords; }, [startCoords]);
  useEffect(() => { endRef.current   = endCoords;   }, [endCoords]);

  useMapEvents({
    async click(e) {
      const activeCity = cityRef.current;
      const centerLatLng = L.latLng(activeCity.center[0], activeCity.center[1]);
      const dist = centerLatLng.distanceTo(e.latlng);
      if (dist >= activeCity.radius_meters * 0.95) {
        setError('Clicaste fora da zona de cobertura atual do CityFlow.');
        return;
      }

      setError(null);
      setInfo(null);

      if (startRef.current && endRef.current) {
        setStartCoords(null);
        setEndCoords(null);
        setRouteGeometry([]);
        return;
      }

      setIsSnapping(true);
      try {
        const response = await axios.post(`${API_BASE_URL}/api/v1/snap-point`, {
          coords: [e.latlng.lat, e.latlng.lng],
          city: activeCity.slug,
        }, { timeout: 12000 });

        if (response.data && response.data.snapped_coords) {
          const snapped = response.data.snapped_coords;
          const adjusted = response.data.adjusted;
          const offset = response.data.distance_meters;

          if (!startRef.current) {
            setStartCoords(snapped);
          } else if (!endRef.current) {
            setEndCoords(snapped);
          }

          if (adjusted && offset > 5) {
            setInfo(`Ponto ajustado para a rua pedonal mais próxima (${offset.toFixed(0)} m).`);
          }
        }
      } catch (err) {
        if (err.code === 'ECONNABORTED') {
          setError('O servidor demorou demasiado a validar o ponto. Tenta novamente em instantes.');
        } else if (err.response && err.response.status === 422) {
          setError(err.response.data.detail || 'Ponto inválido. Clica mais perto de uma rua pedonal.');
        } else if (err.message && err.message.toLowerCase().includes('network')) {
          setError('Sem ligação ao servidor. Verifica se o backend está em execução.');
        } else {
          setError('Não foi possível validar o ponto no servidor.');
        }
      } finally {
        setIsSnapping(false);
      }
    },
  });

  return null;
}

function CityDropdown({ cities, value, onChange }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const onClickAway = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    };
    const onEsc = (event) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onClickAway);
    document.addEventListener('keydown', onEsc);
    return () => {
      document.removeEventListener('mousedown', onClickAway);
      document.removeEventListener('keydown', onEsc);
    };
  }, [open]);

  const current = cities.find((c) => c.slug === value) || cities[0];

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="w-full flex items-center justify-between gap-3 bg-white border border-slate-200 hover:border-blue-300 rounded-xl px-4 py-3 text-left shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400 min-h-[48px]"
      >
        <span className="flex items-center gap-3 min-w-0">
          <span className="bg-blue-50 text-blue-600 rounded-lg p-1.5 shrink-0">
            <Building2 size={18} />
          </span>
          <span className="font-bold text-slate-800 truncate">{current.display_name}</span>
        </span>
        <ChevronDown
          size={18}
          className={`text-slate-400 shrink-0 transition-transform duration-200 ${open ? 'rotate-180 text-blue-600' : ''}`}
        />
      </button>

      {open && (
        <ul
          role="listbox"
          className="absolute z-30 left-0 right-0 mt-2 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-top-1"
        >
          {cities.map((c) => {
            const active = c.slug === value;
            return (
              <li
                key={c.slug}
                role="option"
                aria-selected={active}
                tabIndex={0}
                onClick={() => { onChange(c.slug); setOpen(false); }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onChange(c.slug);
                    setOpen(false);
                  }
                }}
                className={`flex items-center justify-between gap-3 px-4 py-3 cursor-pointer transition-colors ${
                  active ? 'bg-blue-50 text-blue-700' : 'hover:bg-slate-50 text-slate-700'
                }`}
              >
                <span className="font-semibold">{c.display_name}</span>
                {active && <Check size={16} className="text-blue-600" />}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default function App() {
  const [cities, setCities] = useState(FALLBACK_CITIES);
  const [citySlug, setCitySlug] = useState(FALLBACK_CITIES[0].slug);

  const [startCoords, setStartCoords] = useState(null);
  const [endCoords, setEndCoords] = useState(null);
  const [routeGeometry, setRouteGeometry] = useState([]);
  const [routeDistance, setRouteDistance] = useState(0);
  const [maxRouteIncline, setMaxRouteIncline] = useState(0);

  const [maxIncline, setMaxIncline] = useState(8);
  const [minWidth, setMinWidth] = useState(1.2);
  const [avoidStairs, setAvoidStairs] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [isSnapping, setIsSnapping] = useState(false);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const city = useMemo(
    () => cities.find((c) => c.slug === citySlug) || cities[0],
    [cities, citySlug],
  );

  useEffect(() => {
    let cancelled = false;
    axios.get(`${API_BASE_URL}/api/v1/cities`).then((response) => {
      if (cancelled || !response.data) return;
      const list = response.data.cities || [];
      if (list.length > 0) {
        setCities(list);
        setCitySlug((current) => list.some((c) => c.slug === current) ? current : (response.data.default || list[0].slug));
      }
    }).catch(() => {
      // mantém a lista de fallback
    });
    return () => { cancelled = true; };
  }, []);

  const handleCityChange = (slug) => {
    setCitySlug(slug);
    setStartCoords(null);
    setEndCoords(null);
    setRouteGeometry([]);
    setRouteDistance(0);
    setMaxRouteIncline(0);
    setError(null);
    setInfo(null);
  };

  const handleCalculateRoute = async () => {
    if (!startCoords || !endCoords) {
      setError('Por favor clica no mapa para definir a Partida e o Destino.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setInfo(null);
    setRouteGeometry([]);
    setRouteDistance(0);
    setMaxRouteIncline(0);

    try {
      const payload = {
        start_coords: startCoords,
        end_coords: endCoords,
        city: city.slug,
        profile: {
          profile_name: 'custom_user',
          max_incline: maxIncline / 100.0,
          min_width: parseFloat(minWidth),
          avoid_stairs: avoidStairs,
          surface_preference: ['paved', 'asphalt', 'concrete'],
        },
      };

      const response = await axios.post(`${API_BASE_URL}/api/v1/route`, payload);

      if (response.data && response.data.route_geometry) {
        setRouteGeometry(response.data.route_geometry);
        setRouteDistance(response.data.distance_meters || 0);
        setMaxRouteIncline(response.data.max_route_incline || 0);
      }
    } catch (err) {
      if (err.response && err.response.status === 424) {
        setError(`Não existe rota possível com as restrições atuais (inclinação máx.: ${maxIncline}%, largura mín.: ${minWidth} m).`);
      } else {
        setError('Ocorreu um erro inesperado ao comunicar com o servidor.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const initialBounds = useMemo(() => computeBounds(city.center, city.radius_meters), [city]);

  return (
    <div className="w-screen h-screen flex overflow-hidden bg-slate-50 font-sans text-slate-800">

      <button
        className="md:hidden fixed z-[60] bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-2xl transition-transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2 font-bold"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        aria-label="Abrir/fechar menu"
      >
        {isSidebarOpen ? <X size={24} /> : (
          <>
            <Menu size={24} />
            <span className="hidden sm:inline">Definições</span>
          </>
        )}
      </button>

      {isSidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[40] animate-in fade-in transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <aside className={`fixed md:relative top-0 left-0 h-full bg-white border-r border-slate-200 shadow-2xl md:shadow-xl z-50 flex flex-col shrink-0 w-[90%] max-w-[400px] md:w-[35%] lg:w-[30%] md:min-w-[320px] md:max-w-[450px] transform transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>

        <div className="flex-1 overflow-y-auto p-6 md:p-8 flex flex-col gap-8">

          <div className="flex items-center gap-4">
            <div className="bg-blue-100 p-3 rounded-2xl shrink-0 text-blue-600">
              <MapIcon size={32} />
            </div>
            <div className="flex flex-col">
              <h1 className="text-3xl font-black text-slate-800 tracking-tight leading-none mb-1">
                CityFlow
              </h1>
              <p className="text-blue-600 font-bold tracking-wide text-sm">
                Mobilidade inclusiva
              </p>
            </div>
          </div>

          <div className="border-t border-slate-100" />

          <div className="flex flex-col gap-3">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Building2 className="text-slate-400" size={20} /> Cidade
            </h2>
            <CityDropdown
              cities={cities}
              value={city.slug}
              onChange={handleCityChange}
            />
            <p className="text-xs text-slate-400 leading-relaxed">
              Cada cidade tem o seu próprio grafo OSM com elevação real do terreno.
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <RouteIcon className="text-slate-400" size={20} /> O Teu Trajeto
            </h2>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-sm space-y-3">
               <div className="flex items-center gap-3">
                  <Navigation className={`w-5 h-5 shrink-0 ${startCoords ? 'text-blue-600' : 'text-slate-300'}`} />
                  <span className={startCoords ? 'font-semibold text-slate-700' : 'text-slate-400 italic'}>
                    {startCoords ? 'Partida definida' : 'Clica no mapa p/ Partida'}
                  </span>
               </div>
               <div className="flex items-center gap-3">
                  <Goal className={`w-5 h-5 shrink-0 ${endCoords ? 'text-red-500' : 'text-slate-300'}`} />
                  <span className={endCoords ? 'font-semibold text-slate-700' : 'text-slate-400 italic'}>
                    {endCoords ? 'Destino definido' : 'Clica no mapa p/ Destino'}
                  </span>
               </div>
            </div>
          </div>

          <div className="flex flex-col gap-5">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <ShieldCheck className="text-slate-400" size={20} /> O Teu Perfil de Acessibilidade
            </h2>

            <div className="flex flex-col gap-6 bg-white p-5 rounded-2xl shadow-sm border border-slate-200">

              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label htmlFor="incline-slider" className="font-semibold text-slate-700 text-sm">Inclinação máxima</label>
                  <span className="font-bold text-blue-600 text-sm bg-blue-50 px-2 rounded-md">{maxIncline}%</span>
                </div>
                <input
                  id="incline-slider"
                  type="range"
                  min="2" max="15" step="1"
                  value={maxIncline}
                  onChange={(e) => setMaxIncline(e.target.value)}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />

                <div className="flex justify-between text-xs font-semibold mt-1">
                   <span className={maxIncline <= 5 ? 'text-emerald-600 font-bold' : 'text-slate-400'}>
                     {maxIncline <= 5 ? 'Suave / Muito acessível' : ''}
                   </span>
                   <span className={maxIncline > 5 && maxIncline <= 11 ? 'text-blue-600 font-bold' : 'text-slate-400'}>
                     {maxIncline > 5 && maxIncline <= 11 ? 'Padrão (norma técnica)' : ''}
                   </span>
                   <span className={maxIncline >= 12 ? 'text-red-500 font-bold' : 'text-slate-400'}>
                     {maxIncline >= 12 ? 'Exigente / só para especialistas' : ''}
                   </span>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label htmlFor="width-slider" className="font-semibold text-slate-700 text-sm">Largura mínima da via</label>
                  <span className="font-bold text-blue-600 text-sm bg-blue-50 px-2 rounded-md">{minWidth} m</span>
                </div>
                <input
                  id="width-slider"
                  type="range"
                  min="0.5" max="2.0" step="0.1"
                  value={minWidth}
                  onChange={(e) => setMinWidth(e.target.value)}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>

              <div className="border-t border-slate-100" />

              <label className="flex items-center justify-between cursor-pointer group">
                <span className="font-semibold text-slate-700 text-sm group-hover:text-blue-700 transition-colors">Evitar escadas</span>
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={avoidStairs}
                    onChange={(e) => setAvoidStairs(e.target.checked)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setAvoidStairs(!avoidStairs);
                      }
                    }}
                  />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </div>
              </label>

            </div>
          </div>

          {info && (
            <div role="status" className="bg-blue-50 text-blue-700 p-4 rounded-xl border border-blue-200 flex items-start gap-2 animate-in fade-in">
               <Info className="w-5 h-5 shrink-0 mt-0.5" />
               <p className="text-sm font-medium leading-relaxed">{info}</p>
            </div>
          )}

          {error && (
            <div role="alert" className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200 flex flex-col gap-2 animate-in fade-in">
               <div className="flex items-center gap-2 font-bold text-sm">
                 <AlertCircle className="w-5 h-5" />
                 Alerta de acessibilidade
               </div>
              <p className="text-sm font-medium leading-relaxed">{error}</p>
            </div>
          )}

        </div>

         <div className="p-6 border-t border-slate-200 bg-slate-50 flex flex-col gap-4">
           <button
             type="button"
             onClick={handleCalculateRoute}
             disabled={isLoading || !startCoords || !endCoords}
             className="w-full flex items-center justify-center px-6 py-4 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl transition-all shadow-lg focus:outline-none focus:ring-4 focus:ring-slate-300 disabled:opacity-50 disabled:cursor-not-allowed group"
           >
             {isLoading ? (
               <><Loader2 className="animate-spin mr-3 w-5 h-5" />A calcular…</>
             ) : (
               <span className="group-hover:scale-105 transition-transform">Calcular rota segura</span>
             )}
           </button>

           {routeDistance > 0 && !error && (
              <div className="flex flex-col gap-3 animate-in slide-in-from-bottom-2">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex justify-around items-center">
                   <div className="flex flex-col items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Distância</span>
                      <span className="text-lg font-black text-slate-700">{(routeDistance / 1000).toFixed(2)} <span className="text-sm font-semibold">km</span></span>
                   </div>
                   <div className="w-px h-10 bg-slate-100"></div>
                   <div className="flex flex-col items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Tempo est.</span>
                      <span className="text-lg font-black text-blue-600">
                        {Math.ceil(routeDistance / ((maxIncline < 10 && minWidth > 0.8) ? 58.3 : 41.6))} <span className="text-sm font-semibold">min</span>
                      </span>
                   </div>
                   <div className="w-px h-10 bg-slate-100"></div>
                   <div className="flex flex-col items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Inclinação crítica</span>
                      <span className={`text-lg font-black ${(maxRouteIncline * 100) > maxIncline ? 'text-red-600' : 'text-emerald-600'}`}>
                        {(maxRouteIncline * 100).toFixed(1)} <span className="text-sm font-semibold">%</span>
                      </span>
                   </div>
                </div>

                {(maxRouteIncline * 100) > maxIncline ? (
                  <div className="flex items-center justify-center gap-2 text-red-700 bg-red-50 p-3 rounded-xl border border-red-200 text-sm font-bold animate-in zoom-in-95">
                     <AlertTriangle className="w-5 h-5 shrink-0" />
                     <span>Atenção: esta rota excede o teu limite de conforto.</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2 text-emerald-700 bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-sm font-bold animate-in zoom-in-95">
                     <CheckCircle className="w-5 h-5 shrink-0" />
                     <span>Dentro do teu limite de conforto.</span>
                  </div>
                )}
              </div>
           )}

           <p className="text-xs text-center font-medium text-slate-400">
             O 3.º clique no mapa limpa a simulação.
           </p>
         </div>

      </aside>

      <main className="flex-1 w-full relative z-0">
        {isSnapping && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-white/90 backdrop-blur px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-sm font-semibold text-slate-700">
            <Loader2 className="animate-spin w-4 h-4" />
            A validar ponto…
          </div>
        )}
        <MapContainer
          center={city.center}
          zoom={15}
          style={{ height: '100%', width: '100%' }}
          maxBounds={initialBounds}
          maxBoundsViscosity={1.0}
          minZoom={14}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <CityFly city={city} />

          <InteractiveMap
             city={city}
             startCoords={startCoords} setStartCoords={setStartCoords}
             endCoords={endCoords} setEndCoords={setEndCoords}
             setRouteGeometry={setRouteGeometry}
             setError={setError}
             setInfo={setInfo}
             setIsSnapping={setIsSnapping}
          />

          {startCoords && <Marker position={startCoords} icon={startMarkerIcon} />}
          {endCoords   && <Marker position={endCoords}   icon={endMarkerIcon}   />}

          {routeGeometry.length > 0 && (
            <Polyline
              positions={routeGeometry}
              pathOptions={{ color: '#2563eb', weight: 6, opacity: 0.8, lineCap: 'round', lineJoin: 'round' }}
            />
          )}
        </MapContainer>
      </main>

    </div>
  );
}
