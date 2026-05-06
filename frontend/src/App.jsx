import { useState } from 'react';
import { Map as MapIcon, AlertCircle, Loader2, Navigation, Goal, Route as RouteIcon, ShieldCheck, AlertTriangle, CheckCircle, Menu, X } from 'lucide-react';

import axios from 'axios';
import { MapContainer, TileLayer, Marker, Polyline, useMapEvents } from 'react-leaflet';
import L from 'leaflet';


const MAP_COVERAGE_RADIUS = 5000; 
const CENTER_COORDS = [41.296, -7.746];
const CENTER_LATLNG = L.latLng(CENTER_COORDS[0], CENTER_COORDS[1]);


const marginLat = MAP_COVERAGE_RADIUS / 111000;
const marginLng = MAP_COVERAGE_RADIUS / (111000 * Math.cos(CENTER_COORDS[0] * Math.PI / 180));
const MAX_BOUNDS = [
  [CENTER_COORDS[0] - marginLat, CENTER_COORDS[1] - marginLng],
  [CENTER_COORDS[0] + marginLat, CENTER_COORDS[1] + marginLng]
];


const startIconHtml = `<div class="bg-blue-600 text-white rounded-full p-2 w-9 h-9 flex items-center justify-center shadow-lg border-2 border-white">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
</div>`;

const endIconHtml = `<div class="bg-red-600 text-white rounded-full p-2 w-9 h-9 flex items-center justify-center shadow-lg border-2 border-white">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg>
</div>`;

const startMarkerIcon = new L.divIcon({ html: startIconHtml, className: "custom-marker", iconSize: [36, 36], iconAnchor: [18, 36] });
const endMarkerIcon = new L.divIcon({ html: endIconHtml, className: "custom-marker", iconSize: [36, 36], iconAnchor: [18, 36] });

function InteractiveMap({ startCoords, setStartCoords, endCoords, setEndCoords, setRouteGeometry, setError, setIsSnapping }) {
  useMapEvents({
    async click(e) {
      const dist = CENTER_LATLNG.distanceTo(e.latlng);
      if (dist >= MAP_COVERAGE_RADIUS * 0.95) {
        setError('O ponto que clicaste encontra-se fora da zona de cobertura atual do CityFlow.');
        return;
      }

      setError(null);

      // 3o clique limpa tudo
      if (startCoords && endCoords) {
        setStartCoords(null);
        setEndCoords(null);
        setRouteGeometry([]);
        return;
      }

      // Validar e fazer snap do ponto para a estrada valida mais proxima
      setIsSnapping(true);
      try {
        const response = await axios.post('http://localhost:8000/api/v1/snap-point', {
          coords: [e.latlng.lat, e.latlng.lng]
        });

        if (response.data && response.data.snapped_coords) {
          const snapped = response.data.snapped_coords;
          if (!startCoords) {
            setStartCoords(snapped);
          } else if (!endCoords) {
            setEndCoords(snapped);
          }
        }
      } catch (err) {
        if (err.response && err.response.status === 422) {
          setError(err.response.data.detail || 'Ponto invalido. Clique mais perto de uma rua acessivel.');
        } else {
          setError('Erro ao validar o ponto no servidor.');
        }
      } finally {
        setIsSnapping(false);
      }
    }
  });

  return null;
}

export default function App() {
  
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleCalculateRoute = async () => {
    if (!startCoords || !endCoords) {
      setError('Por favor clica no mapa para selecionar a Partida e a Chegada.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setRouteGeometry([]);
    setRouteDistance(0);
    setMaxRouteIncline(0);

    try {
      const payload = {
        start_coords: startCoords,
        end_coords: endCoords,
        profile: {
          profile_name: "custom_user",
          max_incline: maxIncline / 100.0,
          min_width: parseFloat(minWidth),
          avoid_stairs: avoidStairs,
          surface_preference: ["paved", "asphalt", "concrete"]
        }
      };

      const response = await axios.post('http://localhost:8000/api/v1/route', payload);
      
      if (response.data && response.data.route_geometry) {
        setRouteGeometry(response.data.route_geometry);
        setRouteDistance(response.data.distance_meters || 0);
        setMaxRouteIncline(response.data.max_route_incline || 0);
      }
      
    } catch (err) {
      if (err.response && err.response.status === 424) {
        setError(`A rota é impossível com as restrições atuais (max inclinação: ${maxIncline}%, larg. mínima: ${minWidth}m).`);
      } else {
        setError('Ocorreu um erro inesperado ao comunicar com o servidor.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-screen h-screen flex overflow-hidden bg-slate-50 font-sans text-slate-800">
      
      {}
      <button 
        className="md:hidden fixed z-[60] bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-2xl transition-transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2 font-bold"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        aria-label="Toggle menu"
      >
        {isSidebarOpen ? <X size={24} /> : (
          <>
            <Menu size={24} />
            <span className="hidden sm:inline">Definições</span>
          </>
        )}
      </button>

      {}
      {isSidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[40] animate-in fade-in transition-opacity" 
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {}
      <aside className={`fixed md:relative top-0 left-0 h-full bg-white border-r border-slate-200 shadow-2xl md:shadow-xl z-50 flex flex-col shrink-0 w-[90%] max-w-[400px] md:w-[35%] lg:w-[30%] md:min-w-[320px] md:max-w-[450px] transform transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        
        <div className="flex-1 overflow-y-auto p-6 md:p-8 flex flex-col gap-8">
          
          {}
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 p-3 rounded-2xl shrink-0 text-blue-600">
              <MapIcon size={32} />
            </div>
            <div className="flex flex-col">
              <h1 className="text-3xl font-black text-slate-800 tracking-tight leading-none mb-1">
                CityFlow
              </h1>
              <p className="text-blue-600 font-bold tracking-wide">
                Vila Real
              </p>
            </div>
          </div>

          <div className="border-t border-slate-100" />

          {}
          <div className="flex flex-col gap-2">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <RouteIcon className="text-slate-400" size={20} /> O Seu Trajeto
            </h2>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-sm space-y-3">
               <div className="flex items-center gap-3">
                  <Navigation className={`w-5 h-5 shrink-0 ${startCoords ? 'text-blue-600' : 'text-slate-300'}`} />
                  <span className={startCoords ? 'font-semibold text-slate-700' : 'text-slate-400 italic'}>
                    {startCoords ? `Origem definida` : 'Clique no mapa p/ Origem'}
                  </span>
               </div>
               <div className="flex items-center gap-3">
                  <Goal className={`w-5 h-5 shrink-0 ${endCoords ? 'text-red-500' : 'text-slate-300'}`} />
                  <span className={endCoords ? 'font-semibold text-slate-700' : 'text-slate-400 italic'}>
                    {endCoords ? `Destino definido` : 'Clique no mapa p/ Destino'}
                  </span>
               </div>
            </div>
          </div>

          {}
          <div className="flex flex-col gap-5">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <ShieldCheck className="text-slate-400" size={20} /> O Teu Perfil de Acessibilidade
            </h2>
            
            <div className="flex flex-col gap-6 bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
              
              {}
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label htmlFor="incline-slider" className="font-semibold text-slate-700 text-sm">Máxima Inclinação</label>
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
                
                {}
                <div className="flex justify-between text-xs font-semibold mt-1">
                   <span className={maxIncline <= 5 ? "text-emerald-600 font-bold" : "text-slate-400"}>
                     {maxIncline <= 5 ? "Suave / Muito Acessível" : ""}
                   </span>
                   <span className={maxIncline > 5 && maxIncline <= 11 ? "text-blue-600 font-bold" : "text-slate-400"}>
                     {maxIncline > 5 && maxIncline <= 11 ? "Padrão (Norma Técnica)" : ""}
                   </span>
                   <span className={maxIncline >= 12 ? "text-red-500 font-bold" : "text-slate-400"}>
                     {maxIncline >= 12 ? "Apenas Especialistas / Requer Esforço" : ""}
                   </span>
                </div>
              </div>

              {}
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label htmlFor="width-slider" className="font-semibold text-slate-700 text-sm">Largura da Via (mín)</label>
                  <span className="font-bold text-blue-600 text-sm bg-blue-50 px-2 rounded-md">{minWidth}m</span>
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

              {}
              <label className="flex items-center justify-between cursor-pointer group">
                <span className="font-semibold text-slate-700 text-sm group-hover:text-blue-700 transition-colors">Evitar Escadas Subtis</span>
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

          {}
          {error && (
            <div role="alert" className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200 flex flex-col gap-2 animate-in fade-in">
               <div className="flex items-center gap-2 font-bold text-sm">
                 <AlertCircle className="w-5 h-5" />
                 Alerta de Acessibilidade
               </div>
              <p className="text-sm font-medium leading-relaxed">{error}</p>
            </div>
          )}

        </div>

         {}
         <div className="p-6 border-t border-slate-200 bg-slate-50 flex flex-col gap-4">
           <button
             type="button"
             onClick={handleCalculateRoute}
             disabled={isLoading || !startCoords || !endCoords}
             className="w-full flex items-center justify-center px-6 py-4 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl transition-all shadow-lg focus:outline-none focus:ring-4 focus:ring-slate-300 disabled:opacity-50 disabled:cursor-not-allowed group"
           >
             {isLoading ? (
               <><Loader2 className="animate-spin mr-3 w-5 h-5" />A Calcular...</>
             ) : (
               <span className="group-hover:scale-105 transition-transform">Calcular Rota Segura</span>
             )}
           </button>
           
           {}
           {routeDistance > 0 && !error && (
              <div className="flex flex-col gap-3 animate-in slide-in-from-bottom-2">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex justify-around items-center">
                   <div className="flex flex-col items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Distância</span>
                      <span className="text-lg font-black text-slate-700">{(routeDistance / 1000).toFixed(2)} <span className="text-sm font-semibold">km</span></span>
                   </div>
                   <div className="w-px h-10 bg-slate-100"></div>
                   <div className="flex flex-col items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Tempo Est.</span>
                      <span className="text-lg font-black text-blue-600">
                        {Math.ceil(routeDistance / ((maxIncline < 10 && minWidth > 0.8) ? 58.3 : 41.6))} <span className="text-sm font-semibold">min</span>
                      </span>
                   </div>
                   <div className="w-px h-10 bg-slate-100"></div>
                   <div className="flex flex-col items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Inclinação Crítica</span>
                      <span className={`text-lg font-black ${(maxRouteIncline * 100) > maxIncline ? 'text-red-600' : 'text-emerald-600'}`}>
                        {(maxRouteIncline * 100).toFixed(1)} <span className="text-sm font-semibold">%</span>
                      </span>
                   </div>
                </div>

                {}
                {(maxRouteIncline * 100) > maxIncline ? (
                  <div className="flex items-center justify-center gap-2 text-red-700 bg-red-50 p-3 rounded-xl border border-red-200 text-sm font-bold animate-in zoom-in-95">
                     <AlertTriangle className="w-5 h-5 shrink-0" />
                     <span>Atenção: Excede o teu limite de conforto.</span>
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
             O 3º clique no mapa limpa a simulação.
           </p>
         </div>

      </aside>

      {}
      <main className="flex-1 w-full relative z-0">
        {isSnapping && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-white/90 backdrop-blur px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-sm font-semibold text-slate-700">
            <Loader2 className="animate-spin w-4 h-4" />
            A validar ponto...
          </div>
        )}
        <MapContainer 
          center={CENTER_COORDS} 
          zoom={15} 
          style={{ height: '100%', width: '100%' }}
          maxBounds={MAX_BOUNDS}
          maxBoundsViscosity={1.0}
          minZoom={14}
          zoomControl={false} 
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <InteractiveMap
             startCoords={startCoords} setStartCoords={setStartCoords}
             endCoords={endCoords} setEndCoords={setEndCoords}
             setRouteGeometry={setRouteGeometry}
             setError={setError}
             setIsSnapping={setIsSnapping}
          />

          {startCoords && <Marker position={startCoords} icon={startMarkerIcon} />}
          {endCoords && <Marker position={endCoords} icon={endMarkerIcon} />}
          
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
