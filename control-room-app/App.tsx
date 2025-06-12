import React, { useEffect, useState, useRef } from 'react';
import { View, Text, FlatList, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Define soldier and history
type Soldier = {
  id: string;
  name: string;
  pulse: number;
  temperature: number;
  sweatLevel: number;
  movement: string;
  risk: string;
  dangerLevel: number;
};

type DataPoint = { time: number; pulse: number; temperature: number; sweat: number };
type HistoryMap = Record<string, DataPoint[]>;

const INITIAL_DATA: Soldier[] = [
  { id: '1', name: 'Roy Levi', pulse: 80, temperature: 36.9, sweatLevel: 60, movement: 'Still', risk: 'Normal', dangerLevel: 0 },
  { id: '2', name: 'Danny Cohen', pulse: 110, temperature: 38.6, sweatLevel: 10, movement: 'Moving', risk: 'Heat Stroke', dangerLevel: 2 },
  { id: '3', name: 'Yoav Zur', pulse: 100, temperature: 37.5, sweatLevel: 30, movement: 'Still', risk: 'Extreme Fatigue', dangerLevel: 1 },
];

export default function App() {
  const [soldiers, setSoldiers] = useState<Soldier[]>(INITIAL_DATA);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const lastAlerted = useRef<Set<string>>(new Set());
  const [historyMap, setHistoryMap] = useState<HistoryMap>({});

  const playBeep = () => {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1000, ctx.currentTime);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.2);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setSoldiers(prev => {
        return prev.map(s => {
          const newPulse = Math.round(s.pulse + (Math.random() * 6 - 3));
          const newTemp = parseFloat((s.temperature + (Math.random() * 0.4 - 0.2)).toFixed(1));
          const newSweat = Math.max(0, Math.min(100, s.sweatLevel + Math.random() * 10 - 5));
          const newMove = Math.random() > 0.7 ? 'Moving' : 'Still';

          let newRisk = 'Normal';
          let newDanger = 0;

          if (newTemp > 38.5 && newSweat < 20) {
            newRisk = 'Heat Stroke'; newDanger = 2;
          } else if (newTemp < 35.0) {
            newRisk = 'Hypothermia'; newDanger = 2;
          } else if (newPulse > 120 && newSweat < 25) {
            newRisk = 'Pre Heart Attack'; newDanger = 2;
          } else if (newPulse > 105 && newTemp > 37.5 && newSweat < 30) {
            newRisk = 'Physical Overload'; newDanger = 1;
          } else if (newPulse > 110 && newMove === 'Still') {
            newRisk = 'Pre Fainting'; newDanger = 1;
          } else if (newPulse > 95 && newSweat > 85) {
            newRisk = 'Panic Attack'; newDanger = 1;
          }

          if (newDanger === 2 && !lastAlerted.current.has(s.id)) {
            playBeep();
            lastAlerted.current.add(s.id);
          } else if (newDanger < 2 && lastAlerted.current.has(s.id)) {
            lastAlerted.current.delete(s.id);
          }

          setHistoryMap(prevHist => {
            const updated = { ...prevHist };
            if (!updated[s.id]) updated[s.id] = [];
            updated[s.id].push({ time: now, pulse: newPulse, temperature: newTemp, sweat: newSweat });
            if (updated[s.id].length > 30) updated[s.id] = updated[s.id].slice(-30);
            return updated;
          });

          return { ...s, pulse: newPulse, temperature: newTemp, sweatLevel: newSweat, movement: newMove, risk: newRisk, dangerLevel: newDanger };
        }).sort((a, b) => b.dangerLevel - a.dangerLevel);
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
  };

  const renderItem = ({ item }: { item: Soldier }) => (
    <TouchableOpacity onPress={() => toggleExpand(item.id)}>
      <View style={[styles.card, dangerStyles[item.dangerLevel], item.dangerLevel === 2 && styles.alert]}>        
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.rowText}>
          💓 {item.pulse} BPM   🌡️ {item.temperature}°C   💧 {Math.round(item.sweatLevel)}%   🧭 {item.movement}   ⚠️ {item.risk}
        </Text>
        {expandedId === item.id && (
          <View style={styles.details}>
            <Text style={styles.detailsText}>Pulse:</Text>
            <ResponsiveContainer width="100%" height={100}>
              <LineChart data={historyMap[item.id] || []}>
                <XAxis dataKey="time" tickFormatter={formatTime} stroke="#aaa" fontSize={10} />
                <YAxis stroke="#aaa" domain={['auto', 'auto']} />
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <Tooltip labelFormatter={formatTime} />
                <Line type="monotone" dataKey="pulse" stroke="#ff6666" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <Text style={styles.detailsText}>Temperature:</Text>
            <ResponsiveContainer width="100%" height={100}>
              <LineChart data={historyMap[item.id] || []}>
                <XAxis dataKey="time" tickFormatter={formatTime} stroke="#aaa" fontSize={10} />
                <YAxis stroke="#aaa" domain={['auto', 'auto']} />
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <Tooltip labelFormatter={formatTime} />
                <Line type="monotone" dataKey="temperature" stroke="#66ccff" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <Text style={styles.detailsText}>Sweat Level:</Text>
            <ResponsiveContainer width="100%" height={100}>
              <LineChart data={historyMap[item.id] || []}>
                <XAxis dataKey="time" tickFormatter={formatTime} stroke="#aaa" fontSize={10} />
                <YAxis stroke="#aaa" domain={['auto', 'auto']} />
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <Tooltip labelFormatter={formatTime} />
                <Line type="monotone" dataKey="sweat" stroke="#00cc99" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={soldiers}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        ListHeaderComponent={<Text style={styles.title}>Soldier Monitoring Dashboard</Text>}
      />
      <Image source={require('./assets/logo-transparent.png')} style={styles.logo} />
    </View>
  );
}

const dangerStyles = [
  { backgroundColor: '#2d4032' },
  { backgroundColor: '#665c1d' },
  { backgroundColor: '#5a2020' },
];

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
    paddingHorizontal: 20,
    paddingTop: 40,
  },
  logo: {
    width: 200,
    height: 200,
    position: 'absolute',
    bottom: 20,
    left: 20,
    opacity: 0.6,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 16,
  },
  card: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    marginBottom: 8,
    borderRadius: 12,
  },
  alert: {
    borderWidth: 2,
    borderColor: 'red',
  },
  rowText: {
    color: '#fff',
    fontSize: 13,
    marginTop: 4,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  details: {
    marginTop: 8,
    padding: 10,
    backgroundColor: '#1e1e1e',
    borderRadius: 8,
  },
  detailsText: {
    color: '#ccc',
    fontSize: 13,
    marginBottom: 4,
  },
});
