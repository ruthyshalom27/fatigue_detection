// App.js - React Native Entry Point
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeScreen from './src/screens/HomeScreen';
import StatsScreen from './src/screens/StatsScreen';
import { API_URL } from './src/config';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator>
        <Tab.Screen 
          name="Monitor" 
          component={HomeScreen}
          options={{ title: 'Live Monitoring' }}
        />
        <Tab.Screen 
          name="Stats" 
          component={StatsScreen}
          options={{ title: 'Statistics' }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
