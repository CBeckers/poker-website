const express = require('express');
const mysql = require('mysql');
const cors = require('cors');

const app = express();
const port = 5000;

app.use(cors());

const db = mysql.createConnection({
  host: 'your_mysql_host',  // e.g., 'localhost'
  user: 'your_mysql_user',
  password: 'your_mysql_password',
  database: 'your_mysql_database',
});

db.connect((err) => {
  if (err) {
    console.error('MySQL connection error:', err);
    return;
  }
  console.log('Connected to MySQL database');
});

app.get('/api/data', (req, res) => {
  const sql = 'SELECT * FROM your_table'; // Replace with your actual table name
  db.query(sql, (err, results) => {
    if (err) {
      console.error('Error fetching data:', err);
      res.status(500).json({ error: 'Failed to fetch data' });
      return;
    }
    res.json(results);
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
