import axios from 'axios';

// Create an axios instance
const axiosClient = axios.create({
  baseURL: 'http://127.0.0.1:8000', // Your FastAPI backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosClient;
