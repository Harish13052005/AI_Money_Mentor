import 'react-native-gesture-handler';
import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import DashboardScreen from './screens/DashboardScreen';
import NewRecordScreen from './screens/NewRecordScreen';
import RecordDetailScreen from './screens/RecordDetailScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  const [initialRoute, setInitialRoute] = useState(null);

  useEffect(() => {
    checkLoginStatus();
  }, []);

  const checkLoginStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      setInitialRoute(token ? 'Dashboard' : 'Login');
    } catch (e) {
      setInitialRoute('Login');
    }
  };

  if (!initialRoute) {
    return null;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: true,
          animationEnabled: true,
        }}
        initialRouteName={initialRoute}
      >
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="Register"
          component={RegisterScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{ headerShown: true, title: 'Dashboard' }}
        />
        <Stack.Screen
          name="NewRecord"
          component={NewRecordScreen}
          options={{ title: 'New Record' }}
        />
        <Stack.Screen
          name="RecordDetail"
          component={RecordDetailScreen}
          options={{ title: 'Record Details' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}