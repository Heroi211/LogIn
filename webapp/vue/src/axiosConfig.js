import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

instance.interceptors.request.use(
    config => {
      // Adicione tokens de autenticação ou outras configurações aqui
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    error => {
      return Promise.reject(error);
    }
  );
  
  instance.interceptors.response.use(
    response => response,
    error => {
      // Trate erros de resposta aqui
      return Promise.reject(error);
    }
  );
  
  export default instance;