import React, { useEffect, useState } from 'react';
import { View, Text, Button, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useIsFocused } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getHistory } from '../services/api';

export default function DashboardScreen({ navigation }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const isFocused = useIsFocused();

  const loadRecords = async () => {
    setLoading(true);
    setError('');
    try {
      const token = await AsyncStorage.getItem('token');
      const r = await getHistory(token);
      setRecords(r || []);
    } catch (e) {
      setError(e.message || 'Failed to load records');
    }
    setLoading(false);
  };

  useEffect(() => {
    if (isFocused) {
      loadRecords();
    }
  }, [isFocused]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Records</Text>
        <Button title="Logout" onPress={async () => { await AsyncStorage.removeItem('token'); navigation.replace('Login'); }} />
      </View>

      <View style={styles.actionRow}>
        <Button title="New Analysis" onPress={() => navigation.navigate('NewRecord')} />
      </View>

      {loading ? <Text>Loading...</Text> : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}

      <FlatList
        data={records}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('RecordDetail', { record: item })}>
            <Text style={styles.itemText}>Record #{item.id} — {new Date(item.created_at).toLocaleString()}</Text>
            <Text>Income: {item.income} | Expenses: {item.expenses}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: 20 },
  actionRow: { marginTop: 16, marginBottom: 12 },
  item: { padding: 12, borderBottomWidth: 1, borderColor: '#eee' },
  itemText: { fontWeight: '600' },
  error: { color: 'red' }
});
