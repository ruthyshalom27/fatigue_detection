// src/screens/HomeScreen.js - Main monitoring screen
import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Image, ActivityIndicator } from 'react-native';
import { STATS_ENDPOINT, POLL_INTERVAL, VIDEO_STREAM_URL } from '../config';

export default function HomeScreen() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const pollStats = async () => {
      try {
        const response = await fetch(STATS_ENDPOINT);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        setStats(data);
        setLoading(false);
        setError(null);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    const interval = setInterval(pollStats, POLL_INTERVAL);
    pollStats(); // Initial fetch

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#00d4ff" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Error: {error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Image 
        source={{ uri: VIDEO_STREAM_URL }} 
        style={styles.videoStream}
      />
      <View style={styles.statsContainer}>
        <StatCard label="Status" value={stats?.status || '--'} />
        <StatCard label="Fatigue" value={`${stats?.fatigue_score || 0}%`} />
        <StatCard label="EAR" value={(stats?.ear || 0).toFixed(3)} />
        <StatCard label="Blinks/min" value={(stats?.blink_rate || 0).toFixed(1)} />
      </View>
    </View>
  );
}

function StatCard({ label, value }) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050a10',
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#050a10',
  },
  videoStream: {
    width: '100%',
    height: 300,
    backgroundColor: '#000',
    borderRadius: 8,
    marginBottom: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 8,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#0b1420',
    padding: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#1a3a5c',
  },
  statLabel: {
    fontSize: 12,
    color: '#4a7090',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 20,
    color: '#00d4ff',
    fontWeight: 'bold',
  },
  errorText: {
    color: '#ff3366',
    fontSize: 16,
  },
});
