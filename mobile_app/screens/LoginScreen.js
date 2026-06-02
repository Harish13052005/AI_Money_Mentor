import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { login } from '../services/api';

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setError('');
    try {
      const token = await login(username, password);
      if (token) navigation.replace('Dashboard');
    } catch (e) {
      setError(e.message || 'Login failed');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AI Money Mentor</Text>
      <TextInput placeholder="Username" value={username} onChangeText={setUsername} style={styles.input} />
      <TextInput placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry style={styles.input} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title="Login" onPress={handleSubmit} />
      <View style={{ height: 10 }} />
      <Button title="Register" onPress={() => navigation.navigate('Register')} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 16 },
  title: { fontSize: 24, marginBottom: 16, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 8, marginBottom: 12, borderRadius: 4 },
  error: { color: 'red', marginBottom: 8 }
});
