// src/screens/StatsScreen.js - Detailed statistics
import React, { useState, useEffect } from 'react';
import { View, ScrollView, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { STATS_ENDPOINT, POLL_INTERVAL } from '../config';

export default function StatsScreen() {
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
    pollStats();

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
    <ScrollView style={styles.container}>
      <MetricRow label="Status" value={stats?.status} />
      <MetricRow label="Fatigue Score" value={`${stats?.fatigue_score}%`} />
      <MetricRow label="Eye Aspect Ratio" value={(stats?.ear || 0).toFixed(3)} />
      <MetricRow label="Blink Rate (per min)" value={(stats?.blink_rate || 0).toFixed(1)} />
      <MetricRow label="Total Blinks" value={stats?.blink_count} />
      <MetricRow label="Closed Frames" value={stats?.closed_frames} />
      <MetricRow label="Face Detected" value={stats?.face_detected ? 'Yes' : 'No'} />
    </ScrollView>
  );
}

function MetricRow({ label, value }) {
  return (
    <View style={styles.metricRow}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
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
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 12,
    marginBottom: 8,
    backgroundColor: '#0b1420',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#1a3a5c',
  },
  metricLabel: {
    fontSize: 14,
    color: '#4a7090',
  },
  metricValue: {
    fontSize: 16,
    color: '#00d4ff',
    fontWeight: 'bold',
  },
  errorText: {
    color: '#ff3366',
    fontSize: 16,
  },
});
