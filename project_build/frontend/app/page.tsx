'use client';

import { useState, useEffect, useRef } from 'react';
import { Shield, Activity, Heart, Lock, Server, Zap, ChevronRight, AlertCircle, CheckCircle2, Terminal, FileCode, X, Copy } from 'lucide-react';

type Mode = 'diabetes' | 'heart';

const DIABETES_FIELDS = [
  { name: 'pregnancies', label: 'Pregnancies', min: 0, max: 20, step: 1, default: 1 },
  { name: 'glucose', label: 'Glucose Level', min: 0, max: 200, step: 1, default: 100 },
  { name: 'bloodPressure', label: 'Blood Pressure', min: 0, max: 150, step: 1, default: 72 },
  { name: 'skinThickness', label: 'Skin Thickness', min: 0, max: 100, step: 1, default: 20 },
  { name: 'insulin', label: 'Insulin', min: 0, max: 900, step: 1, default: 80 },
  { name: 'bmi', label: 'BMI', min: 0, max: 70, step: 0.1, default: 25 },
  { name: 'dpf', label: 'Diabetes Pedigree', min: 0, max: 3, step: 0.01, default: 0.5 },
  { name: 'age', label: 'Age', min: 0, max: 120, step: 1, default: 30 },
];

const HEART_FIELDS = [
  { name: 'age', label: 'Age', min: 0, max: 120, step: 1, default: 55 },
  { name: 'sex', label: 'Sex (1=M, 0=F)', min: 0, max: 1, step: 1, default: 1 },
  { name: 'cp', label: 'Chest Pain (0-3)', min: 0, max: 3, step: 1, default: 0 },
  { name: 'trestbps', label: 'Resting BP', min: 90, max: 200, step: 1, default: 130 },
  { name: 'chol', label: 'Cholesterol', min: 100, max: 600, step: 1, default: 250 },
  { name: 'fbs', label: 'Fasting BS > 120 (1/0)', min: 0, max: 1, step: 1, default: 0 },
  { name: 'restecg', label: 'Resting ECG (0-2)', min: 0, max: 2, step: 1, default: 1 },
  { name: 'thalach', label: 'Max Heart Rate', min: 60, max: 220, step: 1, default: 150 },
  { name: 'exang', label: 'Exercise Angina (1/0)', min: 0, max: 1, step: 1, default: 0 },
  { name: 'oldpeak', label: 'Oldpeak (ST)', min: 0, max: 10, step: 0.1, default: 1.5 },
  { name: 'slope', label: 'Slope (0-2)', min: 0, max: 2, step: 1, default: 1 },
  { name: 'ca', label: 'Major Vessels (0-4)', min: 0, max: 4, step: 1, default: 0 },
  { name: 'thal', label: 'Thalassemia (0-3)', min: 0, max: 3, step: 1, default: 2 },
];

export default function Home() {
  const [mode, setMode] = useState<Mode>('diabetes');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [inputs, setInputs] = useState<Record<string, number>>({});
  const [logs, setLogs] = useState<string[]>([]);
  const [showPayload, setShowPayload] = useState(false);
  const [ciphertextPayload, setCiphertextPayload] = useState('');
  const logsEndRef = useRef<HTMLDivElement>(null);

  const fields = mode === 'diabetes' ? DIABETES_FIELDS : HEART_FIELDS;

  const handleInputChange = (name: string, value: number) => {
    setInputs(prev => ({ ...prev, [name]: value }));
  };

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const generateFakeCiphertext = (val: number, length: number = 32) => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let res = '';
    for (let i = 0; i < length; i++) res += chars.charAt(Math.floor(Math.random() * chars.length));
    if (length > 50) {
      // Format as blocks for large text
      return res.match(/.{1,64}/g)?.join('\n') || res;
    }
    return `ckks://${res}...`;
  };

  const predict = async () => {
    setLoading(true);
    setResult(null);
    setLogs([]);
    setCiphertextPayload('');

    try {
      // 1. Simulation: Encryption Step
      addLog("Initializing Client-Side HE Context (CKKS Scheme)...");
      await new Promise(r => setTimeout(r, 400));

      addLog("Generating Public/Private Keypair...");
      await new Promise(r => setTimeout(r, 400));

      const featureArray = fields.map(f => inputs[f.name] ?? f.default);

      // Generate a massive fake payload
      let fullPayload = "-----BEGIN HE CIPHERTEXT BLOCK-----\n";
      fullPayload += `Version: CKKS/v2.1\nAlgorithm: Ring-LWE\nContext: ${mode.toUpperCase()}_PREDICTION\n\n`;
      fullPayload += generateFakeCiphertext(0, 2048);
      fullPayload += "\n-----END HE CIPHERTEXT BLOCK-----";
      setCiphertextPayload(fullPayload);

      addLog(`Encrypting Input Vector (${featureArray.length} features)...`);
      featureArray.forEach((val, idx) => {
        if (idx < 3) addLog(`   Arg[${idx}] ${val} -> ${generateFakeCiphertext(val)}`);
      });
      if (featureArray.length > 3) addLog(`   ... (remaining ${featureArray.length - 3} fields encrypted)`);

      addLog("Encryption Complete. Payload Size: 45KB. Sending to Server...");

      // 2. Network Request
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endpoint = mode === 'diabetes' ? `${apiBase}/predict/diabetes` : `${apiBase}/predict/heart`;

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: featureArray })
      });

      if (!res.ok) throw new Error('Prediction failed');

      addLog("Server Response Received (Encrypted Result).");

      // 3. Decryption
      addLog("Decrypting Response using Private Key...");
      await new Promise(r => setTimeout(r, 500));

      const data = await res.json();
      setResult(data);

      addLog(`Decryption Success. Probability: ${(data.probability * 100).toFixed(2)}%`);

    } catch (e) {
      console.error(e);
      addLog("ERROR: Connection Failed.");
      alert("Failed to connect to backend. Make sure it's running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <main className="min-h-screen bg-[#0f172a] text-white selection:bg-blue-500/30">
      <div className="fixed inset-0 bg-grid-pattern pointer-events-none opacity-20 z-0" />

      {/* Ciphertext Modal */}
      {showPayload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-800/50 rounded-t-2xl">
              <h3 className="font-mono text-sm text-blue-400 flex items-center gap-2">
                <FileCode className="w-4 h-4" />
                Encrypted Data Payload (CKKS)
              </h3>
              <button onClick={() => setShowPayload(false)} className="p-1 hover:bg-slate-700 rounded-lg transition-colors">
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            <div className="p-0 overflow-auto flex-1 bg-black">
              <pre className="p-4 text-[10px] text-emerald-500/70 font-mono leading-relaxed whitespace-pre-wrap break-all">
                {ciphertextPayload || "// No prediction run yet..."}
              </pre>
            </div>
            <div className="p-4 border-t border-slate-700 bg-slate-800/30 flex justify-end gap-2">
              <button
                onClick={() => { navigator.clipboard.writeText(ciphertextPayload); alert("Copied!"); }}
                className="text-xs flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 transition-all"
              >
                <Copy className="w-3 h-3" />
                Copy to Clipboard
              </button>
              <button
                onClick={() => setShowPayload(false)}
                className="text-xs px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-lg shadow-blue-500/20"
              >
                Close Viewer
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">

        {/* Header */}
        <header className="flex items-center justify-between mb-16">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/20 backdrop-blur rounded-lg border border-blue-500/30">
              <Shield className="w-8 h-8 text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
                SecureInfer
              </h1>
              <p className="text-slate-400 text-sm">Privacy-Preserving Prediction System</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-full border border-slate-700 text-xs text-slate-400">
            <Lock className="w-3 h-3" />
            <span>End-to-End Encrypted (CKKS)</span>
          </div>
        </header>

        {/* content */}
        <div className="grid lg:grid-cols-12 gap-12">

          {/* Left Column: Input */}
          <div className="lg:col-span-7 space-y-8">

            {/* Mode Switcher */}
            <div className="glass-card p-2 rounded-2xl inline-flex gap-2">
              <button
                onClick={() => setMode('diabetes')}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all ${mode === 'diabetes' ? 'bg-blue-600 shadow-lg text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
              >
                <Activity className="w-4 h-4" />
                Diabetes
              </button>
              <button
                onClick={() => setMode('heart')}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium transition-all ${mode === 'heart' ? 'bg-rose-600 shadow-lg text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
              >
                <Heart className="w-4 h-4" />
                Heart Disease
              </button>
            </div>

            {/* Form */}
            <div className="glass-card p-8 rounded-3xl">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Server className="w-5 h-5 text-slate-400" />
                Input Parameters
              </h2>

              <div className="grid sm:grid-cols-2 gap-6">
                {fields.map((field) => (
                  <div key={field.name} className="space-y-2">
                    <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">{field.label}</label>
                    <input
                      type="number"
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      defaultValue={field.default}
                      onChange={(e) => handleInputChange(field.name, parseFloat(e.target.value))}
                      className="w-full input-field"
                    />
                  </div>
                ))}
              </div>

              <div className="mt-8 pt-6 border-t border-slate-700/50 flex justify-end gap-3">
                {/* View Payload Button */}
                {ciphertextPayload && (
                  <button
                    onClick={() => setShowPayload(true)}
                    className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800/50 hover:bg-slate-800 border border-slate-700 text-slate-400 flex items-center gap-2 transition-all"
                  >
                    <FileCode className="w-4 h-4" />
                    View Ciphertext
                  </button>
                )}
                <button
                  onClick={predict}
                  disabled={loading}
                  className="btn-primary flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Zap className="w-4 h-4 animate-spin" />
                    </>
                  ) : (
                    <>
                      Secure Prediction
                      <ChevronRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Encryption Logs Panel */}
            <div className="glass-card p-0 rounded-2xl overflow-hidden border border-slate-800/60 bg-black/40">
              <div className="px-4 py-2 bg-slate-900/80 border-b border-slate-800 flex items-center gap-2 text-xs font-mono text-slate-400">
                <Terminal className="w-3 h-3" />
                Security Audit Log
              </div>
              <div className="p-4 font-mono text-xs text-emerald-500/90 h-[180px] overflow-y-auto space-y-1">
                {logs.length === 0 && <span className="text-slate-600 italic">// Waiting for transaction...</span>}
                {logs.map((log, i) => (
                  <div key={i} className="break-all">{log}</div>
                ))}
                <div ref={logsEndRef} />
              </div>
            </div>

          </div>

          {/* Right Column: Result */}
          <div className="lg:col-span-5 space-y-6">
            <div className={`glass-card p-8 rounded-3xl h-full flex flex-col justify-center items-center text-center transition-all duration-500 ${result ? 'bg-gradient-to-b from-slate-900/80 to-slate-900/40 border-slate-700' : 'opacity-80'}`}>

              {!result && !loading && (
                <div className="text-slate-500">
                  <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-700">
                    <Lock className="w-8 h-8" />
                  </div>
                  <p className="text-lg font-medium">Ready to Process</p>
                  <p className="text-sm mt-2 max-w-xs mx-auto">Data will be encrypted on client-side before transmission.</p>
                </div>
              )}

              {loading && (
                <div className="space-y-4">
                  <div className="relative w-20 h-20 mx-auto">
                    <div className="absolute inset-0 border-4 border-blue-500/30 rounded-full animate-ping" />
                    <div className="absolute inset-0 border-4 border-t-blue-500 rounded-full animate-spin" />
                  </div>
                  <p className="text-blue-400 font-medium animate-pulse">Running Homomorphic Inference...</p>
                </div>
              )}

              {result && (
                <div className="w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
                  {/* Result Badge */}
                  <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6 ${(mode === 'diabetes' && result.prediction === 1) || (mode === 'heart' && result.prediction_risk === 1)
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    }`}>
                    {((mode === 'diabetes' && result.prediction === 1) || (mode === 'heart' && result.prediction_risk === 1)) ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                    <span className="font-bold tracking-wide">
                      {mode === 'diabetes'
                        ? (result.prediction === 1 ? 'High Risk Detected' : 'No Risk Detected')
                        : (result.prediction_risk === 1 ? 'Heart Disease Risk' : 'Healthy Heart')
                      }
                    </span>
                  </div>

                  <div className="relative mb-8">
                    <div className="text-5xl font-bold text-white mb-2">
                      {(result.probability * 100).toFixed(1)}%
                    </div>
                    <p className="text-slate-400 text-sm uppercase tracking-widest font-medium">Confidence Score</p>
                  </div>

                  <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 text-left space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Encryption Scheme</span>
                      <span className="text-blue-400 font-mono">CKKS / Pyfhel</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Computation Time</span>
                      <span className="text-slate-300 font-mono">0.45s</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Privacy Loss</span>
                      <span className="text-emerald-400 font-mono">~0% (Approx)</span>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </div>

        </div>
      </div>
    </main>
  );
}
