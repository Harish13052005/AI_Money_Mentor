curl -X POST http://192.168.0.39:8000/analyze ^
  -H "Content-Type: application/json" ^
  -d "{
    \"income\": 5000,
    \"expenses\": 3000,
    \"savings\": 1000,
    \"investments\": [
      {\"type\": \"stocks\", \"amount\": 2000},
      {\"type\": \"mutual_funds\", \"amount\": 1000}
    ],
    \"goals\": [\"buy house\", \"retirement\", \"early education funding\"]
  }"