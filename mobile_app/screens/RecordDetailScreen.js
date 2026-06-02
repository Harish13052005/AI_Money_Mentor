import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { updateRecord } from '../services/api';

export default function RecordDetailScreen({ route, navigation }) {
  const { record } = route.params;
  const [income, setIncome] = useState(String(record.income || ''));
  const [expenses, setExpenses] = useState(String(record.expenses || ''));
  const [savings, setSavings] = useState(String(record.savings || ''));
  const [message, setMessage] = useState('');

  const handleSave = async () => {
    setMessage('');
    try {
      const payload = {
        income: parseFloat(income),
        expenses: parseFloat(expenses),
        savings: parseFloat(savings),
        investments: record.investments || [],
        goals: record.goals || []
      };
      const token = await AsyncStorage.getItem('token');
      await updateRecord(token, record.id, payload);
      setMessage('Saved successfully');
    } catch (e) {
      setMessage(e.message || 'Save failed');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Button title="Back" onPress={() => navigation.goBack()} />
      <Text style={styles.title}>Record #{record.id}</Text>
      <Text>Created: {new Date(record.created_at).toLocaleString()}</Text>

      <Text style={styles.label}>Income</Text>
      <TextInput style={styles.input} value={income} onChangeText={setIncome} keyboardType="numeric" />

      <Text style={styles.label}>Expenses</Text>
      <TextInput style={styles.input} value={expenses} onChangeText={setExpenses} keyboardType="numeric" />

      <Text style={styles.label}>Savings</Text>
      <TextInput style={styles.input} value={savings} onChangeText={setSavings} keyboardType="numeric" />

      <View style={{ height: 12 }} />
      <Button title="Save" onPress={handleSave} />
      {message ? <Text style={{ marginTop: 8 }}>{message}</Text> : null}

      <View style={{ height: 20 }} />
      <Text style={{ fontWeight: '600' }}>Analysis</Text>
      <Text>{record.analysis_result ? JSON.stringify(record.analysis_result, null, 2) : 'No analysis'}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 18, fontWeight: '700', marginTop: 8 },
  label: { marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 8, borderRadius: 4 }
});
