import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createRecord } from '../services/api';

const emptyInvestment = { type: '', amount: '' };

export default function NewRecordScreen({ navigation }) {
  const [income, setIncome] = useState('');
  const [expenses, setExpenses] = useState('');
  const [savings, setSavings] = useState('');
  const [goals, setGoals] = useState('');
  const [investments, setInvestments] = useState([emptyInvestment]);
  const [message, setMessage] = useState('');

  const handleInvestmentChange = (index, field, value) => {
    const next = [...investments];
    next[index] = { ...next[index], [field]: value };
    setInvestments(next);
  };

  const addInvestment = () => {
    setInvestments([...investments, emptyInvestment]);
  };

  const handleSubmit = async () => {
    setMessage('');
    try {
      const token = await AsyncStorage.getItem('token');
      const payload = {
        income: parseFloat(income),
        expenses: parseFloat(expenses),
        savings: parseFloat(savings),
        investments: investments
          .filter((inv) => inv.type && inv.amount)
          .map((inv) => ({ type: inv.type, amount: parseFloat(inv.amount) })),
        goals: goals.split(',').map((goal) => goal.trim()).filter(Boolean),
      };

      await createRecord(token, payload);
      setMessage('Analysis saved successfully');
      navigation.goBack();
    } catch (e) {
      setMessage(e.message || 'Submission failed');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>New Financial Analysis</Text>
      <TextInput style={styles.input} placeholder="Income" keyboardType="numeric" value={income} onChangeText={setIncome} />
      <TextInput style={styles.input} placeholder="Expenses" keyboardType="numeric" value={expenses} onChangeText={setExpenses} />
      <TextInput style={styles.input} placeholder="Savings" keyboardType="numeric" value={savings} onChangeText={setSavings} />

      <Text style={styles.sectionTitle}>Investments</Text>
      {investments.map((investment, index) => (
        <View key={index} style={styles.investmentRow}>
          <TextInput
            style={[styles.input, styles.investmentInput]}
            placeholder="Type"
            value={investment.type}
            onChangeText={(text) => handleInvestmentChange(index, 'type', text)}
          />
          <TextInput
            style={[styles.input, styles.investmentInput]}
            placeholder="Amount"
            keyboardType="numeric"
            value={investment.amount}
            onChangeText={(text) => handleInvestmentChange(index, 'amount', text)}
          />
        </View>
      ))}
      <Button title="Add Investment" onPress={addInvestment} />

      <Text style={styles.sectionTitle}>Goals (comma separated)</Text>
      <TextInput style={styles.input} placeholder="e.g. buy house, retirement" value={goals} onChangeText={setGoals} />

      <View style={styles.buttonContainer}>
        <Button title="Submit" onPress={handleSubmit} />
      </View>
      {message ? <Text style={styles.message}>{message}</Text> : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, marginBottom: 16, fontWeight: '700' },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 12, borderRadius: 6 },
  sectionTitle: { fontSize: 16, fontWeight: '600', marginBottom: 8 },
  investmentRow: { flexDirection: 'row', justifyContent: 'space-between' },
  investmentInput: { flex: 1, marginRight: 8 },
  buttonContainer: { marginTop: 16 },
  message: { marginTop: 12, color: 'green' }
});
