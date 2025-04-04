import React, { useState, useEffect } from 'react';
import './App.css';
import { io } from 'socket.io-client';

function App() {
  const [data, setData] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Create Socket Connection
    const newSocket = io('http://localhost:5000'); // Connect to backend
    setSocket(newSocket);

    // Fetch initial data
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/initial_data');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };

    fetchData(); // Get initial data
    return () => {
      newSocket.disconnect();
    }; // Clean up on unmount
  }, []);

  useEffect(() => {
    if (!socket) return;

    // Listen for data updates from the server
    socket.on('data_update', (newData) => {
      setData(newData); // Update the data state with the new data
    });

    return () => {
      socket.off('data_update'); // Clean up on unmount
    };
  }, [socket]);

  return (
    <div className="App">
      <h1>Live Data from MySQL (WebSockets)</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.sensor_name}</td>
              <td>{item.reading_value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
