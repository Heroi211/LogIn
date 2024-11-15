import axios from "axios";
import qs from "qs";

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASEURL || "http://localhost:8000/v1",
});

const ApiService = {
  login: async (usuario, senha) => {
    try {
      console.log("Tentando fazer login com:", usuario, senha);
      console.log("Base URL:", api.defaults.baseURL);
      const response = await api.post(
        "/users/login",
        qs.stringify({
          username: usuario,
          password: senha,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );
      console.log("Resposta do servidor:", response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao fazer login:", error);
      throw error;
    }
  },
};

export default ApiService;
