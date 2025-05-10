// src/services/ApiService.js
import axios from "axios";
import { useAppStore } from "@/stores/app"; // Importa sua store global

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASEURL || "http://localhost:8000/v1",
});

// Interceptor para detectar respostas 401 (token expirado ou inválido)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Remove o token armazenado
      localStorage.removeItem("token");
      // Aciona o modal de login através da store global
      const appStore = useAppStore();
      appStore.triggerLoginModal();
    }
    return Promise.reject(error);
  }
);

const ApiService = {
  login: async (usuario, senha) => {
    const response = await api.post(
      "/users/login",
      {
        username: usuario,
        password: senha,
      },
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );
    return response.data;
  },

  getRoutines: async () => {
    const response = await api.get("/routines", {
      headers: {
        Authorization: `bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.data;
  },

  getClients: async () => {
    const response = await api.get("/clients", {
      headers: {
        Authorization: `bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.data;
  },

  getUsers: async () => {
    const response = await api.get("/users", {
      headers: {
        Authorization: `bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.data;
  },

  forgotPassword: async (email) => {
    const response = await api.post(`/users/forgot-password/${email}`);
    return response.data;
  },

  resetSenha: async (senha, token) => {
    const response = await api.post(`/users/reset-password?password=${senha}&token=${token}`);
    return response.data;
  },

  signup: async (userData) => {
    const response = await api.post("/users/signup", {
      name: userData.name,
      password: userData.password,
      email: userData.email,
      phone: userData.phone,
      cpf: userData.cpf,
    });
    return response.data;
  },

  salvarRotina: async (rotina) => {
    const response = await api.post(
      "/routines",
      {
        titulo: rotina.titulo,
        descricao: rotina.descricao,
        dt_vencimento: rotina.dt_vencimento,
        hr_estimativa: rotina.hr_estimativa,
      },
      {
        headers: {
          Authorization: `bearer ${localStorage.getItem("token")}`,
        },
      }
    );
    return response.data;
  },

  deleteRoutine : async (id) => {
    const response = await api.delete(`/routines/`, {
      params: {
        routine_id: id,
      },
      headers: {
        Authorization: `bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.data;
  },
};

export default ApiService;
