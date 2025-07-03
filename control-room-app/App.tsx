import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, ScrollView } from 'react-native';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

type Metric = {
  time: number;
  pulse: number;
  temperature: number;
  sweat: number;
};

type ServerMetric = {
  user_id: string;
  heart_rate: number;
  temperature: number;
  movement_x: number;
  movement_y: number;
  movement_z: number;
  sweat_level: number;
  timestamp: string;
};

type Exception = {
  user_id: string;
  timestamp: string;
  exception_type: string;
  exception_level: string;
  details: string;
};

const METRICS_URL = 'http://51.17.183.152:3000/metrics/last/1';
const EXCEPTION_URL = 'http://51.17.183.152:3000/test';

export default function App() {
  const [dataHistory, setDataHistory] = useState<Metric[]>([]);
  const [serverHistory, setServerHistory] = useState<ServerMetric[]>([]);
  const [latest, setLatest] = useState<ServerMetric | null>(null);
  const [exception, setException] = useState<Exception | null>(null);
  const [isSilenced, setIsSilenced] = useState(false);
  const [panicMode, setPanicMode] = useState(false);
  const silenceTime = useRef<number | null>(null);
  const lastExceptionDate = useRef<string>('2025-01-01T00:00:00');
  const silenceLockUntil = useRef<number | null>(null);
  const userFirstSeenAt = useRef<{ [key: string]: number }>({});


  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(METRICS_URL);
        if (response.ok) {
          const data: ServerMetric = await response.json();
          setLatest(data);
          setServerHistory(prev => [...prev, data].slice(-300));
    
          if (!userFirstSeenAt.current[data.user_id]) {
               userFirstSeenAt.current[data.user_id] = Date.now(); // נרשם זמן כניסה של חייל חדש
              }


          // שמירה של עד 10 דקות אחרונות (300 נקודות × 2 שניות)
          setDataHistory(prev => {
            const entry = {
             time: new Date(data.timestamp).getTime(),
              pulse: data.heart_rate,
              temperature: data.temperature,
             sweat: data.sweat_level,
            };
           const trimmed = [...prev, entry].slice(-300);

            const localEx = analyzeMetrics(trimmed);
//             const advancedEx = analyzeAdvancedMetrics([...serverHistory, data].slice(-150));
//             if (advancedEx) {
//                 setException(advancedEx);
//                 setIsSilenced(false);
//                 silenceTime.current = null;
// }

            if (localEx) {
              setException(localEx);
              setIsSilenced(false);
              silenceTime.current = null;
            }

            return trimmed;
        });

        }
      } catch (err) {
        console.error('Metrics error:', err);
      }

      try {
        const res = await fetch(`${EXCEPTION_URL}?date_str=${lastExceptionDate.current}`);
        const data = await res.json();
        const now = Date.now();

        if (data && data.new_data && data.new_data.user_id === latest?.user_id) {
          const newTimestamp = data.new_data.timestamp;

          if (isSilenced && silenceTime.current && now - silenceTime.current > 10000) {
            lastExceptionDate.current = newTimestamp;
            setException(data.new_data);
            setIsSilenced(false);
            silenceTime.current = null;
          } else if (!isSilenced) {
            lastExceptionDate.current = newTimestamp;
            setException(data.new_data);
          }
        } else if (isSilenced && silenceTime.current && now - silenceTime.current > 15000) {
          setException(null);
        }
      } catch (err) {
        console.error('Exception error:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [latest?.user_id]);

  const handleSilence = () => {
    if (panicMode) {
      setPanicMode(false);
      if (!exception || exception.exception_type === 'Panic Button') {
        setException(null);
      }
    } else {
      setIsSilenced(true);
      silenceTime.current = Date.now();
    }
  };

  const handlePanic = () => {
    setPanicMode(true);
    setException({
      user_id: latest?.user_id ?? '',
      timestamp: new Date().toISOString(),
      exception_type: 'Panic Button',
      exception_level: 'red',
      details: 'Soldier pressed panic button',
    });
    setIsSilenced(false);
    silenceTime.current = null;
  };

  const getCardStyle = () => {
    if (panicMode) return styles.red;
    if (isSilenced) return styles.gray;
    if (exception?.exception_level === 'red') return styles.red;
    if (exception?.exception_level === 'yellow') return styles.yellow;
    return styles.green;
  };

  const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { minute: '2-digit', second: '2-digit' });
  };

  return (
    <View style={styles.container}>
      <View style={styles.logoTopRight}>
        <TouchableOpacity onPress={handlePanic} activeOpacity={1}>
          <Image
            source={require('./assets/logo-transparent.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </TouchableOpacity>
      </View>

      <ScrollView>
        <Text style={styles.title}>Soldier Monitoring Dashboard</Text>

        {latest ? (
          <View style={[styles.card, getCardStyle()]}>
            <Text style={styles.name}>User ID: {latest.user_id}</Text>
            <Text style={styles.row}>
              Timestamp: {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}
            </Text>

            {exception ? (
              <>
                <Text style={styles.name}>Exception Type: {exception.exception_type}</Text>
                <Text style={styles.name}>Exception Level: {exception.exception_level}</Text>
                <Text style={styles.name}>Details: {exception.details}</Text>
              </>
            ) : (
              <Text style={styles.name}>Status: Normal</Text>
            )}

            <Text style={styles.row}>
              💓 Pulse: {latest.heart_rate}   🌡️ Temp: {latest.temperature}°C   💧 Sweat: {Math.round(latest.sweat_level)}%
            </Text>

            {(exception || panicMode) && !isSilenced && (
              <TouchableOpacity onPress={handleSilence} style={styles.button}>
                <Text style={styles.buttonText}>He's Okay now</Text>
              </TouchableOpacity>
            )}

            <View style={styles.graphSection}>
              <Text style={styles.graphTitle}>Pulse</Text>
              <ResponsiveContainer width="100%" height={100}>
                <LineChart data={dataHistory}>
                  <XAxis dataKey="time" tickFormatter={formatTime} stroke="#aaa" fontSize={10} />
                  <YAxis stroke="#aaa" />
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <Tooltip labelFormatter={formatTime} />
                  <Line type="monotone" dataKey="pulse" stroke="#ff6666" dot={false} />
                </LineChart>
              </ResponsiveContainer>

              <Text style={styles.graphTitle}>Temperature</Text>
              <ResponsiveContainer width="100%" height={100}>
                <LineChart data={dataHistory}>
                  <XAxis dataKey="time" tickFormatter={formatTime} stroke="#aaa" fontSize={10} />
                  <YAxis stroke="#aaa" />
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <Tooltip labelFormatter={formatTime} />
                  <Line type="monotone" dataKey="temperature" stroke="#66ccff" dot={false} />
                </LineChart>
              </ResponsiveContainer>

              <Text style={styles.graphTitle}>Sweat Level</Text>
              <ResponsiveContainer width="100%" height={100}>
                <LineChart data={dataHistory}>
                  <XAxis dataKey="time" tickFormatter={formatTime} stroke="#aaa" fontSize={10} />
                  <YAxis stroke="#aaa" />
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <Tooltip labelFormatter={formatTime} />
                  <Line type="monotone" dataKey="sweat" stroke="#00cc99" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </View>
          </View>
        ) : (
          <Text style={styles.noData}>Waiting for soldier data...</Text>
        )}
      </ScrollView>
    </View>
  );
}
function durationAbove(history: Metric[], field: keyof Metric, threshold: number, ms: number, below = false) {
  const now = Date.now();
  return history.filter(m => now - m.time <= ms && (below ? m[field] < threshold : m[field] > threshold)).length === Math.floor(ms / 2000);
}

function recentTrend(history: Metric[], field: keyof Metric, count: number) {
  const values = history.slice(-count).map(m => m[field]);
  return values.length === count ? values[count - 1] - values[0] : 0;
}


function analyzeMetrics(history: Metric[]): Exception | null {
  const latest = history[history.length - 1];
  if (!latest) return null;
  const now = new Date().toISOString();

  // דופק נמוך מאוד – ברדיקרדיה
  if (latest.pulse < 40) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Bradycardia',
      exception_level: 'red',
      details: 'Pulse below 40 BPM',
    };
  }

  // דופק גבוה במנוחה מעל 2 דקות
  if (durationAbove(history, 'pulse', 100, 120000)) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Resting Tachycardia',
      exception_level: 'yellow',
      details: 'Pulse > 100 for over 2 minutes',
    };
  }

  // דופק גבוה מדי (180+) בכל מצב
  if (latest.pulse > 180) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Extreme Pulse',
      exception_level: 'red',
      details: 'Pulse exceeded 180 BPM',
    };
  }

  // חום גבוה מאוד – מכת חום
  if (latest.temperature > 39) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Heat Stroke',
      exception_level: 'red',
      details: 'Temperature > 39°C',
    };
  }

  // חום בינוני עם דופק גבוה
  if (latest.temperature > 38.1 && latest.temperature <= 39.0 && latest.pulse > 150) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Heat Stress',
      exception_level: 'red',
      details: 'Temp 38.1–39 with high pulse >150',
    };
  }

  // חום בינוני בלבד
  if (latest.temperature > 38.1 && latest.temperature <= 39.0) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Moderate Fever',
      exception_level: 'yellow',
      details: 'Temperature between 38.1–39.0°C',
    };
  }

  // חום קל לאורך זמן
  if (durationAbove(history, 'temperature', 37.6, 600000)) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Mild Fever',
      exception_level: 'yellow',
      details: 'Slight fever > 10 minutes',
    };
  }

  // היפותרמיה קלה
  if (latest.temperature >= 35.0 && latest.temperature <= 35.4) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Mild Hypothermia',
      exception_level: 'yellow',
      details: 'Body temp between 35.0–35.4°C',
    };
  }

  // היפותרמיה חמורה
  if (latest.temperature < 35.0) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Severe Hypothermia',
      exception_level: 'red',
      details: 'Body temp < 35.0°C',
    };
  }

  // מגמת עלייה בטמפרטורה
  if (recentTrend(history, 'temperature', 15) > 0.5) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Temp Spike',
      exception_level: 'yellow',
      details: 'Temperature increased > 0.5°C in 30 sec',
    };
  }

  // עומס חום משולב
  if (latest.temperature > 38 && latest.pulse > 150 && latest.sweat > 600) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Heat Load',
      exception_level: 'red',
      details: 'Temp > 38°C, Pulse > 150, Sweat > 600',
    };
  }

  // התייבשות חמורה (ירידה בזיעה, דופק גבוה, טמפ' גבוהה)
  const pulseRising = history.length >= 5 && (history[history.length - 1].pulse - history[history.length - 5].pulse > 10);
  const sweatFalling = history.length >= 5 && (history[history.length - 5].sweat > 500 && latest.sweat < 300);
  if (pulseRising && sweatFalling && latest.temperature > 38.2) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Severe Dehydration',
      exception_level: 'red',
      details: 'Pulse↑, sweat↓, temp↑',
    };
  }

  // חשד להתייבשות
  if (
    history.length >= 5 &&
    history[history.length - 1].pulse - history[history.length - 5].pulse > 5 &&
    sweatFalling &&
    latest.temperature < 37.4
  ) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Dehydration Suspicion',
      exception_level: 'yellow',
      details: 'Small pulse↑ and sweat↓',
    };
  }

  // קפיצה חדה ברטיבות
  if (recentTrend(history, 'sweat', 3) > 250) {
    return {
      user_id: '1',
      timestamp: now,
      exception_type: 'Sudden Sweat Rise',
      exception_level: 'yellow',
      details: 'Rapid increase in sweat level',
    };
  }

  return null;
}



const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212', padding: 20, paddingTop: 60 },
  logoTopRight: {
    position: 'absolute',
    top: 10,
    right: 10,
    zIndex: 10,
  },
  logo: {
    width: 60,
    height: 60,
    opacity: 0.9,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 16,
  },
  card: {
    padding: 16,
    borderRadius: 10,
    marginBottom: 40,
    width: '90%',
    alignSelf: 'center',
  },
  red: { backgroundColor: '#5a2020', borderWidth: 2, borderColor: 'red' },
  yellow: { backgroundColor: '#665c1d', borderWidth: 2, borderColor: 'yellow' },
  green: { backgroundColor: '#2d4032', borderWidth: 2, borderColor: 'green' },
  gray: { backgroundColor: '#444', borderWidth: 2, borderColor: '#aaa' },
  row: { color: '#fff', fontSize: 15, marginTop: 6 },
  name: { fontSize: 17, fontWeight: 'bold', color: '#fff' },
  noData: { color: '#aaa', fontStyle: 'italic', textAlign: 'center', marginTop: 50 },
  button: {
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 14,
    backgroundColor: '#333',
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  buttonText: { color: '#fff', fontWeight: 'bold' },
  graphSection: { marginTop: 20 },
  graphTitle: { color: '#ccc', marginTop: 10, marginBottom: 4 },
});

