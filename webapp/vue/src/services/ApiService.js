import axios from "axios";

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASEURL || "http://localhost:8000/v1",
});

const ApiService = {
  login: async (usuario, senha) => {
    const response = await api.post("/users/login", {
      username: usuario,
      password: senha,
    },
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    }
  );
    return response.data;
  },
};

export default ApiService;
