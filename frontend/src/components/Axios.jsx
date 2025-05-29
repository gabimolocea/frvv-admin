import axios from 'axios'

const baseUrl = 'http://localhost:8000';

const AxiosInstance = axios.create({
    baseURL: baseUrl,
    timeout: 5000,   
    headers: {
        'Content-Type': 'application/json',
    },
});

export default AxiosInstance;